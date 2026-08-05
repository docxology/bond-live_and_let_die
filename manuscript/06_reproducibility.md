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

Verification gates (see README):

```
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/
uv run mypy src/
rg -n "template[_]code_project" .   # expectation: zero
```
