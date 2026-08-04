"""SAN MONIQUE figure rendering (matplotlib, deterministic).

Two publication figures:

* :func:`render_supply_graph` — the narcotics supply graph with the cheapest
  production->Miami route and the critical transit bottleneck highlighted.
* :func:`render_island_route` — the mangrove/crocodile terrain grid with the
  planned infiltration route overlaid.

All output is deterministic and written under ``output/figures/`` (git-ignored,
regenerable). Figure data is derived from the pure domain modules — no numbers
are hand-authored here.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless; tests must not open display windows

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from live_and_let_die.island_ops import (
    ROUTE_GOAL,
    ROUTE_START,
    SAN_MONIQUE_TERRAIN,
    TERRAIN_NAMES,
    TerrainGrid,
    plan_san_monique_route,
)
from live_and_let_die.supply_graph import (
    SAN_MONIQUE_GRAPH,
    Node,
    analyze_san_monique,
)

__all__ = ["render_island_route", "render_supply_graph"]

PACKAGE_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FIGURE_DIR = PACKAGE_ROOT / "output" / "figures"

#: Deterministic layout for the supply graph (production left -> markets right).
_NODE_POS: dict[str, tuple[float, float]] = {
    "poppy_fields": (0.0, 0.4),
    "field_works": (0.0, -0.4),
    "airfield": (1.0, 0.3),
    "cove": (2.0, 0.3),
    "harbor": (1.0, -0.5),
    "miami": (3.0, 0.3),
    "new_york": (3.0, -0.3),
}

#: Terrain glyph -> RGB colour for the island figure.
_TERRAIN_RGB: dict[str, tuple[float, float, float]] = {
    "R": (0.55, 0.55, 0.55),
    "O": (0.76, 0.70, 0.50),
    "B": (0.91, 0.83, 0.55),
    "M": (0.12, 0.47, 0.19),
    "S": (0.42, 0.30, 0.26),
    "W": (0.29, 0.57, 0.85),
    "C": (0.06, 0.16, 0.32),
    "X": (0.25, 0.25, 0.25),
}


def _ensure_dir(target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)


def render_supply_graph(out_path: str | Path | None = None) -> Path:
    """Render (and return) the San Monique supply graph figure."""
    target = Path(out_path) if out_path is not None else DEFAULT_FIGURE_DIR / "supply_graph.png"
    _ensure_dir(target)

    analysis = analyze_san_monique()
    _, path = SAN_MONIQUE_GRAPH.shortest_path("poppy_fields", "miami")
    path_edges = set(zip(path, path[1:]))
    critical = analysis["critical_transit_node"]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for edge in SAN_MONIQUE_GRAPH.edges():
        sx, sy = _NODE_POS[edge.source]
        tx, ty = _NODE_POS[edge.target]
        is_path = (edge.source, edge.target) in path_edges
        colour = "#C0392B" if is_path else "#5D6D7E"
        lw = 2.6 if is_path else 1.4
        ax.annotate(
            "",
            xy=(tx, ty),
            xytext=(sx, sy),
            arrowprops=dict(arrowstyle="-|>", color=colour, lw=lw, shrinkA=12, shrinkB=12),
        )
        ax.text(
            (sx + tx) / 2,
            (sy + ty) / 2,
            f"{edge.weight:.0f}",
            fontsize=7,
            color=colour,
            ha="center",
            va="center",
        )

    for node in SAN_MONIQUE_GRAPH.node_ids():
        nx, ny = _NODE_POS[node]
        node_obj: Node = SAN_MONIQUE_GRAPH.node(node)
        is_critical = node == critical
        colour = "#C0392B" if is_critical else "#1A5276"
        ax.scatter(nx, ny, s=280 if is_critical else 220, color=colour, zorder=3)
        label = node_obj.name if not is_critical else f"{node_obj.name}  [bottleneck]"
        ax.text(nx, ny + 0.13, label, fontsize=8, ha="center", color="#17202A")

    ax.set_title("San Monique narcotics supply graph\n(red = cheapest production→Miami route · bottleneck = airfield)")
    ax.set_xlim(-0.4, 3.4)
    ax.set_ylim(-1.0, 1.1)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(target, dpi=150)
    plt.close(fig)
    return target


def _render_grid_rgb(grid: TerrainGrid) -> np.ndarray:
    rgb = np.zeros((grid.nrows, grid.ncols, 3), dtype=float)
    for r in range(grid.nrows):
        for c in range(grid.ncols):
            rgb[r, c, :] = _TERRAIN_RGB[grid.cell(r, c)]
    return rgb


def render_island_route(out_path: str | Path | None = None) -> Path:
    """Render (and return) the San Monique infiltration route figure."""
    target = Path(out_path) if out_path is not None else DEFAULT_FIGURE_DIR / "island_route.png"
    _ensure_dir(target)

    grid = TerrainGrid(SAN_MONIQUE_TERRAIN)
    route = plan_san_monique_route()
    rgb = _render_grid_rgb(grid)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(rgb, interpolation="nearest")
    path = route.path
    xs = [c for (_, c) in path]
    ys = [r for (r, _) in path]
    ax.plot(xs, ys, color="#F4D03F", lw=2.6, marker="o", ms=4, zorder=3)
    ax.scatter([ROUTE_START[1]], [ROUTE_START[0]], marker="o", s=140, color="#27AE60", zorder=4, label="landing")
    ax.scatter([ROUTE_GOAL[1]], [ROUTE_GOAL[0]], marker="*", s=240, color="#C0392B", zorder=4, label="airfield")

    legend_specs = [(glyph, TERRAIN_NAMES[glyph]) for glyph in ("R", "B", "M", "W", "C", "X")]
    handles = [
        Line2D([0], [0], marker="s", color="none", markerfacecolor=_TERRAIN_RGB[glyph], markersize=9, label=name)
        for glyph, name in legend_specs
    ]
    handles.append(Line2D([0], [0], color="#F4D03F", lw=2.6, label="infiltration route"))
    ax.legend(handles=handles, loc="lower left", fontsize=7, framealpha=0.9)

    ax.set_title(
        f"San Monique infiltration route\ncost {route.cost:.0f} · wades {route.crocodile_cells} crocodile-water cells"
    )
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(target, dpi=150)
    plt.close(fig)
    return target
