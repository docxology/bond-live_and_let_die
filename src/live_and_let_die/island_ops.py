"""Caribbean island ops planner over mangrove / crocodile terrain.

San Monique is a mangrove-choked Caribbean island criss-crossed by crocodile
infested lagoons. This module turns the island into a weighted terrain grid and
plans the infiltration route that minimises total movement cost while it
tracks how much of the route crosses crocodile water.

* :class:`TerrainGrid` — a validated 2-D grid where each cell is a terrain type
  with a movement cost (barrier cells are impassable).
* :func:`TerrainGrid.plan_route` — Dijkstra over 4-neighbours returning the
  cheapest route plus its crocodile exposure.
* :func:`TerrainGrid.crocodile_exposure` — how much of a route wades into
  crocodile water.

Pure, deterministic, stdlib-only; no ``infrastructure.*`` and no ``bond_api``.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass

__all__ = [
    "CROCODILE",
    "ROUTE_START",
    "ROUTE_GOAL",
    "SAN_MONIQUE_TERRAIN",
    "TERRAIN_COSTS",
    "TerrainGrid",
    "TerrainRoute",
    "plan_san_monique_route",
]

#: Terrain glyphs and their per-cell movement cost. ``X`` is impassable.
TERRAIN_COSTS: dict[str, float] = {
    "R": 1.0,  # road
    "O": 1.0,  # open ground
    "B": 1.0,  # beach
    "M": 3.0,  # mangrove
    "S": 5.0,  # swamp / mudflat
    "W": 3.0,  # open water (boatable but slow)
    "C": 7.0,  # crocodile water   <-- the hazard
    "X": float("inf"),
}

#: The crocodile glyph.
CROCODILE = "C"

#: Human-readable terrain names for reporting and the figure legend.
TERRAIN_NAMES: dict[str, str] = {
    "R": "road",
    "O": "open ground",
    "B": "beach",
    "M": "mangrove",
    "S": "swamp",
    "W": "open water",
    "C": "crocodile water",
    "X": "impassable",
}


@dataclass(frozen=True)
class TerrainRoute:
    """The outcome of a terrain route search."""

    cost: float
    path: tuple[tuple[int, int], ...]
    crocodile_cells: int

    def edge_count(self) -> int:
        """Number of moves (cells in the path minus the starting cell)."""
        return max(0, len(self.path) - 1)


class TerrainGrid:
    """A rectangular terrain grid over which an agent plans a route.

    Cells are referenced as ``(row, col)`` with row 0 at the top. Diagonal moves
    are not permitted; only the four cardinal neighbours are traversable.
    """

    def __init__(self, rows: tuple[str, ...]) -> None:
        if not rows:
            raise ValueError("terrain rows must be non-empty")
        width = len(rows[0])
        if any(len(row) != width for row in rows):
            raise ValueError("all terrain rows must have equal length")
        if not all(set(row) <= set(TERRAIN_COSTS) for row in rows):
            unknown = sorted({ch for row in rows for ch in row} - set(TERRAIN_COSTS))
            raise ValueError(f"unknown terrain glyphs: {unknown}")
        self._rows = rows
        self._nrows = len(rows)
        self._ncols = width

    @property
    def nrows(self) -> int:
        return self._nrows

    @property
    def ncols(self) -> int:
        return self._ncols

    def cell(self, row: int, col: int) -> str:
        """The terrain glyph at ``(row, col)``."""
        if not self.in_bounds(row, col):
            raise IndexError(f"cell ({row}, {col}) out of bounds")
        return self._rows[row][col]

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self._nrows and 0 <= col < self._ncols

    def cost(self, row: int, col: int) -> float:
        """Movement cost of occupying ``(row, col)`` (infinite for barriers)."""
        return TERRAIN_COSTS[self.cell(row, col)]

    def traversable(self, row: int, col: int) -> bool:
        return self.in_bounds(row, col) and TERRAIN_COSTS[self.cell(row, col)] != float("inf")

    def is_crocodile(self, row: int, col: int) -> bool:
        return self.in_bounds(row, col) and self.cell(row, col) == CROCODILE

    def neighbors(self, row: int, col: int) -> tuple[tuple[int, int], ...]:
        """Traversable in-bounds cardinal neighbours, row-major sorted."""
        candidates = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        return tuple(c for c in candidates if self.traversable(*c))

    def _entrance_cost(self, current: tuple[int, int], nxt: tuple[int, int]) -> float:
        return self.cost(*nxt)

    def plan_route(self, start: tuple[int, int], goal: tuple[int, int]) -> TerrainRoute:
        """Dijkstra: cheapest route from ``start`` to ``goal``.

        The total cost is the sum of the entrance cost of every cell after the
        start. Tie-breaking is deterministic (``(cost, row, col)`` heap keys).
        An unreachable goal raises ``ValueError``.
        """
        if not self.in_bounds(*start):
            raise ValueError(f"start {start} out of bounds")
        if not self.in_bounds(*goal):
            raise ValueError(f"goal {goal} out of bounds")
        if not self.traversable(*start):
            raise ValueError(f"start {start} is not traversable")
        if not self.traversable(*goal):
            raise ValueError(f"goal {goal} is not traversable")
        if start == goal:
            return TerrainRoute(0.0, (start,), 0)

        dist: dict[tuple[int, int], float] = {start: 0.0}
        prev: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
        heap: list[tuple[float, int, int, tuple[int, int]]] = [(0.0, start[0], start[1], start)]
        while heap:
            cost, r, c, cell = heapq.heappop(heap)
            if cost != dist.get(cell):
                continue
            if cell == goal:
                break
            for nxt in self.neighbors(*cell):
                new_cost = cost + self._entrance_cost(cell, nxt)
                if new_cost < dist.get(nxt, float("inf")):
                    dist[nxt] = new_cost
                    prev[nxt] = cell
                    heapq.heappush(heap, (new_cost, nxt[0], nxt[1], nxt))
        if goal not in dist:
            raise ValueError(f"no route from {start} to {goal}")
        return self._build_route(start, goal, prev, dist[goal])

    def _build_route(
        self,
        start: tuple[int, int],
        goal: tuple[int, int],
        prev: dict[tuple[int, int], tuple[int, int] | None],
        cost: float,
    ) -> TerrainRoute:
        cell = goal
        path: list[tuple[int, int]] = [cell]
        while cell != start:
            prior = prev[cell]
            assert prior is not None
            cell = prior
            path.append(cell)
        path.reverse()
        return TerrainRoute(cost, tuple(path), self.crocodile_exposure(tuple(path)))

    def crocodile_exposure(self, path: tuple[tuple[int, int], ...]) -> int:
        """Number of crocodile-water cells traversed (excluding the start)."""
        return sum(1 for (r, c) in path[1:] if self.is_crocodile(r, c))


# ---------------------------------------------------------------------------
# Canonical San Monique terrain (deterministic). 9x9.
#   r0 is the north coast (airfield approach), r8 the south landing beaches.
#   Rows 2-5 are impassable cliff on the flanks; the only north-south gap is a
#   crocodile channel (cols 3-5), so any overland route must wade it.
#   Start: (8, 1) southern beach -> Goal: (0, 4) airfield zone.
# ---------------------------------------------------------------------------
SAN_MONIQUE_TERRAIN: tuple[str, ...] = (
    "RROOOOOOX",  # r0  north coast / airfield approach
    "OOMMMMOOX",  # r1
    "XXXCCCXXX",  # r2  cliff flanks + crocodile channel
    "XXXCCCXXX",  # r3
    "XXXCCCXXX",  # r4
    "XXXCCCXXX",  # r5
    "OOMMMMOOX",  # r6
    "MMMMMMMMX",  # r7  mangrove belt
    "BBBOOOOOX",  # r8  south landing beaches
)

#: Infiltration start: the southern landing beach.
ROUTE_START = (8, 1)
#: Infiltration goal: the airfield zone on the north coast.
ROUTE_GOAL = (0, 4)


def plan_san_monique_route() -> TerrainRoute:
    """Plan the canonical infiltration route across San Monique (deterministic)."""
    return TerrainGrid(SAN_MONIQUE_TERRAIN).plan_route(ROUTE_START, ROUTE_GOAL)
