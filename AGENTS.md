# AGENTS.md — LIVE AND LET DIE / SAN MONIQUE

This is a PROJECT BOND film package (codename **SAN MONIQUE**) implementing the
FROZEN BOND-API mission protocol over a pure, deterministic domain core. It has
been deepened across phases; the protocol surface is stable.

## Layer contract

- Pure core (`supply_graph.py`, `coded_comms.py`, `island_ops.py`,
  `interdiction.py`, `voodoo_drums.py`, `market_flow.py`): no
  `infrastructure.*` and no `bond_api` imports — importable in isolation.
- `mission.py` is the **thin protocol adapter**: it imports `bond_api.protocol` /
  `bond_api.registry` and the pure core, and implements `MissionProvider`.
- `manuscript_variables.py` hydrates manuscript tokens from
  `manuscript/config.yaml` + the pure core.
- `figures/plots.py` renders deterministic figures.
- `scripts/` are thin orchestrators only.

## Protocol stability

`src/live_and_let_die/mission.py` exposes `MissionProvider` (film
`live_and_let_die`, codename `SAN MONIQUE`) at module top level with
`brief`/`recon`/`plan`/`execute`/`debrief` plus the `GADGET_REGISTRY` and
`register_gadgets(registry=None)` hook. **Do not change this public shape** —
bond-cli, the coordinator reconcile, and the orchestrator consume it across
packages. Deepen inside the package (new modules, richer `execute` internals),
never by breaking discovery.

## Behavior notes

- Deterministic: fixed provenance seed 8, zero wall-clock in artifacts, canonical
  SHA-256 input hash (now covering graph, ciphers, drum message, and per-leg
  economics). No random draws anywhere.
- No mock framework: tests use real data + computation only.
- Do not change the FROZEN bond-api protocol types — code against them.

## Reading order for agents

1. `docs/agent_instructions.md` — operational constraints & verification.
2. `docs/architecture.md` — module boundaries.
3. `docs/testing_philosophy.md` — how tests are written here.
4. `manuscript/SYNTAX.md` — manuscript token conventions.
