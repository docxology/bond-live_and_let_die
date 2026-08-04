"""Subprocess smoke tests for the thin SAN MONIQUE CLI scripts.

Each script is run with the venv's python from the package root; exit code 0
means the phase completed. Artifact-writing scripts are asserted by the files
they create under the git-ignored ``output/`` tree.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = PACKAGE_ROOT / "scripts"


def _run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        cwd=str(PACKAGE_ROOT),
        capture_output=True,
        text=True,
    )


def test_preflight_passes() -> None:
    result = _run("00_preflight.py")
    assert result.returncode == 0, result.stderr
    assert "PREFLIGHT PASS" in result.stdout


def test_run_mission_full_flow() -> None:
    result = _run("run_mission.py")
    assert result.returncode == 0, result.stderr
    assert "SAN MONIQUE" in result.stdout
    assert "airfield" in result.stdout


def test_per_phase_scripts_exit_zero() -> None:
    for script in ("brief.py", "recon.py", "plan.py", "execute.py", "debrief.py"):
        result = _run(script)
        assert result.returncode == 0, (script, result.stderr)


def test_execute_writes_outcome_artifact() -> None:
    result = _run("execute.py")
    assert result.returncode == 0, result.stderr
    artifact = PACKAGE_ROOT / "output" / "data" / "mission_outcome.json"
    assert artifact.is_file() and artifact.stat().st_size > 0


def test_generate_figures_writes_pngs() -> None:
    result = _run("generate_figures.py")
    assert result.returncode == 0, result.stderr
    for name in ("supply_graph.png", "island_route.png"):
        assert (PACKAGE_ROOT / "output" / "figures" / name).is_file()


def test_z_generate_manuscript_variables_strict() -> None:
    result = _run("z_generate_manuscript_variables.py")
    assert result.returncode == 0, result.stderr
    data = PACKAGE_ROOT / "output" / "data" / "manuscript_variables.json"
    assert data.is_file() and data.stat().st_size > 0
    resolved = PACKAGE_ROOT / "output" / "manuscript"
    assert len(list(resolved.glob("*.md"))) >= 1


def test_scripts_are_mockfree() -> None:
    for script in sorted(SCRIPTS.glob("*.py")):
        text = script.read_text(encoding="utf-8")
        assert "unittest.mock" not in text
        assert "MagicMock" not in text
