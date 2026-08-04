#!/usr/bin/env python3
"""SAN MONIQUE — debrief: distil lessons from the executed mission outcome."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))  # noqa: E402

from live_and_let_die.mission import MissionProvider  # noqa: E402


def main() -> int:
    provider = MissionProvider()
    plan = provider.plan(provider.brief())
    outcome = provider.execute(plan)
    debrief = provider.debrief(outcome)
    print(f"outcome success={debrief.outcome.success}")
    for i, lesson in enumerate(debrief.lessons, start=1):
        print(f"lesson {i}: {lesson}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
