# TODO — LIVE AND LET DIE / SAN MONIQUE

Build status and declared integration points. This file reflects what was built
and what is intentionally deferred.

## Built — Phase 2 (baseline)

- **Pure domain core** (3 modules, importable without bond-api):
  - `supply_graph.py` — shortest paths, Edmonds-Karp max-flow/min-cut, edge- and
    node-level disruption, canonical San Monique graph + `analyze_san_monique()`.
  - `coded_comms.py` — keyword (symbol-substitution) cipher, encipher/decipher,
    frequency tables, frequency-attack solver, cosine scoring, glyph roster.
  - `island_ops.py` — terrain grid, 4-neighbour Dijkstra routing,
    crocodile-exposure hazard metric.
- **Mission adapter** (`mission.py`): FROZEN BOND-API `MissionProvider` (film
  `live_and_let_die`, codename `SAN MONIQUE`), deterministic provenance (seed 8,
  SHA-256 input hash), gadget registration.
- **Figures / manuscript / CLIs / tests**: `figures/plots.py` (supply graph +
  island route), manuscript token hydration, per-phase thin CLIs, real-data
  tests, metadata sidecars.

## Built — Phase 4 (deep improvement)

Three new tested algorithm modules (all pure, deterministic, importable without
bond-api) plus wiring, figures, manuscript, and tests:

- `interdiction.py` — **budgeted network interdiction**: greedy + exact
  (exhaustive) solvers over max-flow impact and an efficiency target list.
  Canonical result: 3-leg plan collapses the 220-unit operation.
- `voodoo_drums.py` — **voodoo drum-code signaling**: Morse-style rhythm codec
  over a per-beat grid, strict run-length decode, rhythm signature + distance.
- `market_flow.py` — **market-flow economics**: per-leg price markup/purity
  dilution, producer share (1.7%), price-spread ratio, gross revenue.
- `mission.py` now reports `interdiction` / `drums` / `market` in `execute()`
  results and registers three new gadgets; the protocol surface
  (brief/recon/plan/execute/debrief, film/codename, `register_gadgets`,
  `GADGET_REGISTRY`) is **unchanged**.
- `manuscript_variables.py`: ~28 new `LALD_*` tokens for the deepened metrics.
- `figures/plots.py`: new `render_interdiction_curve` (reduction vs budget).
- `references.bib`: Wood (1993) interdiction, Morse signal code, Reuter &
  Kleiman (1986), Caulkins & Reuter (2010).

## Integration points (declared, not yet bound)

- **Gadget payloads are opaque callables.** When `bond-utilities` ships
  `mission_io.record_provenance_outcome`, the mission `execute` outcome can
  additionally persist through it; the pure core does not need to change.
- **Coordinator binding.** `mission.py` exposes the provider under the stable
  `MissionProvider` name; `bond-coordinator` / `bond-orchestrator` drive it via
  `bond_api.discovery.load_provider` with no further work.
- **Manuscript rendering.** Sections hydrate to `output/manuscript/`; wiring into
  the suite's Pandoc PDF pipeline is a shared follow-up.

## Verification

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format src/ scripts/ tests/
uv run mypy src/ scripts/
rg -n "template[_]code_project" .   # expectation: zero
```
