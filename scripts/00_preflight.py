#!/usr/bin/env python3
"""SAN MONIQUE — 00 preflight: verify the package is ready to run a mission.

Checks that bond-api (the FROZEN protocol) is importable, that the film's
MissionProvider satisfies the protocol, and that a full deterministic run
succeeds. Exits 0 only if every check passes, and non-zero (with the failed
check named on stderr) otherwise.

The checks are explicit conditionals, never bare ``assert`` statements: under
``python -O`` asserts are stripped, which would turn this gate into an
unconditional pass.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))  # noqa: E402

import bond_api  # noqa: E402
from bond_api.protocol import MissionProvider as ProviderProtocol  # noqa: E402
from bond_api.protocol import ReconRequest, protocol_surface, run_mission  # noqa: E402
from live_and_let_die.mission import FILM, MissionProvider  # noqa: E402

#: The frozen bond-api mission flow: brief, recon, plan, execute, debrief.
EXPECTED_PROVIDER_METHODS = 5


def _fail(reason: str) -> int:
    """Report a failed preflight check on stderr and yield a non-zero status."""
    print(f"PREFLIGHT FAIL: {reason}", file=sys.stderr)
    return 1


def main() -> int:
    """Run every preflight check; return 0 only when all of them hold."""
    surface = protocol_surface()
    if not surface["dataclasses"]:
        return _fail("bond_api exposed no protocol dataclasses")
    if len(surface["provider_methods"]) != EXPECTED_PROVIDER_METHODS:
        return _fail(
            f"mission flow must have {EXPECTED_PROVIDER_METHODS} stages, got {len(surface['provider_methods'])}"
        )

    provider = MissionProvider()
    if not isinstance(provider, ProviderProtocol):
        return _fail("MissionProvider does not satisfy the frozen bond_api protocol")
    if provider.film != FILM:
        return _fail(f"provider film is {provider.film!r}, expected {FILM!r}")

    debrief = run_mission(provider, ReconRequest("preflight verification"))
    if not debrief.outcome.success:
        return _fail("mission outcome was not successful")
    if not debrief.lessons:
        return _fail("debrief produced no lessons")

    print(f"bond_api {bond_api.__version__} OK")
    print(f"film {provider.film} · protocol dataclasses: {len(surface['dataclasses'])}")
    print(f"mission flow: {', '.join(surface['provider_methods'])}")
    print(f"outcome success={debrief.outcome.success} lessons={len(debrief.lessons)}")
    print("PREFLIGHT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
