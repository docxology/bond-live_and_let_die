"""Real-data tests for the San Monique island ops planner (mangrove/crocodile)."""

from __future__ import annotations

import pytest

from live_and_let_die.island_ops import (
    ROUTE_GOAL,
    ROUTE_START,
    SAN_MONIQUE_TERRAIN,
    TERRAIN_COSTS,
    TerrainGrid,
    TerrainRoute,
    min_san_monique_crocodile_exposure,
    plan_san_monique_route,
)


def test_terrain_grid_construction() -> None:
    grid = TerrainGrid(SAN_MONIQUE_TERRAIN)
    assert grid.nrows == 9
    assert grid.ncols == 9
    assert grid.cell(0, 0) == "R"
    with pytest.raises(IndexError):
        grid.cell(99, 0)


def test_terrain_grid_guardrails() -> None:
    with pytest.raises(ValueError):
        TerrainGrid(())
    with pytest.raises(ValueError):
        TerrainGrid(("AB", "A"))  # unequal widths
    with pytest.raises(ValueError):
        TerrainGrid(("AB", "?Z"))  # unknown glyph


def test_terrain_costs_and_predicates() -> None:
    grid = TerrainGrid(SAN_MONIQUE_TERRAIN)
    assert TERRAIN_COSTS["X"] == float("inf")
    assert grid.cost(8, 1) == 1.0  # beach
    assert grid.cost(5, 3) == 7.0  # crocodile
    assert grid.traversable(8, 1)
    assert not grid.traversable(2, 0)  # cliff
    assert not grid.traversable(99, 0)
    assert grid.is_crocodile(5, 3)
    assert not grid.is_crocodile(8, 1)
    assert not grid.is_crocodile(0, 0)


def test_neighbors_exclude_barriers_and_out_of_bounds() -> None:
    grid = TerrainGrid(SAN_MONIQUE_TERRAIN)
    # A corner beach: only in-bounds, traversable neighbours survive.
    assert (8, 1) in grid.neighbors(8, 2)
    # Cell in the cliff flank has few options.
    assert all(grid.traversable(*n) for n in grid.neighbors(2, 2))


def test_plan_route_trivial() -> None:
    grid = TerrainGrid(SAN_MONIQUE_TERRAIN)
    route = grid.plan_route(ROUTE_START, ROUTE_START)
    assert route.cost == 0.0 and route.path == (ROUTE_START,)
    assert route.edge_count() == 0


def test_plan_route_out_of_bounds_and_impassable() -> None:
    grid = TerrainGrid(SAN_MONIQUE_TERRAIN)
    with pytest.raises(ValueError):
        grid.plan_route((99, 0), ROUTE_GOAL)
    with pytest.raises(ValueError):
        grid.plan_route(ROUTE_START, (99, 0))
    with pytest.raises(ValueError):
        grid.plan_route((2, 0), ROUTE_GOAL)  # start on impassable cliff
    with pytest.raises(ValueError):
        grid.plan_route(ROUTE_START, (2, 0))  # goal on impassable cliff


def test_plan_route_unreachable() -> None:
    # Start sealed inside a barrier box cannot reach the outside goal.
    grid = TerrainGrid(("XXX", "XCX", "XXX"))
    with pytest.raises(ValueError):
        grid.plan_route((1, 1), (0, 1))


def test_plan_san_monique_route_known_values() -> None:
    route = plan_san_monique_route()
    assert isinstance(route, TerrainRoute)
    assert route.cost == 41.0
    assert route.crocodile_cells == 4
    assert route.edge_count() == 11
    assert route.path[0] == ROUTE_START
    assert route.path[-1] == ROUTE_GOAL
    # The route must cross the crocodile channel (the only north-south gap).
    assert route.crocodile_cells >= 1


def test_crocodile_exposure_counts_only_cells() -> None:
    grid = TerrainGrid(SAN_MONIQUE_TERRAIN)
    path = ((5, 3), (4, 3), (4, 4), (8, 1))
    assert grid.crocodile_exposure(path) == 2  # (5,3) and (4,3) are croc water


def test_min_crocodile_exposure_is_a_bound_over_all_routes() -> None:
    """The universal claim ("any approach wades at least N") is computed as one.

    Reading N off the cheapest route proves nothing about the alternatives; this
    is the exposure-minimising search over the entire route space.
    """
    grid = TerrainGrid(SAN_MONIQUE_TERRAIN)
    floor = grid.min_crocodile_exposure(ROUTE_START, ROUTE_GOAL)
    assert floor == 4
    assert min_san_monique_crocodile_exposure() == floor
    # The cheapest route can never beat the floor.
    assert plan_san_monique_route().crocodile_cells >= floor
    assert grid.min_crocodile_exposure(ROUTE_START, ROUTE_START) == 0


def test_min_exposure_differs_from_the_cheapest_routes_exposure() -> None:
    """Positive control: the two quantities are genuinely different measures.

    A one-cell crocodile shortcut (total cost 8) beside a crocodile-free
    perimeter detour (total cost 14). The cheapest route wades one cell; the
    exposure floor over all routes is zero. An implementation that just returned
    ``plan_route(...).crocodile_cells`` — the defect being repaired — returns 1
    here and fails.
    """
    grid = TerrainGrid(
        (
            "OCOOO",
            "OXXXO",
            "OXXXO",
            "OXXXO",
            "OOOOO",
        )
    )
    cheapest = grid.plan_route((0, 0), (0, 2))
    assert cheapest.crocodile_cells == 1
    assert cheapest.cost == 8.0
    assert grid.min_crocodile_exposure((0, 0), (0, 2)) == 0


def test_min_crocodile_exposure_guardrails() -> None:
    grid = TerrainGrid(SAN_MONIQUE_TERRAIN)
    with pytest.raises(ValueError):
        grid.min_crocodile_exposure((99, 0), ROUTE_GOAL)
    with pytest.raises(ValueError):
        grid.min_crocodile_exposure(ROUTE_START, (2, 0))  # impassable cliff
    sealed = TerrainGrid(("XXX", "XCX", "XXX", "OOO"))
    with pytest.raises(ValueError):
        sealed.min_crocodile_exposure((1, 1), (3, 1))


def test_deterministic_routes() -> None:
    grid = TerrainGrid(SAN_MONIQUE_TERRAIN)
    r1 = grid.plan_route(ROUTE_START, ROUTE_GOAL)
    r2 = grid.plan_route(ROUTE_START, ROUTE_GOAL)
    assert r1 == r2
