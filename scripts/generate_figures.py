#!/usr/bin/env python3
"""SAN MONIQUE — render both mission figures (supply graph + island route)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))  # noqa: E402

from live_and_let_die.figures import render_island_route, render_supply_graph  # noqa: E402


def main() -> int:
    supply_path = render_supply_graph()
    island_path = render_island_route()
    print(f"supply graph : {supply_path}")
    print(f"island route : {island_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
