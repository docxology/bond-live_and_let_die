# Testing philosophy — LIVE AND LET DIE / SAN MONIQUE

Tests are **real-data, deterministic, and mock-free**.

## Principles

1. **No mocks.** No `unittest.mock`, `MagicMock`, `mocker.patch`, or
   `create_autospec`. We validate real computation: the canonical San Monique
   datasets and the algorithms operating on them.
2. **Deterministic assertions.** Every expected value is stable because the
   inputs and algorithms are deterministic (fixed seed 8, no untracked RNG, no
   wall-clock in artifacts). Tests assert exact known values (e.g. route cost
   41, 4 crocodile cells, bottleneck airfield).
3. **Coverage gate.** `uv run pytest tests/ --cov=src --cov-fail-under=90`
   enforces ≥90% line+branch on `src/`. Live count in
   `docs/_generated/COUNTS.md`.
4. **Per-module real-data files.** `test_supply_graph.py`,
   `test_coded_comms.py`, `test_island_ops.py` cover each pure module's
   algorithm and error branches with real inputs.
5. **End-to-end + cross-reference.** `test_mission.py` runs the full
   `MissionProvider` lifecycle and the outcome JSON round-trip;
   `test_manuscript_variables.py` holds the live `{{TOKEN}}` cross-reference
   gate over `manuscript/[0-9]*.md`.
6. **Subprocess smoke.** `test_scripts_smoke.py` runs each thin CLI with the
   venv python from the package root, asserting exit code 0 and artifact
   creation under `output/`.

## Conventions

- `conftest.py` forces `MPLBACKEND=Agg` (headless) and puts the package root
  and `src/` on `sys.path`.
- Deterministic branch coverage: error branches (invalid node/edge, out-of-bounds
  cell, unreachable goal, unknown source) are exercised explicitly.
- `output/` is git-ignored; script smoke tests write regenerable artifacts that
  do not dirty the tree.
