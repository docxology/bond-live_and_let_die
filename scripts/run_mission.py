#!/usr/bin/env python3
"""SAN MONIQUE — run the full five-stage mission and print the debrief."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))  # noqa: E402

from bond_api.protocol import ReconRequest, run_mission  # noqa: E402
from live_and_let_die.mission import MissionProvider  # noqa: E402


def main() -> int:
    provider = MissionProvider()
    debrief = run_mission(provider, ReconRequest("run full SAN MONIQUE analysis"))
    outcome = debrief.outcome
    supply = outcome.results["supply"]
    ops = outcome.results["ops"]
    comms = outcome.results["comms"]

    print(f"Film: {provider.film} · Mission: {provider.brief().codename}")
    print(f"Outcome success={outcome.success} · input_hash={outcome.provenance.input_hash}")
    print(f"Supply critical transit node : {supply['critical_transit_node']}")
    print(f"Disruption (units to Miami)  : {supply['disruption_units']:.0f}")
    print(f"Communiqué deciphered        : {comms['plaintext']}")
    print(f"Infiltration cost/crocodiles : {ops['route_cost']:.0f} / {ops['crocodile_cells']}")
    print("Lessons:")
    for lesson in debrief.lessons:
        print(f"  - {lesson}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
