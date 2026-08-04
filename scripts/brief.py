#!/usr/bin/env python3
"""SAN MONIQUE — brief: declare the mission (objectives, assets, constraints)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))  # noqa: E402

from live_and_let_die.mission import MissionProvider  # noqa: E402


def main() -> int:
    brief = MissionProvider().brief()
    print(f"film={brief.film} codename={brief.codename}")
    for i, objective in enumerate(brief.objectives, start=1):
        print(f"objective {i}: {objective}")
    for asset in brief.assets:
        print(f"asset {asset.kind}: {asset.name}")
    for constraint in brief.constraints:
        print(f"constraint {constraint.kind}: {constraint.detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
