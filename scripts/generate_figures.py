#!/usr/bin/env python3
"""SAN MONIQUE — render every mission figure.

Three deterministic figures: the narcotics supply graph, the interdiction
trade-off curve, and the island infiltration route. All land under the
git-ignored ``output/figures/`` tree.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))  # noqa: E402

from live_and_let_die.figures import (  # noqa: E402
    render_interdiction_curve,
    render_island_route,
    render_supply_graph,
)


def main() -> int:
    """Render all three figures and print each output path."""
    supply_path = render_supply_graph()
    interdiction_path = render_interdiction_curve()
    island_path = render_island_route()
    print(f"supply graph      : {supply_path}")
    print(f"interdiction curve: {interdiction_path}")
    print(f"island route      : {island_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
