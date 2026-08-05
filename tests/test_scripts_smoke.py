"""Subprocess smoke tests for the thin SAN MONIQUE CLI scripts.

Each script is run with the venv's python from the package root; exit code 0
means the phase completed. Artifact-writing scripts are asserted by the files
they create under the git-ignored ``output/`` tree.
"""

from __future__ import annotations

import subprocess
import sys
import time
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


def _generated_artifact_bytes() -> dict[str, bytes]:
    """Every persisted artifact the byte-identical regeneration claim covers.

    That is the hydrated variable table plus every resolved manuscript section
    — the exact files ``z_generate_manuscript_variables.py`` writes. Figures
    (PNG) are rendered by a different script and are not in scope here.
    """
    data = PACKAGE_ROOT / "output" / "data" / "manuscript_variables.json"
    manuscript = PACKAGE_ROOT / "output" / "manuscript"
    artifacts = {"data/manuscript_variables.json": data.read_bytes()}
    for section in sorted(manuscript.glob("*.md")):
        artifacts[f"manuscript/{section.name}"] = section.read_bytes()
    return artifacts


def test_regeneration_is_byte_identical() -> None:
    """The documented regeneration command must reproduce its own output exactly.

    ``README.md`` and ``manuscript/06_reproducibility.md`` claim the manuscript
    artifacts regenerate byte-for-byte from the committed tree. This runs the
    real script twice and diffs the persisted bytes, so the claim is bound to
    behaviour rather than to a fixed value injected by a test.

    The sleep is load-bearing. The wall-clock stamp this package used to emit
    had one-second resolution, so two back-to-back runs produced identical
    bytes by luck and the breach survived a green suite. Crossing a second
    boundary is what makes the test able to fail.
    """
    first = _run("z_generate_manuscript_variables.py")
    assert first.returncode == 0, first.stderr
    before = _generated_artifact_bytes()
    assert len(before) > 1, "nothing was regenerated — the comparison would be vacuous"

    time.sleep(1.1)

    second = _run("z_generate_manuscript_variables.py")
    assert second.returncode == 0, second.stderr
    after = _generated_artifact_bytes()

    assert sorted(after) == sorted(before), "the two runs wrote different files"
    differing = sorted(name for name in before if before[name] != after[name])
    assert not differing, f"regeneration is not byte-identical: {differing}"


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
