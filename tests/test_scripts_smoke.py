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


def test_generate_figures_writes_every_png() -> None:
    """The generator must render every figure the manuscript cites.

    ``interdiction_curve.png`` is asserted explicitly: it existed in
    ``figures/plots.py`` and was referenced by the results section while the
    generator script never called it, so the documented figure was never
    produced by the documented command.
    """
    figures_dir = PACKAGE_ROOT / "output" / "figures"
    for name in ("supply_graph.png", "interdiction_curve.png", "island_route.png"):
        stale = figures_dir / name
        if stale.exists():
            stale.unlink()

    result = _run("generate_figures.py")
    assert result.returncode == 0, result.stderr
    for name in ("supply_graph.png", "interdiction_curve.png", "island_route.png"):
        target = figures_dir / name
        assert target.is_file() and target.stat().st_size > 0, f"{name} was not rendered"


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
        assert "mocker.patch" not in text


def test_preflight_gate_survives_optimized_python() -> None:
    """The preflight checks must not be bare asserts.

    ``python -O`` strips ``assert`` statements, so a gate built on them passes
    unconditionally. Running preflight under ``-O`` proves the checks are real
    conditionals; the source scan proves it stays that way.
    """
    result = subprocess.run(
        [sys.executable, "-O", str(SCRIPTS / "00_preflight.py")],
        cwd=str(PACKAGE_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "PREFLIGHT PASS" in result.stdout

    source = (SCRIPTS / "00_preflight.py").read_text(encoding="utf-8")
    offenders = [
        line.strip() for line in source.splitlines() if line.strip().startswith("assert ") or line.strip() == "assert"
    ]
    assert not offenders, f"preflight must not gate on bare asserts: {offenders}"
