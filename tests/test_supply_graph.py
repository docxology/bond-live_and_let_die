"""Real-data tests for the San Monique supply-graph analytics module.

Every assertion is a genuine computation over the canonical graph (no mocks):
shortest paths, max-flow / min-cut, and critical-transit disruption.
"""

from __future__ import annotations

import pytest

from live_and_let_die.supply_graph import (
    Edge,
    Node,
    SAN_MONIQUE_GRAPH,
    analyze_san_monique,
    build_supply_graph,
)


def test_canonical_graph_shape() -> None:
    assert len(SAN_MONIQUE_GRAPH.node_ids()) == 7
    assert len(SAN_MONIQUE_GRAPH.edges()) == 10
    markets = {n.id for n in SAN_MONIQUE_GRAPH.nodes_of_kind("market")}
    assert markets == {"miami", "new_york"}
    assert SAN_MONIQUE_GRAPH.node("miami").kind == "market"
    assert SAN_MONIQUE_GRAPH.has_node("airfield")
    assert not SAN_MONIQUE_GRAPH.has_node("nope")
    assert SAN_MONIQUE_GRAPH.degree("airfield") >= 1


def test_node_guardrails() -> None:
    with pytest.raises(ValueError):
        Node("", "production", "x")
    with pytest.raises(ValueError):
        Node("a", "bogus", "x")
    with pytest.raises(ValueError):
        Node("a", "production", " ")
    with pytest.raises(ValueError):
        Node("a", "production", "x", capacity=-1.0)


def test_edge_guardrails() -> None:
    with pytest.raises(ValueError):
        Edge("", "b", 1.0, 1.0)
    with pytest.raises(ValueError):
        Edge("a", "", 1.0, 1.0)
    with pytest.raises(ValueError):
        Edge("a", "b", -1.0, 1.0)
    with pytest.raises(ValueError):
        Edge("a", "b", 1.0, -1.0)


def test_build_validation() -> None:
    with pytest.raises(ValueError):
        build_supply_graph([Node("a", "production", "A"), Node("a", "market", "A2")], [])
    with pytest.raises(ValueError):
        build_supply_graph(
            [Node("a", "production", "A"), Node("b", "market", "B")],
            [Edge("a", "c", 1.0, 1.0)],  # unknown target
        )
    with pytest.raises(ValueError):
        build_supply_graph(
            [Node("a", "production", "A"), Node("b", "market", "B")],
            [Edge("c", "b", 1.0, 1.0)],  # unknown source
        )


def test_unknown_node_key() -> None:
    with pytest.raises(KeyError):
        SAN_MONIQUE_GRAPH.node("missing")


def test_shortest_path_known_values() -> None:
    cost, path = SAN_MONIQUE_GRAPH.shortest_path("poppy_fields", "miami")
    assert cost == 13.0
    assert path == ("poppy_fields", "airfield", "miami")
    cost, path = SAN_MONIQUE_GRAPH.shortest_path("poppy_fields", "new_york")
    assert cost == 18.0
    assert path == ("poppy_fields", "field_works", "harbor", "new_york")


def test_shortest_path_trivial_and_errors() -> None:
    assert SAN_MONIQUE_GRAPH.shortest_path("miami", "miami") == (0.0, ("miami",))
    with pytest.raises(ValueError):
        SAN_MONIQUE_GRAPH.shortest_path("bogus", "miami")
    with pytest.raises(ValueError):
        SAN_MONIQUE_GRAPH.shortest_path("miami", "bogus")

    # The market nodes have no outgoing edges: new_york cannot reach miami.
    with pytest.raises(ValueError):
        SAN_MONIQUE_GRAPH.shortest_path("miami", "new_york")


def test_neighbors_sorted() -> None:
    neighbours = SAN_MONIQUE_GRAPH.neighbors("airfield")
    targets = [t for t, _ in neighbours]
    assert targets == sorted(targets)
    assert "miami" in targets


def test_max_flow_and_min_cut() -> None:
    # Total throughput is capped by destination demand (120 + 100).
    assert SAN_MONIQUE_GRAPH.max_flow("poppy_fields", "miami") > 0
    cut_value, cut_edges = SAN_MONIQUE_GRAPH.min_cut("poppy_fields", "miami")
    assert cut_value == pytest.approx(SAN_MONIQUE_GRAPH.max_flow("poppy_fields", "miami"))


def test_disruption_bounds() -> None:
    base = SAN_MONIQUE_GRAPH.max_flow("poppy_fields", "miami")
    edge = Edge("airfield", "miami", 7.0, 90.0)
    drop = SAN_MONIQUE_GRAPH.disruption("poppy_fields", "miami", edge)
    assert 0.0 <= drop <= base


def test_node_disruption_and_unknown() -> None:
    drop = SAN_MONIQUE_GRAPH.node_disruption("poppy_fields", "miami", "airfield")
    assert drop > 0
    with pytest.raises(ValueError):
        SAN_MONIQUE_GRAPH.node_disruption("poppy_fields", "miami", "ghost")


def test_critical_node_is_airfield() -> None:
    assert SAN_MONIQUE_GRAPH.critical_node("poppy_fields", "miami") == "airfield"


def test_analyze_san_monique_deterministic() -> None:
    first = analyze_san_monique()
    second = analyze_san_monique()
    assert first == second
    assert first["critical_transit_node"] == "airfield"
    assert first["disruption_units"] == 150.0
    assert first["max_flow_total"] == 220.0
    assert first["min_cut_value"] == 220.0
    assert first["markets"] == ["miami", "new_york"]
    assert first["nodes"] == 7
    assert first["edges"] == 10
    assert first["shortest_path_miami"] == (13.0, ["poppy_fields", "airfield", "miami"])
