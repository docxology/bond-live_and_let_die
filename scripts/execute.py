#!/usr/bin/env python3
"""SAN MONIQUE — execute: run all three analyses and write a provenanced outcome.

Writes the deterministic outcome (bond_api JSON) to output/data/mission_outcome.json.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))  # noqa: E402

from bond_api.serialization import to_json  # noqa: E402
from live_and_let_die.mission import MissionProvider  # noqa: E402


def main() -> int:
    provider = MissionProvider()
    plan = provider.plan(provider.brief())
    outcome = provider.execute(plan)

    out_dir = ROOT / "output" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "mission_outcome.json"
    target.write_text(to_json(outcome), encoding="utf-8")

    print(f"success={outcome.success} steps={outcome.results['steps_completed']}")
    print(f"input_hash={outcome.provenance.input_hash}")
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
