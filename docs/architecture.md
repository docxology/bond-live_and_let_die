# Architecture — LIVE AND LET DIE / SAN MONIQUE

## Layer contract

```
┌────────────────────────────────────────────────────────────────┐
│ scripts/  (thin orchestrators: brief/recon/plan/execute/debrief,
│           run_mission, generate_figures, z_generate_manuscript) │
└───────────────────────────────┬────────────────────────────────┘
                                │
┌───────────────────────────────▼────────────────────────────────┐
│ mission.py  (thin protocol adapter)                            │
│   bonds bond_api.MissionProvider + GadgetRegistry to the core  │
│   provides provenance seed + input hash                        │
└───────┬───────────────────────────────┬────────────────────────┘
        │                               │
┌───────▼──────────┐     ┌──────────────▼──────────────┐
│ manuscript_      │     │ figures/plots.py            │
│ variables.py     │     │  supply graph + island route│
│ (token hydration)│     └──────────────┬──────────────┘
└───────┬──────────┘                    │
        │                               │
    ┌───▼───────────────────────────────▼───┐
    │ PURE DOMAIN CORE (no bond_api/infra)  │
    │  supply_graph.py · coded_comms.py     │
    │  island_ops.py                        │
    └───────────────────────────────────────┘
```

## Module responsibilities

- `supply_graph.py` — graph analytics. `SupplyGraph` (Dijkstra, Edmonds-Karp
  max-flow, residual min-cut, disruption), canonical `SAN_MONIQUE_GRAPH`, and
  `analyze_san_monique()`.
- `coded_comms.py` — cipher machinery. Keyword key construction, encipher/
  decipher, frequency tables, frequency-attack solver, cosine scoring, glyph
  roster.
- `island_ops.py` — terrain planning. `TerrainGrid` (weighted grid, 4-neighbour
  Dijkstra, crocodile exposure), canonical `SAN_MONIQUE_TERRAIN`.
- `mission.py` — the `MissionProvider` adapter; registers gadgets, computes
  results + provenance (`run_analysis`).
- `manuscript_variables.py` — reads `manuscript/config.yaml`, computes every
  `{{TOKEN}}` from the core, resolves the numbered sections.
- `figures/plots.py` — deterministic matplotlib figures.

## Dependency rule

The three pure modules import only stdlib (plus numpy in figures). They never
import `infrastructure.*` or `bond_api`; `mission.py` /
`manuscript_variables.py` are where protocol and config coupling lives.
