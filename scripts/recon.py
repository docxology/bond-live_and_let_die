#!/usr/bin/env python3
"""SAN MONIQUE — recon: survey the mission goal, assets, and ground truth."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))  # noqa: E402

from bond_api.protocol import ReconRequest  # noqa: E402
from live_and_let_die.mission import MissionProvider  # noqa: E402


def main() -> int:
    report = MissionProvider().recon(ReconRequest("survey the San Monique operation"))
    for finding in report.findings:
        print(f"{finding.label}: {finding.detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
