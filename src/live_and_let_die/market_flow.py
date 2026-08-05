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

The model reproduces the classic finding that the farm-gate producer captures
only a small fraction of the street value — the "producer share" — which is the
economic heart of narcotics interdiction. Pure, deterministic, stdlib-only; no
``infrastructure.*`` and no ``bond_api``.
"""

from __future__ import annotations

from typing import Any

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
FARM_GATE_PRICE = 300.0

#: Retail (street-level) markup multiplier applied after the final transit leg.
RETAIL_MARKUP = 3.0

#: Retail-level purity dilution factor (the "cut" at the point of sale).
RETAIL_DILUTION = 0.75

#: Per-leg economics: markup multiplier and purity dilution factor, keyed by
#: ``(source, target)`` on the canonical San Monique graph.
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


def _path_price(node_id: str) -> tuple[float, float]:
    """(price, purity) at ``node_id`` along its cheapest path from the source.

    Raises ``ValueError`` if a path edge has no defined economics (a dataset
    inconsistency).
    """
    _, path = SAN_MONIQUE_GRAPH.shortest_path(_SOURCE, node_id)
    price = FARM_GATE_PRICE
    purity = 1.0
    for src, dst in zip(path, path[1:], strict=False):
        try:
            markup, dilution = EDGE_ECONOMICS[(src, dst)]
        except KeyError:
            raise ValueError(f"no economics defined for leg {src!r} -> {dst!r}") from None
        price *= markup
        purity *= dilution
    return price, purity


def node_prices() -> dict[str, tuple[float, float]]:
    """Price and purity at every reachable node (source -> each destination)."""
    result: dict[str, tuple[float, float]] = {_SOURCE: (FARM_GATE_PRICE, 1.0)}
    for node_id in SAN_MONIQUE_GRAPH.node_ids():
        if node_id == _SOURCE:
            continue
        if SAN_MONIQUE_GRAPH.degree(node_id) > 0 or node_id in SAN_MONIQUE_DEMAND:
            result[node_id] = _path_price(node_id)
    return dict(sorted(result.items()))


def market_flow_report() -> dict[str, Any]:
    """Run the canonical market-flow economic study (deterministic)."""
    markets: dict[str, Any] = {}
    avg_street_numerator = 0.0
    total_demand = 0.0
    for market_id in sorted(SAN_MONIQUE_DEMAND):
        transit_price, transit_purity = _path_price(market_id)
        street_price = transit_price * RETAIL_MARKUP
        street_purity = transit_purity * RETAIL_DILUTION
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
    producer_share = FARM_GATE_PRICE / avg_street_price if avg_street_price else 0.0
    spread_ratio = avg_street_price / FARM_GATE_PRICE if FARM_GATE_PRICE else 0.0
    return {
        "farm_gate_price": FARM_GATE_PRICE,
        "markets": markets,
        "avg_street_price": avg_street_price,
        "producer_share": producer_share,
        "spread_ratio": spread_ratio,
        "total_revenue": sum(m["revenue"] for m in markets.values()),
    }
