# tests — SAN MONIQUE

Real-data, deterministic, mock-free tests. Per-module files plus end-to-end,
cross-reference, figure, and subprocess-smoke coverage.

| File | Covers |
| --- | --- |
| `test_supply_graph.py` | Graph analytics: shortest paths, max-flow/min-cut, disruption, canonical analysis |
| `test_coded_comms.py` | Keyword cipher, encipher/decipher, frequency analysis, solver, roster |
| `test_island_ops.py` | Terrain grid, routing, crocodile exposure, guards |
| `test_mission.py` | Full `MissionProvider` lifecycle + outcome JSON round-trip + gadgets |
| `test_manuscript_variables.py` | Token hydration + live `{{TOKEN}}` cross-reference gate |
| `test_figures.py` | Deterministic figure rendering |
| `test_scripts_smoke.py` | Subprocess runs of every thin CLI + artifact assertions |

`conftest.py` forces `MPLBACKEND=Agg` and puts the package root + `src/` on
`sys.path`. Gate: `uv run pytest tests/ --cov=src --cov-fail-under=90`.
