"""Tests for SAN MONIQUE figure rendering (deterministic, headless)."""

from __future__ import annotations

from pathlib import Path

from live_and_let_die.figures import (
    render_interdiction_curve,
    render_island_route,
    render_supply_graph,
)


def test_render_all_figures_custom_path(tmp_path: Path) -> None:
    supply = render_supply_graph(tmp_path / "supply.png")
    island = render_island_route(tmp_path / "island.png")
    interdict = render_interdiction_curve(tmp_path / "interdict.png")
    for target in (supply, island, interdict):
        assert target.is_file() and target.stat().st_size > 0


def test_render_figures_default_output_dir() -> None:
    # Defaults land in the (git-ignored) output/figures/ directory.
    supply = render_supply_graph()
    island = render_island_route()
    interdict = render_interdiction_curve()
    for target in (supply, island, interdict):
        assert "output/figures" in str(target)
        assert target.is_file()
