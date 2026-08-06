"""Budgeted narcotics network interdiction (San Monique).

Given the capacity-constrained San Monique supply network, the question an
interdiction agency answers is *operational*: with a limited budget ``B`` of
transit legs it can sever in one operation, which legs cost the enemy the most
throughput?

This module implements the network-interdiction problem deterministically:

* :func:`greedy_interdiction` — the greedy (myopic) heuristic: at each step sever
  the remaining leg whose loss drops total throughput the most.
* :func:`exact_interdiction` — the optimal solution via exhaustive enumeration
  of sever leg-subsets (feasible for small budgets / graphs); a correctness
  upper bound on the greedy heuristic.
* :func:`efficiency_ranking` — the standalone "target list": each severable leg's
  independent throughput impact, ranked.

The model is the deterministic variant of R. K. Wood's classic *network
interdiction* problem on the capacity-flow abstraction (:mod:`~.supply_graph`):
flows follow max-flow, severing removes legs, and impact is measured as
throughput reduction from the un-interdicted baseline. Pure, deterministic,
stdlib-only; no ``infrastructure.*`` and no ``bond_api``.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Any, Iterable

from live_and_let_die.supply_graph import (
    Edge,
    Node,
    SAN_MONIQUE_DEMAND,
    SAN_MONIQUE_GRAPH,
    SUPER_SINK,
    SUPER_SOURCE,
    SupplyGraph,
)

__all__ = [
    "InterdictionPlan",
    "canonical_flow_graph",
    "efficiency_ranking",
    "exact_interdiction",
    "greedy_interdiction",
    "interdict_san_monique",
]

_EPS = 1e-9


@dataclass(frozen=True)
class InterdictionPlan:
    """The outcome of a budgeted interdiction run.

    ``severed`` lists the legs removed (as ``(source, target)`` tuples in the
    order they were chosen), ``gains`` the marginal throughput reduction each
    contributed, and ``reduction`` the cumulative total (which for the greedy
    plan equals the sum of its marginal gains).
    """

    budget: int
    severed: tuple[tuple[str, str], ...]
    reduction: float
    remaining_flow: float
    gains: tuple[float, ...]

    def cost_effectiveness(self) -> float:
        """Throughput reduction per *actually severed* leg (>0 iff any leg severed).

        Defined over ``len(self.severed)`` rather than the requested ``budget``:
        when the budget exceeds the severable set (or the operation collapses
        early), dividing by the requested budget would understate how much each
        severed leg achieved — the metric is per severed leg, not per allocated
        budget.
        """
        if not self.severed:
            return 0.0
        return float(self.reduction / len(self.severed))


def canonical_flow_graph() -> SupplyGraph:
    """The San Monique network with a super-source/super-sink for total flow.

    Production nodes are bounded by their crop capacity and markets by their
    demand ceilings; the real transit legs stay severable.
    """
    production = list(SAN_MONIQUE_GRAPH.nodes_of_kind("production"))
    transit = list(SAN_MONIQUE_GRAPH.nodes_of_kind("transit"))
    markets = list(SAN_MONIQUE_GRAPH.nodes_of_kind("market"))
    nodes: list[Node] = [
        Node(SUPER_SOURCE, "production", "Total supply"),
        Node(SUPER_SINK, "market", "Total demand"),
    ]
    nodes.extend(production)
    nodes.extend(transit)
    nodes.extend(markets)
    edges: list[Edge] = list(SAN_MONIQUE_GRAPH.edges())
    for prod in production:
        edges.append(Edge(SUPER_SOURCE, prod.id, 0.0, prod.capacity))
    for market in markets:
        edges.append(Edge(market.id, SUPER_SINK, 0.0, SAN_MONIQUE_DEMAND[market.id]))
    return SupplyGraph(nodes, edges)


def _without(graph: SupplyGraph, removed: frozenset[tuple[str, str]]) -> SupplyGraph:
    """A copy of ``graph`` with the given leg tuples removed."""
    remaining = [edge for edge in graph.edges() if edge.as_tuple() not in removed]
    nodes = [graph.node(node_id) for node_id in graph.node_ids()]
    return SupplyGraph(nodes, remaining)


def _sorted_severable(graph: SupplyGraph, severable: Iterable[tuple[str, str]]) -> tuple[tuple[str, str], ...]:
    """Normalise the severable leg set: dedupe, validate, sort deterministically."""
    seen: set[tuple[str, str]] = set()
    ordered: list[tuple[str, str]] = []
    for leg in severable:
        src, dst = leg
        if not graph.has_node(src) or not graph.has_node(dst):
            raise ValueError(f"severable leg {leg!r} references unknown graph nodes")
        if leg not in seen:
            seen.add(leg)
            ordered.append(leg)
    return tuple(sorted(ordered))


def efficiency_ranking(
    graph: SupplyGraph,
    source: str,
    sink: str,
    severable: Iterable[tuple[str, str]],
) -> tuple[tuple[tuple[str, str], float], ...]:
    """Independent throughput impact of severing each leg, ranked descending.

    Exactly the legs in ``severable`` are ranked — the caller decides the
    candidate set. :func:`interdict_san_monique` passes only the real transit
    legs, never the virtual super-source/super-sink edges (severing those would
    measure the capacity bound, not an operational strike). Ties break
    alphabetically by leg.
    """
    base = graph.max_flow(source, sink)
    legs = _sorted_severable(graph, severable)
    scored: list[tuple[tuple[str, str], float]] = []
    for leg in legs:
        drop = base - _without(graph, frozenset({leg})).max_flow(source, sink)
        scored.append((leg, drop))
    scored.sort(key=lambda item: (-item[1], item[0]))
    return tuple(scored)


def greedy_interdiction(
    graph: SupplyGraph,
    source: str,
    sink: str,
    budget: int,
    severable: Iterable[tuple[str, str]],
) -> InterdictionPlan:
    """Myopic greedy interdiction: sever the highest-marginal leg, repeat.

    Returns a plan whose ``reduction`` is the cumulative baseline-vs-final
    throughput drop. Deterministic tie-breaking: when two legs give the same
    marginal drop the alphabetically first (sorted) leg is chosen.
    """
    if budget < 0:
        raise ValueError(f"budget must be >= 0, got {budget}")
    legs = _sorted_severable(graph, severable)
    base = graph.max_flow(source, sink)
    removed: list[tuple[str, str]] = []
    cumulative: list[float] = []
    for _ in range(budget):
        best_leg: tuple[str, str] | None = None
        best_drop = -1.0
        removed_set = frozenset(removed)
        current = cumulative[-1] if cumulative else 0.0  # reduction already achieved
        for leg in legs:
            if leg in removed_set:
                continue
            # Total reduction (from the original base) if this leg were also
            # severed; its *marginal* contribution is the excess over ``current``.
            total_drop = base - _without(graph, removed_set | {leg}).max_flow(source, sink)
            if total_drop > best_drop:
                best_drop = total_drop
                best_leg = leg
        if best_leg is None:
            break  # nothing left to sever
        if best_drop - current <= _EPS:
            # Every remaining leg adds (at most) zero additional reduction —
            # the operation has already collapsed to its floor. Stop rather
            # than spending budget on strikes that achieve nothing.
            break
        removed.append(best_leg)
        cumulative.append(best_drop)
    # Convert cumulative drops into per-sever marginal gains (they sum to
    # the final reduction, which equals the last cumulative drop).
    gains: list[float] = []
    previous = 0.0
    for drop in cumulative:
        gains.append(round(drop - previous, 9))
        previous = drop
    reduction = cumulative[-1] if cumulative else 0.0
    return InterdictionPlan(
        budget=budget,
        severed=tuple(removed),
        reduction=reduction,
        remaining_flow=base - reduction,
        gains=tuple(gains),
    )


def exact_interdiction(
    graph: SupplyGraph,
    source: str,
    sink: str,
    budget: int,
    severable: Iterable[tuple[str, str]],
) -> InterdictionPlan:
    """Optimal interdiction by exhaustive enumeration of sever leg-subsets.

    Feasible for small graphs/budgets and serves as the correctness reference
    for the greedy heuristic (optimal reduction >= greedy reduction).
    """
    if budget < 0:
        raise ValueError(f"budget must be >= 0, got {budget}")
    legs = _sorted_severable(graph, severable)
    base = graph.max_flow(source, sink)
    if budget == 0 or not legs:
        return InterdictionPlan(budget, (), 0.0, base, ())
    best_combo: tuple[tuple[str, str], ...] | None = None
    best_reduction = -1.0
    for combo in itertools.combinations(legs, min(budget, len(legs))):
        remaining = _without(graph, frozenset(combo)).max_flow(source, sink)
        reduction = base - remaining
        if reduction > best_reduction + _EPS:
            best_reduction = reduction
            best_combo = combo
    if best_combo is None:  # pragma: no cover — unreachable: legs is non-empty here
        raise RuntimeError("exhaustive interdiction enumerated no candidate subset")
    return InterdictionPlan(
        budget=budget,
        severed=best_combo,
        reduction=best_reduction,
        remaining_flow=base - best_reduction,
        gains=(),
    )


def interdict_san_monique(budget: int = 3) -> dict[str, Any]:
    """Run the canonical San Monique interdiction study (deterministic).

    Combines the greedy plan, the exact optimum, and the efficiency target list
    into one report dict consumed by the mission and manuscript variables.
    """
    flow_graph = canonical_flow_graph()
    severable = tuple(edge.as_tuple() for edge in SAN_MONIQUE_GRAPH.edges())
    greedy = greedy_interdiction(flow_graph, SUPER_SOURCE, SUPER_SINK, budget, severable)
    exact = exact_interdiction(flow_graph, SUPER_SOURCE, SUPER_SINK, budget, severable)
    ranking = efficiency_ranking(flow_graph, SUPER_SOURCE, SUPER_SINK, severable)
    return {
        "budget": budget,
        "base_flow": flow_graph.max_flow(SUPER_SOURCE, SUPER_SINK),
        "greedy": {
            "severed": list(greedy.severed),
            "reduction": greedy.reduction,
            "remaining_flow": greedy.remaining_flow,
            "cost_effectiveness": greedy.cost_effectiveness(),
            "gains": list(greedy.gains),
        },
        "exact": {
            "severed": list(exact.severed),
            "reduction": exact.reduction,
            "remaining_flow": exact.remaining_flow,
        },
        "efficiency_ranking": [{"leg": list(leg), "reduction": drop} for leg, drop in ranking],
    }
