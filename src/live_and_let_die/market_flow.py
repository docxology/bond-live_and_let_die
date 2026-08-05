"""Narcotics market-flow economics (San Monique: farm gate to street).

The money side of Kananga's operation: the same supply legs that carry volume
also mark prices up and dilute purity from the farm-gate crop to the street
product. This module models the canonical unit economics deterministically:

* :data:`EDGE_ECONOMICS` — per-leg price markup multiplier and purity dilution
  factor;
* :func:`node_prices` — propagate price/purity from the farm gate along each
  market's cheapest path (lowest-cost channel sets the price, by arbitrage);
* :func:`market_flow_report` — per-market street price/purity, demand-weighted
  average, the producer share (farm gate as a fraction of street price), the
  price-spread ratio, and gross revenue.

**Parameter provenance — read this before quoting a number.** Every constant
here (:data:`FARM_GATE_PRICE`, :data:`RETAIL_MARKUP`, :data:`RETAIL_DILUTION`
and the ten markup/dilution pairs in :data:`EDGE_ECONOMICS`) is *invented* for
this fictional scenario. None is estimated from, calibrated against, or
otherwise traceable to any empirical dataset or published figure. Consequently
the small producer share this module reports is an arithmetic consequence of
the chosen markups, **not** a measurement and not a replication of the
empirical literature on narcotics pricing. What the model does establish is the
mechanism: a chain of multiplicative per-leg markups drives the farm-gate share
down as the reciprocal of their product. ``tests/test_market_flow.py`` binds
that mechanism by re-running the model on substituted parameter sets, so the
headline share is demonstrably parameter-driven rather than a law.

Pure, deterministic, stdlib-only; no ``infrastructure.*`` and no ``bond_api``.
"""

from __future__ import annotations

from typing import Any, Mapping

from live_and_let_die.supply_graph import SAN_MONIQUE_DEMAND, SAN_MONIQUE_GRAPH

__all__ = [
    "EDGE_ECONOMICS",
    "FARM_GATE_PRICE",
    "RETAIL_DILUTION",
    "RETAIL_MARKUP",
    "market_flow_report",
    "node_prices",
]

#: Farm-gate price in USD per kilogram of pure-equivalent at the source.
#: Invented scenario parameter — not an empirical estimate.
FARM_GATE_PRICE = 300.0

#: Retail (street-level) markup multiplier applied after the final transit leg.
#: Invented scenario parameter — not an empirical estimate.
RETAIL_MARKUP = 3.0

#: Retail-level purity dilution factor (the "cut" at the point of sale).
#: Invented scenario parameter — not an empirical estimate.
RETAIL_DILUTION = 0.75

#: Per-leg economics: markup multiplier and purity dilution factor, keyed by
#: ``(source, target)`` on the canonical San Monique graph. All twenty numbers
#: are chosen for the fictional scenario; none is sourced from data.
EDGE_ECONOMICS: dict[tuple[str, str], tuple[float, float]] = {
    ("poppy_fields", "airfield"): (2.0, 0.95),
    ("poppy_fields", "field_works"): (1.2, 0.98),
    ("field_works", "airfield"): (2.0, 0.90),
    ("field_works", "harbor"): (2.0, 0.92),
    ("airfield", "cove"): (1.8, 0.90),
    ("airfield", "miami"): (8.0, 0.80),
    ("harbor", "miami"): (8.0, 0.78),
    ("cove", "miami"): (7.0, 0.80),
    ("harbor", "new_york"): (10.0, 0.72),
    ("cove", "new_york"): (9.0, 0.76),
}

_SOURCE = "poppy_fields"


#: Type of the per-leg economics table.
Economics = Mapping[tuple[str, str], tuple[float, float]]


def _path_price(node_id: str, economics: Economics, farm_gate_price: float) -> tuple[float, float]:
    """(price, purity) at ``node_id`` along its cheapest path from the source.

    Raises ``ValueError`` if a path edge has no entry in ``economics`` (a
    dataset inconsistency).
    """
    _, path = SAN_MONIQUE_GRAPH.shortest_path(_SOURCE, node_id)
    price = farm_gate_price
    purity = 1.0
    for src, dst in zip(path, path[1:], strict=False):
        try:
            markup, dilution = economics[(src, dst)]
        except KeyError:
            raise ValueError(f"no economics defined for leg {src!r} -> {dst!r}") from None
        price *= markup
        purity *= dilution
    return price, purity


def node_prices(
    economics: Economics | None = None,
    farm_gate_price: float | None = None,
) -> dict[str, tuple[float, float]]:
    """Price and purity at every reachable node (source -> each destination).

    ``economics`` and ``farm_gate_price`` default to the canonical (invented)
    scenario parameters. They are injectable so a test can re-run the identical
    model on a substituted parameter set and observe the result move — the only
    way to show the headline producer share is parameter-driven.
    """
    table: Economics = EDGE_ECONOMICS if economics is None else economics
    gate = FARM_GATE_PRICE if farm_gate_price is None else farm_gate_price
    result: dict[str, tuple[float, float]] = {_SOURCE: (gate, 1.0)}
    for node_id in SAN_MONIQUE_GRAPH.node_ids():
        if node_id == _SOURCE:
            continue
        if SAN_MONIQUE_GRAPH.degree(node_id) > 0 or node_id in SAN_MONIQUE_DEMAND:
            result[node_id] = _path_price(node_id, table, gate)
    return dict(sorted(result.items()))


def market_flow_report(
    economics: Economics | None = None,
    farm_gate_price: float | None = None,
    retail_markup: float | None = None,
    retail_dilution: float | None = None,
) -> dict[str, Any]:
    """Run the market-flow economic study (deterministic).

    All four parameters default to the canonical invented scenario values; pass
    substitutes to re-run the same model under different assumptions.
    """
    table: Economics = EDGE_ECONOMICS if economics is None else economics
    gate = FARM_GATE_PRICE if farm_gate_price is None else farm_gate_price
    markup = RETAIL_MARKUP if retail_markup is None else retail_markup
    dilution = RETAIL_DILUTION if retail_dilution is None else retail_dilution
    markets: dict[str, Any] = {}
    avg_street_numerator = 0.0
    total_demand = 0.0
    for market_id in sorted(SAN_MONIQUE_DEMAND):
        transit_price, transit_purity = _path_price(market_id, table, gate)
        street_price = transit_price * markup
        street_purity = transit_purity * dilution
        demand = SAN_MONIQUE_DEMAND[market_id]
        revenue = demand * street_price
        markets[market_id] = {
            "street_price": street_price,
            "street_purity": street_purity,
            "demand": demand,
            "revenue": revenue,
        }
        avg_street_numerator += demand * street_price
        total_demand += demand
    avg_street_price = avg_street_numerator / total_demand if total_demand else 0.0
    producer_share = gate / avg_street_price if avg_street_price else 0.0
    spread_ratio = avg_street_price / gate if gate else 0.0
    return {
        "farm_gate_price": gate,
        "markets": markets,
        "avg_street_price": avg_street_price,
        "producer_share": producer_share,
        "spread_ratio": spread_ratio,
        "total_revenue": sum(m["revenue"] for m in markets.values()),
    }
