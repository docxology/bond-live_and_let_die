# AGENTS.md — LIVE AND LET DIE / SAN MONIQUE

This is a PROJECT BOND film package (codename **SAN MONIQUE**) implementing the
FROZEN BOND-API mission protocol over a pure, deterministic domain core.

## Layer contract

- `src/live_and_let_die/supply_graph.py`, `coded_comms.py`, `island_ops.py` are
  **pure**: no `infrastructure.*` and no `bond_api` imports — importable in
  isolation (stdlib + numpy only in practice).
- `src/live_and_let_die/mission.py` is the **thin protocol adapter**: it imports
  `bond_api.protocol` / `bond_api.registry` and the pure core, and implements
  the `MissionProvider` contract.
- `src/live_and_let_die/manuscript_variables.py` hydrates manuscript tokens from
  `manuscript/config.yaml` + the pure core.
- `scripts/` are thin orchestrators only.

## Protocol integration

Add the local path dependency so bond-api is importable (already done):

```yaml
[tool.uv.sources]
bond-api = { path = "/Users/4d/Documents/GitHub/template/projects/working/bond/bond-api" }
```

`src/live_and_let_die/mission.py` exposes `MissionProvider` at module top level
(film `live_and_let_die`, codename `SAN MONIQUE`) and registers gadgets
(`supply_graph_analyzer`, `communique_decipher`, `island_route_planner`) with
the `bond_api.GadgetRegistry`. The orchestrator discovers it by slug on
`sys.path`.

## Behavior notes

- Deterministic: fixed provenance seed 8, zero wall-clock in artifacts, canonical
  SHA-256 input hash. No random draws anywhere.
- No mock framework: tests use real data + computation only.
- Do not change the FROZEN bond-api protocol types — code against them.

## Reading order for agents

1. `docs/agent_instructions.md` — operational constraints & verification.
2. `docs/architecture.md` — module boundaries.
3. `docs/testing_philosophy.md` — how tests are written here.
4. `manuscript/SYNTAX.md` — manuscript token conventions.
