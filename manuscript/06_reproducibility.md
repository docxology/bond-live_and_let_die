# Reproducibility

Every number in this manuscript is computed, never typed: aggregation runs
through `src/live_and_let_die/manuscript_variables.py`, whose `generate_variables`
hydrates each placeholder from `scripts/z_generate_manuscript_variables.py`.
The manuscript cross-reference test scans every numbered section
(`manuscript/[0-9]*.md`) and fails if any placeholder is unresolved or unused,
so the prose cannot drift from the code.

Result provenance is recorded per-mission: the canonical input hash is
`{{LALD_INPUT_HASH}}`, the fixed seed is {{LALD_SEED}}, and execution sets a zero
wall-clock figure. A SHA-256 digest of the canonical inputs fingerprints the
outcome, so an audited outcome can be re-derived without re-running the film.

Verification gates (see README):

```
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/
uv run mypy src/
rg -n "template[_]code_project" .   # expectation: zero
```
