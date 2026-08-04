#!/usr/bin/env python3
"""SAN MONIQUE — 00 preflight: verify the package is ready to run a mission.

Checks that bond-api (the FROZEN protocol) is importable, that the film's
MissionProvider satisfies the protocol, and that a full deterministic run
succeeds. Exits 0 only if every check passes.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))  # noqa: E402

import bond_api  # noqa: E402
from bond_api.protocol import MissionProvider as ProviderProtocol  # noqa: E402
from bond_api.protocol import protocol_surface, run_mission  # noqa: E402
from live_and_let_die.mission import MissionProvider  # noqa: E402


def main() -> int:
    surface = protocol_surface()
    assert surface["dataclasses"], "bond_api exposed no dataclasses"
    assert len(surface["provider_methods"]) == 5, "mission flow must have 5 stages"

    provider = MissionProvider()
    assert isinstance(provider, ProviderProtocol), "MissionProvider violates the protocol"
    assert provider.film == "live_and_let_die"

    from bond_api.protocol import ReconRequest  # noqa: E402

    debrief = run_mission(provider, ReconRequest("preflight verification"))
    assert debrief.outcome.success, "mission outcome was not successful"

    print(f"bond_api {bond_api.__version__} OK")
    print(f"film {provider.film} · protocol dataclasses: {len(surface['dataclasses'])}")
    print(f"mission flow: {', '.join(surface['provider_methods'])}")
    print(f"outcome success={debrief.outcome.success} lessons={len(debrief.lessons)}")
    print("PREFLIGHT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
