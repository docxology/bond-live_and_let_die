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


def test_producer_share_is_small() -> None:
    report = market_flow_report()
    # The classic finding: the farm-gate producer captures only ~1-2% of the
    # street value of the narcotics.
    assert 0.01 < report["producer_share"] < 0.05
    assert report["spread_ratio"] > 20.0
    assert report["total_revenue"] == pytest.approx(3_888_000.0)


def test_market_flow_deterministic() -> None:
    assert market_flow_report() == market_flow_report()
    assert node_prices() == node_prices()


def test_avg_street_demand_weighted() -> None:
    report = market_flow_report()
    # Demand (120, 100) weights the average street price.
    expected = (120 * 14400.0 + 100 * 21600.0) / 220.0
    assert report["avg_street_price"] == pytest.approx(expected)
