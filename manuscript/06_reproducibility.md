# Reproducibility

Every number in this manuscript is computed, never typed: the thin orchestrator
`scripts/z_generate_manuscript_variables.py` calls `generate_variables` in
`src/live_and_let_die/manuscript_variables.py`, which computes each placeholder
from the pure domain core. The manuscript cross-reference test scans every
numbered section (`manuscript/[0-9]*.md`) and fails if any placeholder used in
prose is not produced by `generate_variables()`, so the prose cannot cite a
number the code does not compute. (The converse is not gated: a produced token
that no section uses is permitted and is not a test failure.)

Result provenance is recorded per-mission: the canonical input hash is
`{{LALD_INPUT_HASH}}`, the fixed seed is {{LALD_SEED}}, and execution sets a zero
wall-clock figure. A SHA-256 digest of the canonical inputs fingerprints the
inputs, so a re-run can be checked against an audited outcome — the digest
identifies the inputs, it does not by itself reconstitute the results.

## Byte-identical regeneration

Running `scripts/z_generate_manuscript_variables.py` twice on an unchanged tree
produces byte-identical artifacts. **Scope of that claim:** the hydrated table
`output/data/manuscript_variables.json` and every resolved section under
`output/manuscript/`. Every value in those files comes from a committed source —
the pure domain core, or `manuscript/config.yaml` — and nothing under `src/`
reads the system clock, so there is no run-varying byte to differ. The
publication date above is `paper.date` in `manuscript/config.yaml`, bumped by
hand when the manuscript is republished; it is deliberately not a generation
timestamp, because a generation timestamp would make every regeneration differ.

The claim is gated, not asserted:
`tests/test_scripts_smoke.py::test_regeneration_is_byte_identical` runs the real
script twice — separated by more than one wall-clock second, so a
second-resolution clock cannot slip through by landing in the same second — and
diffs the persisted bytes. Its in-process counterpart is
`tests/test_manuscript_variables.py::test_regenerating_variables_across_a_wall_clock_second_is_identical`.

Two things are outside the scope of the byte-identical claim. Figures under
`output/figures/` are PNGs written by a separate script and are not diffed
here. And nothing in this package records a real timestamp anywhere — if a
future run-scoped provenance record needs one, it must live outside the two
paths named above, and this scope statement must be amended to say so.

Verification gates (see README):

```
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
rg -n "template[_]code_project" .   # expectation: zero
```
