"""Real-data tests for the market-flow (farm-gate to street) economics module."""

from __future__ import annotations

import pytest
from live_and_let_die.market_flow import (
    EDGE_ECONOMICS,
    FARM_GATE_PRICE,
    RETAIL_DILUTION,
    RETAIL_MARKUP,
    market_flow_report,
    node_prices,
)
from live_and_let_die.supply_graph import SAN_MONIQUE_GRAPH


def test_all_canonical_edges_have_economics() -> None:
    canonical_legs = {edge.as_tuple() for edge in SAN_MONIQUE_GRAPH.edges()}
    assert set(EDGE_ECONOMICS) == canonical_legs


def test_economic_constants_sane() -> None:
    assert FARM_GATE_PRICE == 300.0
    assert RETAIL_MARKUP > 1.0
    assert 0.0 < RETAIL_DILUTION < 1.0


def test_node_prices_propagate_from_farm_gate() -> None:
    prices = node_prices()
    assert prices["poppy_fields"] == (300.0, 1.0)
    # Cheapest path poppy->airfield: markup 2.0, dilution 0.95.
    assert prices["airfield"][0] == pytest.approx(600.0)
    assert prices["airfield"][1] == pytest.approx(0.95)
    # Prices are monotone non-decreasing away from the source.
    assert prices["miami"][0] > prices["airfield"][0]


def test_market_flow_report_values() -> None:
    report = market_flow_report()
    miami = report["markets"]["miami"]
    nyc = report["markets"]["new_york"]
    assert miami["street_price"] == pytest.approx(14400.0)
    assert miami["street_purity"] == pytest.approx(0.57)
    assert miami["revenue"] == pytest.approx(1_728_000.0)
    assert nyc["street_price"] == pytest.approx(21600.0)
    assert nyc["street_purity"] == pytest.approx(0.486864)
    assert nyc["revenue"] == pytest.approx(2_160_000.0)


def test_producer_share_and_spread_are_exact_reciprocals() -> None:
    """An identity of the model, not a claim about the world."""
    report = market_flow_report()
    assert report["producer_share"] * report["spread_ratio"] == pytest.approx(1.0)
    assert report["producer_share"] == pytest.approx(report["farm_gate_price"] / report["avg_street_price"])
    assert report["total_revenue"] == pytest.approx(3_888_000.0)


def test_producer_share_is_driven_by_the_assumed_markups() -> None:
    """The small producer share is an output of chosen parameters, not a law.

    The gate this replaces asserted ``0.01 < producer_share < 0.05`` and called
    it "the classic finding" — a band that could not fail without editing the
    constants it measured, and that bound nothing external. This test instead
    re-runs the identical model on substituted parameter sets and demands the
    share move with them, which is the property the model can actually support.
    """
    canonical = market_flow_report()["producer_share"]
    assert canonical == pytest.approx(0.017, abs=5e-4)

    # Neutral transit economics: no leg marks anything up. The producer share
    # must then be exactly the reciprocal of the retail markup — far outside the
    # "1-5%" band the old gate treated as an empirical finding.
    neutral = {leg: (1.0, 1.0) for leg in EDGE_ECONOMICS}
    neutral_share = market_flow_report(economics=neutral)["producer_share"]
    assert neutral_share == pytest.approx(1.0 / RETAIL_MARKUP)
    assert neutral_share > 0.05

    # Doubling every leg markup drives the share down by exactly the path
    # structure: Miami's cheapest path is two legs (x4), New York's is three
    # (x8), so the demand-weighted share lands strictly between canonical/8 and
    # canonical/4. This pins the propagation, not just the direction.
    base = market_flow_report()
    doubled = {leg: (markup * 2.0, dilution) for leg, (markup, dilution) in EDGE_ECONOMICS.items()}
    doubled_report = market_flow_report(economics=doubled)
    assert doubled_report["markets"]["miami"]["street_price"] == pytest.approx(
        4.0 * base["markets"]["miami"]["street_price"]
    )
    assert doubled_report["markets"]["new_york"]["street_price"] == pytest.approx(
        8.0 * base["markets"]["new_york"]["street_price"]
    )
    assert canonical / 8.0 < doubled_report["producer_share"] < canonical / 4.0

    # The farm-gate price cancels out of the share but not out of revenue.
    assert market_flow_report(farm_gate_price=600.0)["producer_share"] == pytest.approx(canonical)
    assert market_flow_report(farm_gate_price=600.0)["total_revenue"] == pytest.approx(
        2 * market_flow_report()["total_revenue"]
    )


def test_injected_parameters_reach_every_consumer() -> None:
    """Guards the injection points themselves: an ignored argument fails here."""
    prices = node_prices(farm_gate_price=1000.0)
    assert prices["poppy_fields"] == (1000.0, 1.0)
    assert prices["airfield"][0] == pytest.approx(2000.0)  # markup 2.0

    halved = market_flow_report(retail_markup=RETAIL_MARKUP / 2.0)
    assert halved["markets"]["miami"]["street_price"] == pytest.approx(7200.0)
    cleaner = market_flow_report(retail_dilution=1.0)
    assert cleaner["markets"]["miami"]["street_purity"] == pytest.approx(0.76)


def test_missing_leg_economics_is_rejected() -> None:
    """The ValueError path in ``_path_price`` — previously uncovered."""
    incomplete = {leg: value for leg, value in EDGE_ECONOMICS.items() if leg != ("airfield", "miami")}
    with pytest.raises(ValueError, match="no economics defined for leg"):
        market_flow_report(economics=incomplete)


def test_market_flow_deterministic() -> None:
    assert market_flow_report() == market_flow_report()
    assert node_prices() == node_prices()


def test_avg_street_demand_weighted() -> None:
    report = market_flow_report()
    # Demand (120, 100) weights the average street price.
    expected = (120 * 14400.0 + 100 * 21600.0) / 220.0
    assert report["avg_street_price"] == pytest.approx(expected)
