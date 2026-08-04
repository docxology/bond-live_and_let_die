# LIVE AND LET DIE (1973) — SAN MONIQUE

**PROJECT BOND · Phase 2 film package** · mission codename **SAN MONIQUE**

Deterministic special-agent mission software for Kananga's narcotics operation
on the Caribbean island of San Monique, built as one of 27 film packages in the
BOND suite. It implements the FROZEN BOND-API `MissionProvider` protocol over a
pure, infrastructure-free domain core.

## Concepts

Three film concepts, three pure domain modules:

| Module | Concept | Real algorithms & data |
| --- | --- | --- |
| `src/live_and_let_die/supply_graph.py` | Narcotics supply-graph analytics (production → transit → market) | Dijkstra shortest paths; Edmonds-Karp max-flow; residual minimum cut; per-transit-node disruption (critical-bottleneck) analysis |
| `src/live_and_let_die/coded_comms.py` | Voodoo-coded communiqué deciphering | Keyword (symbol-substitution) cipher; encipher/decipher; letter-frequency tables; frequency-attack solver with cosine-similarity scoring; voodoo glyph roster |
| `src/live_and_let_die/island_ops.py` | Caribbean island ops planner (mangrove/crocodile terrain) | Weighted terrain grid; 4-neighbour Dijkstra routing; crocodile-exposure hazard tracking |

The film's mission adapter, `src/live_and_let_die/mission.py`, layers the frozen
BOND-API protocol (`brief` / `recon` / `plan` / `execute` / `debrief`) over this
core and registers the analysers as gadgets.

## Canonical findings (computed, never hand-authored)

- Supply graph: 7 nodes, 10 legs; cheapest Miami route is
  `poppy_fields -> airfield -> miami` (cost 13); max throughput is 220 units,
  capped by a min-cut value of 220.
- The critical transit bottleneck is the **airfield** — neutralizing it stops
  150 units of Miami throughput (highest-value interdiction).
- The voodoo communiqué deciphers under the BARON keyword substitution to
  *"KANANGA LETS THE SNAKE BITE"*.
- The infiltration route (cost 41) wades 4 crocodile-water cells to reach the
  airfield.

## Install

From the repository root:

```bash
uv sync --extra dev        # installs deps incl. the local bond-api path dep
```

`pyproject.toml` declares a local path dependency on
`/Users/4d/Documents/GitHub/template/projects/working/bond/bond-api` so the
FROZEN protocol is importable.

## Run the mission

```bash
uv run python scripts/00_preflight.py              # verify readiness
uv run python scripts/run_mission.py               # full five-stage mission
uv run python scripts/brief.py                     # per-phase CLIs
uv run python scripts/recon.py
uv run python scripts/plan.py
uv run python scripts/execute.py
uv run python scripts/debrief.py
uv run python scripts/generate_figures.py          # output/figures/*.png
uv run python scripts/z_generate_manuscript_variables.py
```

Regenerable artifacts are written under `output/` (git-ignored).

## Manuscript

`manuscript/config.yaml` (identity + mission block) drives
`src/live_and_let_die/manuscript_variables.py`, which computes every
`{{TOKEN}}` from the pure domain core — no metric is hand-authored in prose.
`scripts/z_generate_manuscript_variables.py` hydrates and copies the numbered
sections to `output/manuscript/`; strict mode fails on any unresolved token.

## Verification gates

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format src/ scripts/ tests/
uv run mypy src/ scripts/
rg -n "template[_]code_project" .     # expectation: zero
```

See `docs/_generated/COUNTS.md` for the live test count and coverage.

## License

MIT — see `LICENSE`.
