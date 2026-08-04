"""Tests for SAN MONIQUE figure rendering (deterministic, headless)."""

from __future__ import annotations

from pathlib import Path

from live_and_let_die.figures import render_island_route, render_supply_graph


def test_render_both_figures_custom_path(tmp_path: Path) -> None:
    supply = render_supply_graph(tmp_path / "supply.png")
    island = render_island_route(tmp_path / "island.png")
    assert supply.is_file() and supply.stat().st_size > 0
    assert island.is_file() and island.stat().st_size > 0


def test_render_figures_default_output_dir() -> None:
    # Defaults land in the (git-ignored) output/figures/ directory.
    supply = render_supply_graph()
    island = render_island_route()
    assert "output/figures" in str(supply)
    assert "output/figures" in str(island)
    assert supply.is_file() and island.is_file()
