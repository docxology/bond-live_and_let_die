# scripts — thin orchestrators

Each script is a thin CLI: it bootstraps `src/` onto `sys.path` and delegates
to `src/live_and_let_die/*`. All business logic lives in `src/`.

| Script | Phase / purpose |
| --- | --- |
| `00_preflight.py` | Verify bond-api + provider + a full deterministic run |
| `run_mission.py` | Full five-stage mission → debrief |
| `brief.py` / `recon.py` / `plan.py` / `execute.py` / `debrief.py` | Per-phase CLIs |
| `generate_figures.py` | Render supply-graph + island-route figures → `output/figures/` |
| `z_generate_manuscript_variables.py` | Hydrate variables → `output/data/` + resolve sections → `output/manuscript/` |

Run from the package root with the project venv python, e.g.
`uv run python scripts/run_mission.py`.
