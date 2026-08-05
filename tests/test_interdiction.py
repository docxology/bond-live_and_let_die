"""Real-data tests for the budgeted narcotics network interdiction module."""

from __future__ import annotations

import pytest
from live_and_let_die.interdiction import (
    InterdictionPlan,
    canonical_flow_graph,
    efficiency_ranking,
    exact_interdiction,
    greedy_interdiction,
    interdict_san_monique,
)
from live_and_let_die.supply_graph import (
    SAN_MONIQUE_GRAPH,
    SUPER_SINK,
    SUPER_SOURCE,
    Edge,
    Node,
    SupplyGraph,
)

SEVERABLE = tuple(edge.as_tuple() for edge in SAN_MONIQUE_GRAPH.edges())


def test_canonical_flow_graph_shape() -> None:
    graph = canonical_flow_graph()
    assert graph.has_node(SUPER_SOURCE)
    assert graph.has_node(SUPER_SINK)
    assert graph.max_flow(SUPER_SOURCE, SUPER_SINK) == 220.0


def test_cost_effectiveness_zero_budget() -> None:
    plan = InterdictionPlan(budget=0, severed=(), reduction=0.0, remaining_flow=220.0, gains=())
    assert plan.cost_effectiveness() == 0.0


def test_greedy_interdiction_budget_zero() -> None:
    graph = canonical_flow_graph()
    plan = greedy_interdiction(graph, SUPER_SOURCE, SUPER_SINK, 0, SEVERABLE)
    assert plan.severed == () and plan.reduction == 0.0 and plan.remaining_flow == 220.0


def test_greedy_negative_budget() -> None:
    graph = canonical_flow_graph()
    with pytest.raises(ValueError):
        greedy_interdiction(graph, SUPER_SOURCE, SUPER_SINK, -1, SEVERABLE)


def test_exact_negative_budget() -> None:
    graph = canonical_flow_graph()
    with pytest.raises(ValueError):
        exact_interdiction(graph, SUPER_SOURCE, SUPER_SINK, -1, SEVERABLE)


def test_greedy_severs_unknown_node_raises() -> None:
    graph = canonical_flow_graph()
    with pytest.raises(ValueError):
        greedy_interdiction(graph, SUPER_SOURCE, SUPER_SINK, 1, [("ghost", "airfield")])


def test_greedy_three_leg_strike_collapses_operation() -> None:
    plan = greedy_interdiction(canonical_flow_graph(), SUPER_SOURCE, SUPER_SINK, 3, SEVERABLE)
    assert plan.reduction == pytest.approx(220.0)
    assert plan.remaining_flow == pytest.approx(0.0)
    assert len(plan.severed) == 3
    assert sum(plan.gains) == pytest.approx(plan.reduction)
    assert plan.cost_effectiveness() == pytest.approx(220.0 / 3.0)


def test_exact_is_optimal_upper_bound() -> None:
    graph = canonical_flow_graph()
    for budget in (1, 2, 3):
        greedy = greedy_interdiction(graph, SUPER_SOURCE, SUPER_SINK, budget, SEVERABLE)
        exact = exact_interdiction(graph, SUPER_SOURCE, SUPER_SINK, budget, SEVERABLE)
        assert exact.reduction >= greedy.reduction - 1e-9
        assert exact.reduction <= 220.0 + 1e-9


def test_exact_budget_zero() -> None:
    graph = canonical_flow_graph()
    plan = exact_interdiction(graph, SUPER_SOURCE, SUPER_SINK, 0, SEVERABLE)
    assert plan.reduction == 0.0 and plan.severed == ()


def test_reduction_is_monotonic_in_budget() -> None:
    graph = canonical_flow_graph()
    reductions = [greedy_interdiction(graph, SUPER_SOURCE, SUPER_SINK, b, SEVERABLE).reduction for b in range(0, 5)]
    assert reductions == sorted(reductions)


def test_efficiency_ranking_sorted_and_valid() -> None:
    graph = canonical_flow_graph()
    ranking = efficiency_ranking(graph, SUPER_SOURCE, SUPER_SINK, SEVERABLE)
    drops = [drop for _, drop in ranking]
    assert drops == sorted(drops, reverse=True)
    assert ranking[0][0] == ("field_works", "harbor")
    assert ranking[0][1] == pytest.approx(50.0)
    # No virtual source/sink legs appear.
    assert all("SUPPLY" not in leg and "DEMAND" not in leg for leg, _ in ranking)


def test_interdict_san_monique_report() -> None:
    report = interdict_san_monique(budget=3)
    assert report["budget"] == 3
    assert report["base_flow"] == 220.0
    assert report["greedy"]["reduction"] == pytest.approx(220.0)
    assert report["exact"]["reduction"] == pytest.approx(220.0)
    assert report["efficiency_ranking"][0]["leg"] == ["field_works", "harbor"]
    # Deterministic across calls.
    assert report == interdict_san_monique(budget=3)


def test_sever_edges_rebuilds_valid_graph() -> None:
    # Building a small custom graph and severing has no side effects on the
    # canonical graph (sever rebuild is pure).
    nodes = [Node("s", "production", "src"), Node("a", "transit", "mid"), Node("m", "market", "dst")]
    edges = [Edge("s", "a", 1.0, 10.0), Edge("a", "m", 1.0, 10.0)]
    graph = SupplyGraph(nodes, edges)
    assert graph.max_flow("s", "m") == 10.0
    plan = greedy_interdiction(graph, "s", "m", 1, [("s", "a")])
    assert plan.reduction == pytest.approx(10.0)
    # Canonical graph unaffected: pinned against the independently-known value,
    # not against a second call to itself (which would pass even if severing
    # had mutated the shared graph).
    assert SAN_MONIQUE_GRAPH.max_flow("poppy_fields", "miami") == pytest.approx(220.0)
    assert len(SAN_MONIQUE_GRAPH.edges()) == 10
