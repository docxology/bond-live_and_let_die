# Agent instructions — LIVE AND LET DIE / SAN MONIQUE

Operational constraints for AI agents modifying this PROJECT BOND film package.

## Critical directives

- **Scope**: work only inside this package directory. Never touch sibling BOND
  packages, bond root files, or the template repo.
- **Local-only**: no remote, never push. Commit path-scoped inside this repo.
- **Protocol**: implement / depend on the FROZEN `bond_api` types; do not invent
  your own `MissionProvider` protocol. `src/live_and_let_die/mission.py` is the
  thin adapter; the pure domain core must remain importable without `bond_api`.
- **Determinism**: fixed seed (8), no untracked RNG, no wall-clock in persisted
  artifacts. Canonical SHA-256 input hash for auditable provenance.
- **No mocks**: no `unittest.mock` / `MagicMock` / `mocker.patch`. Real data and
  computation only.
- **Pure core**: `supply_graph.py`, `coded_comms.py`, `island_ops.py` must not
  import `infrastructure.*` or `bond_api`.
- **Thin scripts**: business logic in `src/`; `scripts/` are thin wrappers
  (sys.path bootstrap + argv forwarding).

## Manuscript rule

Manuscript metrics are injected from `manuscript/config.yaml` +
`src/live_and_let_die/manuscript_variables.py`. Never hand-author metrics in
prose. When you change the domain core, regenerate the manuscript variables and
figures, and update `docs/_generated/COUNTS.md` with live numbers.

## Verification checklist (run before declaring done)

```bash
uv sync --extra dev   # installs deps incl. the local bond-api path dependency
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/
uv run ruff format src/ scripts/ tests/
uv run mypy src/ scripts/
rg -n "template[_]code_project" .        # expectation: zero (bracket-split so this
                                         # line cannot trip its own gate)
git status --short                        # clean after your commit(s)
```

Regenerate artifacts (`scripts/generate_figures.py`,
`scripts/z_generate_manuscript_variables.py`) so `output/` reflects the current
code, then confirm `git status` is clean.
