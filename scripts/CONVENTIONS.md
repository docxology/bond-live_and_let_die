# CONVENTIONS — scripts

- Every script is runnable as `python scripts/<name>.py` after bootstrapping
  `src/` into `sys.path` (works with the project venv python directly).
- Exit code 0 iff the phase / checks pass; argparse-style errors exit 2.
- Artifact-writing scripts write under `output/` (git-ignored).
- Keep scripts thin: business logic in `src/`, never duplicated here.
