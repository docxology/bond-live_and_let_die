# Style — src

Follow the repo standard (ruff, 88-col, default). Highlights:

- Public functions: full type hints + docstrings with Args/Returns.
- Deterministic: fixed seeds, no untracked RNG, no wall-clock in artifacts.
- Pure modules stay side-effect-free; I/O lives in `mission.py` /
  `manuscript_variables.py` / `figures/plots.py` / `scripts/`.
- Dataclasses for structured values (`Node`, `Edge`, `TerrainRoute`).
