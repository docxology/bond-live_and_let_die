# TODO — LIVE AND LET DIE / SAN MONIQUE

Phase-2 build status and declared integration points. This file reflects what
was built and what is intentionally deferred.

## Built (Phase 2, complete)

- **Pure domain core** (3 modules, importable without bond-api):
  - `src/live_and_let_die/supply_graph.py` — supply-graph analytics: Dijkstra
    shortest paths, Edmonds-Karp max-flow, residual min-cut, edge- and
    node-level disruption analysis, canonical San Monique graph + `analyze_san_monique()`.
  - `src/live_and_let_die/coded_comms.py` — keyword (symbol-substitution)
    cipher, encipher/decipher, frequency tables, frequency-attack solver,
    cosine-similarity scoring, voodoo glyph roster.
  - `src/live_and_let_die/island_ops.py` — terrain grid, 4-neighbour Dijkstra
    routing, crocodile-exposure hazard metric.
- **Mission adapter**: `src/live_and_let_die/mission.py` implements the FROZEN
  BOND-API `MissionProvider` (film `live_and_let_die`, codename `SAN MONIQUE`),
  deterministic provenance (seed 8, SHA-256 input hash), and registers gadgets
  (`supply_graph_analyzer`, `communique_decipher`, `island_route_planner`) on
  the `bond_api.GadgetRegistry`.
- **Figures**: `src/live_and_let_die/figures/plots.py` renders the supply graph
  and island-route figures to `output/figures/`.
- **Manuscript**: `manuscript/config.yaml` + sections; all metrics injected via
  `manuscript_variables.py` (no hardcoded prose numbers).
- **CLIs**: `scripts/` thin wrappers per mission phase (brief/recon/plan/
  execute/debrief) plus `00_preflight.py`, `run_mission.py`,
  `generate_figures.py`, `z_generate_manuscript_variables.py`.
- **Tests**: per-module real-data tests + mission end-to-end + manuscript
  cross-ref gate + figure + subprocess script smoke. Live counts in
  `docs/_generated/COUNTS.md`.

## Integration points (declared, not yet bound)

- **Gadget payloads are opaque callables.** The `GadgetRegistry` stores the
  pure analysers as-is. When `bond-utilities` ships its
  `mission_io.record_provenance_outcome`, the mission `execute` outcome can
  additionally persist through it; the pure core does not need to change.
- **Coordinator binding.** `mission.py` exposes the provider under the stable
  `MissionProvider` name; the `bond-coordinator` /
  `bond-orchestrator` layer can drive it via `bond_api.discovery.load_provider`
  with no further work.
- **Manuscript rendering.** The numbered sections are hydrated to
  `output/manuscript/`; wiring into the suite's Pandoc PDF pipeline is a
  follow-up shared with the other films.

## Verification

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format src/ scripts/ tests/
uv run mypy src/ scripts/
rg -n "template[_]code_project" .   # expectation: zero
```
