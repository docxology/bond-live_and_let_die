#!/usr/bin/env python3
"""SAN MONIQUE — plan: schedule the analytical steps of the mission."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))  # noqa: E402

from live_and_let_die.mission import MissionProvider  # noqa: E402


def main() -> int:
    provider = MissionProvider()
    plan = provider.plan(provider.brief())
    for step in plan.steps:
        params = ", ".join(f"{k}={v}" for k, v in step.params.items())
        print(f"step {step.name}: {step.action} ({params})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
