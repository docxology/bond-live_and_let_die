"""San Monique narcotics supply-graph analytics (production -> transit -> market).

This module models the narcotics supply chain of the film's villain (Kananga's
San Monique operation) as a directed, weighted, capacity-constrained graph and
answers the operational questions a disruptor cares about:

* the cheapest path from a production source to each destination market
  (:func:`SupplyGraph.shortest_path` — Dijkstra);
* the maximum volume the network can move to market (:func:`SupplyGraph.max_flow`
  — Edmonds-Karp), and the *minimum cut* that bounds it
  (:func:`SupplyGraph.min_cut`); and
* which single transit asset is the operative bottleneck — severing it costs
  the most throughput (:func:`SupplyGraph.critical_node` /
  :func:`SupplyGraph.disruption`).

Pure, deterministic, stdlib-only (``heapq`` + ``collections.deque``). No
``infrastructure.*`` and no ``bond_api`` imports — the film's mission adapter
lays the protocol on top of this core.
"""

from __future__ import annotations

import heapq
from collections import deque
from dataclasses import dataclass
from typing import Any, Iterable

__all__ = [
    "Edge",
    "Node",
    "SAN_MONIQUE_GRAPH",
    "SupplyGraph",
    "analyze_san_monique",
    "build_supply_graph",
]

PRODUCTION = "production"
TRANSIT = "transit"
MARKET = "market"

#: Well-formed kinds for graph nodes; used for validation and downstream
#: classification (e.g. a disruption analysis only probes transit nodes).
KINDS = (PRODUCTION, TRANSIT, MARKET)

#: An unbounded edge / node capacity. Real transit routes are treated as
#: effectively uncapped unless a number is supplied.
INF = float("inf")


@dataclass(frozen=True)
class Node:
    """A vertex in the supply graph: a production site, transit asset, or market."""

    id: str
    kind: str
    name: str
    capacity: float = INF

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Node.id must be a non-empty string")
        if self.kind not in KINDS:
            raise ValueError(f"Node.kind must be one of {KINDS}, got {self.kind!r}")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Node.name must be a non-empty string")
        if self.capacity < 0:
            raise ValueError(f"Node.capacity must be >= 0, got {self.capacity}")


@dataclass(frozen=True)
class Edge:
    """A directed supply leg: ``source -> target`` with a unit cost and capacity."""

    source: str
    target: str
    weight: float
    capacity: float

    def __post_init__(self) -> None:
        if not isinstance(self.source, str) or not self.source:
            raise ValueError("Edge.source must be a non-empty string")
        if not isinstance(self.target, str) or not self.target:
            raise ValueError("Edge.target must be a non-empty string")
        if self.weight < 0:
            raise ValueError(f"Edge.weight must be >= 0, got {self.weight}")
        if self.capacity < 0:
            raise ValueError(f"Edge.capacity must be >= 0, got {self.capacity}")

    def as_tuple(self) -> tuple[str, str]:
        """The edge as a (source, target) tuple — hashable short form."""
        return (self.source, self.target)


@dataclass(frozen=True)
class _Route:
    """Internal result of a shortest-path search: cost and ordered node path."""

    cost: float
    path: tuple[str, ...]


class SupplyGraph:
    """A directed, weighted, capacity-constrained supply graph.

    The adjacency index is built once at construction so repeated queries
    (flow, cuts, disruptions) share the same in-memory structure.
    """

    def __init__(self, nodes: Iterable[Node], edges: Iterable[Edge]) -> None:
        self._nodes: dict[str, Node] = {}
        self._edges: list[Edge] = []
        self._adj: dict[str, list[Edge]] = {}
        for node in nodes:
            if node.id in self._nodes:
                raise ValueError(f"duplicate node id {node.id!r}")
            self._nodes[node.id] = node
            self._adj[node.id] = []
        for edge in edges:
            if edge.source not in self._nodes:
                raise ValueError(f"edge references unknown source {edge.source!r}")
            if edge.target not in self._nodes:
                raise ValueError(f"edge references unknown target {edge.target!r}")
            self._edges.append(edge)
            self._adj[edge.source].append(edge)
        self._validate_determinism()

    def _validate_determinism(self) -> None:
        """Keep every traversal stable: adjacency lists sorted by target id."""
        for node_id in self._adj:
            self._adj[node_id].sort(key=lambda edge: edge.target)

    # -- structural queries -------------------------------------------------
    def node_ids(self) -> tuple[str, ...]:
        return tuple(self._nodes)

    def nodes_of_kind(self, kind: str) -> tuple[Node, ...]:
        return tuple(n for n in self._nodes.values() if n.kind == kind)

    def node(self, node_id: str) -> Node:
        if node_id not in self._nodes:
            raise KeyError(f"unknown node {node_id!r}")
        return self._nodes[node_id]

    def edges(self) -> tuple[Edge, ...]:
        return tuple(self._edges)

    def has_node(self, node_id: str) -> bool:
        return node_id in self._nodes

    def degree(self, node_id: str) -> int:
        return len(self._adj.get(node_id, []))

    # -- path finding -------------------------------------------------------
    def neighbors(self, node_id: str) -> tuple[tuple[str, float], ...]:
        """Outgoing neighbours as (target, weight), sorted by target."""
        return tuple((edge.target, edge.weight) for edge in self._adj.get(node_id, []))

    def shortest_path(self, source: str, target: str) -> tuple[float, tuple[str, ...]]:
        """Dijkstra: cheapest cost and ordered node path from ``source`` to ``target``.

        Tie-breaking is deterministic (``(cost, node_id)`` heap keys); an
        unreachable target raises ``ValueError``.
        """
        self._require_node(source, "source")
        self._require_node(target, "target")
        if source == target:
            return 0.0, (source,)
        dist: dict[str, float] = {source: 0.0}
        prev: dict[str, str] = {}
        heap: list[tuple[float, str, int, str]] = []
        tick = 0
        heapq.heappush(heap, (0.0, source, tick, source))
        while heap:
            cost, node_id, _seq, first = heapq.heappop(heap)
            if node_id != first:
                continue
            if cost > dist.get(node_id, INF):
                continue
            if node_id == target:
                return self._reconstruct(source, target, prev, cost)
            for edge in self._adj[node_id]:
                nxt = edge.target
                new_cost = cost + edge.weight
                if new_cost < dist.get(nxt, INF):
                    dist[nxt] = new_cost
                    prev[nxt] = node_id
                    tick += 1
                    heapq.heappush(heap, (new_cost, nxt, tick, nxt))
        raise ValueError(f"no path from {source!r} to {target!r}")

    def _reconstruct(
        self, source: str, target: str, prev: dict[str, str], cost: float
    ) -> tuple[float, tuple[str, ...]]:
        node_id = target
        path: list[str] = [node_id]
        while node_id != source:
            node_id = prev[node_id]
            path.append(node_id)
        path.reverse()
        return cost, tuple(path)

    # -- flow / cut ---------------------------------------------------------
    def max_flow(self, source: str, sink: str) -> float:
        """Maximum flow from ``source`` to ``sink`` via Edmonds-Karp (BFS)."""
        self._require_node(source, "source")
        self._require_node(sink, "sink")
        residual = self._fresh_residual()
        self._edmonds_karp(residual, source, sink)
        flow = 0.0
        for source_node, target_node in residual:
            if source_node != source:
                continue
            original = self._original_capacity(source_node, target_node)
            flow += original - residual[(source_node, target_node)]
        return flow

    def min_cut(self, source: str, sink: str) -> tuple[float, tuple[Edge, ...]]:
        """Minimum cut: the max-flow value and the forward edges crossing it.

        After a max flow, the reachable set from ``source`` in the residual
        graph defines a cut; the original-graph edges leaving that set are the
        min-cut edges whose summed capacity equals the flow.
        """
        self._require_node(source, "source")
        self._require_node(sink, "sink")
        residual = self._fresh_residual()
        self._edmonds_karp(residual, source, sink)
        reachable = self._reachable(residual, source)
        cut_edges = tuple(edge for edge in self._edges if edge.source in reachable and edge.target not in reachable)
        cut_value = sum(edge.capacity for edge in cut_edges)
        return cut_value, cut_edges

    def _fresh_residual(self) -> dict[tuple[str, str], float]:
        """Residual network seeded from edge capacities (both directions)."""
        residual: dict[tuple[str, str], float] = {}
        for edge in self._edges:
            residual[(edge.source, edge.target)] = residual.get((edge.source, edge.target), 0.0) + edge.capacity
            residual.setdefault((edge.target, edge.source), 0.0)
        return residual

    def _original_capacity(self, source: str, target: str) -> float:
        """Sum of edge capacities for a given (source, target) key."""
        return sum(edge.capacity for edge in self._edges if edge.as_tuple() == (source, target))

    def _edmonds_karp(self, residual: dict[tuple[str, str], float], source: str, sink: str) -> None:
        while True:
            parent = self._bfs_path(residual, source, sink)
            if parent is None:
                return
            bottleneck = self._bottleneck(residual, parent, source, sink)
            if bottleneck <= 0:
                return
            step = sink
            while step != source:
                edge_key = parent[step]
                assert edge_key is not None
                residual[edge_key] -= bottleneck
                residual[(edge_key[1], edge_key[0])] = residual.get((edge_key[1], edge_key[0]), 0.0) + bottleneck
                step = edge_key[0]

    def _bfs_path(
        self, residual: dict[tuple[str, str], float], source: str, sink: str
    ) -> dict[str, tuple[str, str] | None] | None:
        parent: dict[str, tuple[str, str] | None] = {source: None}
        queue: deque[str] = deque([source])
        while queue:
            u = queue.popleft()
            for v in self._nodes:
                if v in parent:
                    continue
                key = (u, v)
                if residual.get(key, 0.0) > 0:
                    parent[v] = (u, v)
                    if v == sink:
                        return parent
                    queue.append(v)
        return None

    def _bottleneck(
        self,
        residual: dict[tuple[str, str], float],
        parent: dict[str, tuple[str, str] | None],
        source: str,
        sink: str,
    ) -> float:
        bottleneck = INF
        step = sink
        while step != source:
            edge_key = parent[step]
            assert edge_key is not None
            bottleneck = min(bottleneck, residual[edge_key])
            step = edge_key[0]
        return bottleneck

    def _reachable(self, residual: dict[tuple[str, str], float], source: str) -> set[str]:
        seen: set[str] = set()
        queue: deque[str] = deque([source])
        seen.add(source)
        while queue:
            u = queue.popleft()
            for v in self._nodes:
                if v in seen:
                    continue
                if residual.get((u, v), 0.0) > 0:
                    seen.add(v)
                    queue.append(v)
        return seen

    # -- disruption analysis -------------------------------------------------
    def disruption(self, source: str, sink: str, edge: Edge) -> float:
        """Throughput lost if ``edge`` were severed: max_flow before minus after."""
        self._require_node(source, "source")
        self._require_node(sink, "sink")
        remaining = tuple(e for e in self._edges if e.as_tuple() != edge.as_tuple())
        severed = SupplyGraph(self._nodes.values(), remaining)
        return self.max_flow(source, sink) - severed.max_flow(source, sink)

    def node_disruption(self, source: str, sink: str, node_id: str) -> float:
        """Throughput lost if a node (and all its incident legs) were neutralized."""
        self._require_node(source, "source")
        self._require_node(sink, "sink")
        self._require_node(node_id, "node_id")
        remaining = tuple(e for e in self._edges if e.source != node_id and e.target != node_id)
        severed = SupplyGraph(self._nodes.values(), remaining)
        return self.max_flow(source, sink) - severed.max_flow(source, sink)

    def critical_node(self, source: str, sink: str) -> str:
        """The transit node whose removal costs the most throughput (deterministic).

        Only ``transit`` nodes are probed: production and market nodes are not
        severable assets. Ties resolve to the alphabetically first node id.
        """
        self._require_node(source, "source")
        self._require_node(sink, "sink")
        base = self.max_flow(source, sink)
        best_drop = -INF
        best_node = ""
        transit = sorted(node.id for node in self.nodes_of_kind(TRANSIT))
        for node_id in transit:
            remaining = tuple(e for e in self._edges if e.source != node_id and e.target != node_id)
            severed = SupplyGraph(self._nodes.values(), remaining)
            drop = base - severed.max_flow(source, sink)
            if drop > best_drop + 1e-9:
                best_drop = drop
                best_node = node_id
        return best_node

    def _require_node(self, node_id: str, role: str) -> None:
        if node_id not in self._nodes:
            raise ValueError(f"unknown {role} node {node_id!r}")


# ---------------------------------------------------------------------------
# Canonical San Monique dataset (deterministic; the film's real input).
# ---------------------------------------------------------------------------
_SAN_MONIQUE_NODES: tuple[Node, ...] = (
    Node("poppy_fields", PRODUCTION, "Interior poppy fields", capacity=150.0),
    Node("field_works", PRODUCTION, "Field processing works", capacity=120.0),
    Node("airfield", TRANSIT, "San Monique airfield"),
    Node("harbor", TRANSIT, "Port of San Monique"),
    Node("cove", TRANSIT, "Smuggler's cove jetties"),
    Node("miami", MARKET, "Miami distribution hub"),
    Node("new_york", MARKET, "NYC distribution hub"),
)

_SAN_MONIQUE_EDGES: tuple[Edge, ...] = (
    Edge("poppy_fields", "airfield", 6.0, 100.0),
    Edge("poppy_fields", "field_works", 3.0, 120.0),
    Edge("field_works", "airfield", 4.0, 90.0),
    Edge("field_works", "harbor", 5.0, 110.0),
    Edge("airfield", "cove", 4.0, 80.0),
    Edge("airfield", "miami", 7.0, 90.0),
    Edge("harbor", "miami", 8.0, 70.0),
    Edge("cove", "miami", 6.0, 80.0),
    Edge("harbor", "new_york", 10.0, 60.0),
    Edge("cove", "new_york", 9.0, 50.0),
)

#: Build the canonical graph once; reuse it across analysis, figures, and the
#: mission adapter so all downstream numbers share one source of truth.
SAN_MONIQUE_GRAPH = SupplyGraph(_SAN_MONIQUE_NODES, _SAN_MONIQUE_EDGES)

#: Super-source injected before the single production source for total-flow
#: queries, and a super-sink after the destination markets.
SUPER_SOURCE = "SUPPLY"
SUPER_SINK = "DEMAND"

#: Market demand ceilings (units demanded per reporting period) — the capacity
#: of each market -> DEMAND edge in flow analysis.
SAN_MONIQUE_DEMAND: dict[str, float] = {"miami": 120.0, "new_york": 100.0}


def build_supply_graph(nodes: Iterable[Node], edges: Iterable[Edge]) -> SupplyGraph:
    """Construct a :class:`SupplyGraph` from node/edge iterables (validated)."""
    return SupplyGraph(nodes, edges)


def _flow_graph() -> SupplyGraph:
    """The San Monique graph with a super-source/super-sink for total throughput."""
    nodes = list(node for node in _SAN_MONIQUE_NODES if node.kind != MARKET)
    market_nodes = [node for node in _SAN_MONIQUE_NODES if node.kind == MARKET]
    super_nodes = [
        Node(SUPER_SOURCE, PRODUCTION, "Total supply"),
        Node(SUPER_SINK, MARKET, "Total demand"),
    ]
    all_nodes = super_nodes + nodes + market_nodes
    edges = list(_SAN_MONIQUE_EDGES)
    for node in _SAN_MONIQUE_NODES:
        if node.kind == PRODUCTION:
            edges.append(Edge(SUPER_SOURCE, node.id, 0.0, node.capacity))
    for node in market_nodes:
        edges.append(Edge(node.id, SUPER_SINK, 0.0, SAN_MONIQUE_DEMAND.get(node.id, INF)))
    return SupplyGraph(all_nodes, edges)


def analyze_san_monique() -> dict[str, Any]:
    """Run the full deterministic San Monique supply analysis.

    Returns a flat dict with path, flow, cut, and disruption findings — the
    exact payload the mission ``execute`` step reports and the manuscript
    variables are computed from.
    """
    graph = SAN_MONIQUE_GRAPH
    flow_graph = _flow_graph()
    production = "poppy_fields"
    shortest_miami = graph.shortest_path(production, "miami")
    shortest_new_york = graph.shortest_path(production, "new_york")
    total_flow = flow_graph.max_flow(SUPER_SOURCE, SUPER_SINK)
    bottleneck_value, cut_edges = flow_graph.min_cut(SUPER_SOURCE, SUPER_SINK)
    critical = graph.critical_node(production, "miami")
    disruption = graph.node_disruption(production, "miami", critical)
    markets = sorted(n.id for n in graph.nodes_of_kind(MARKET))
    return {
        "nodes": len(graph.node_ids()),
        "edges": len(graph.edges()),
        "markets": markets,
        "shortest_path_miami": (shortest_miami[0], list(shortest_miami[1])),
        "shortest_path_new_york": (shortest_new_york[0], list(shortest_new_york[1])),
        "max_flow_total": total_flow,
        "min_cut_value": bottleneck_value,
        "min_cut_edges": sorted(e.as_tuple() for e in cut_edges),
        "critical_transit_node": critical,
        "disruption_units": disruption,
    }
