"""SAN MONIQUE figure generation (matplotlib, deterministic).

Renders the supply-graph and island-route figures under ``output/figures/``.
"""

from __future__ import annotations

from live_and_let_die.figures.plots import (
    render_island_route,
    render_supply_graph,
)

__all__ = ["render_island_route", "render_supply_graph"]
