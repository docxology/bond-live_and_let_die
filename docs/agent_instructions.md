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
- **Pure core**: all six domain modules — `supply_graph.py`, `interdiction.py`,
  `coded_comms.py`, `voodoo_drums.py`, `market_flow.py`, `island_ops.py` — must
  stay importable in isolation: no `infrastructure.*`, no `bond_api`, stdlib
  only. `mission.py` is the sole `bond_api` importer.
- **Thin scripts**: business logic in `src/`; `scripts/` are thin wrappers
  (sys.path bootstrap + argv forwarding). Verification checks in a script use
  explicit `if ...: return 1`, never bare `assert` — `python -O` strips asserts
  and would turn a gate into an unconditional pass.
- **Derive, never type**: any value that the code can compute — a node count, a
  bottleneck name, a module count — must be interpolated, including in figure
  captions, `Asset` payloads, and `Finding` details. A literal there is a lie
  waiting for the dataset to change.

## Manuscript rule

Manuscript metrics are injected from `manuscript/config.yaml` +
`src/live_and_let_die/manuscript_variables.py`. Never hand-author metrics in
prose. When you change the domain core, regenerate the manuscript variables and
figures, and update `docs/_generated/COUNTS.md` with live numbers.

The rule extends past obvious results to *constants*: the provenance seed, the
terrain grid shape, the alphabet size, the terrain cost table, the drum timing,
the module and gadget counts all arrive as tokens
(`{{LALD_SEED}}`, `{{LALD_TERRAIN_SHAPE}}`, `{{LALD_ALPHABET_SIZE}}`,
`{{LALD_TERRAIN_COSTS}}`, `{{LALD_DRUM_TIMING}}`, `{{LALD_MODULE_COUNT}}`,
`{{LALD_GADGET_COUNT}}`). If you introduce a new quantity in prose, add it to
`generate_variables()` first — `tests/test_manuscript_variables.py` fails on any
token that does not resolve, and strict-mode hydration fails on any that is left
unsubstituted.

To add a new reported number:

1. compute it in the pure module that owns it;
2. surface it through `run_analysis()` if a mission should report it;
3. add the `LALD_*` entry in `generate_variables()`;
4. reference `{{TOKEN}}` in the section prose;
5. run `scripts/z_generate_manuscript_variables.py` and read the output.

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
