# AGENTS.md — tests

- No mocks: real data + computation only (see `docs/testing_philosophy.md`).
- Deterministic expectations stable across runs (fixed seed 8).
- Keep the `--cov-fail-under=90` gate green; regenerate `docs/_generated/COUNTS.md`
  with the live numbers.
- Match the real-data patterns in `PATTERNS.md`.
