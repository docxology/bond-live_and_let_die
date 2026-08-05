# AGENTS.md — src

- **Pure core** (`supply_graph.py`, `coded_comms.py`, `island_ops.py`,
  `interdiction.py`, `voodoo_drums.py`, `market_flow.py`): no
  `infrastructure.*`, no `bond_api` imports — importable standalone.
- **Adapter** (`mission.py`): implements the FROZEN `bond_api.MissionProvider`;
  register gadgets on `bond_api.GadgetRegistry`; deterministic provenance
  (seed 8, SHA-256 input hash).
- **Manuscript** (`manuscript_variables.py`): metrics always computed from the
  core, never hand-authored in prose.
- Every public function is type-hinted and docstringed; rub the gates
  (see `docs/agent_instructions.md`).
