# Scope and Related Work

This package is one film in the PROJECT BOND suite of 33 packages: 27 film
packages implementing a shared, FROZEN mission protocol
(`bond_api.MissionProvider`) over pure domain cores, plus six infrastructure
packages (api, utilities, coordinator, orchestrator, cli, ops). It is a local
working exemplar developed from the template computing-project scaffold — lineage
is documented, not reproduced as source.

The analytical techniques are classical and deliberately textbook-grade,
spanning three research literatures:

- **Max-flow / min-cut and network interdiction.** Edmonds-Karp with the
  residual-cut theorem underpins bottleneck and single-point-of-failure
  analysis. The budgeted interdiction problem — minimize remaining throughput
  given a fixed number of removed legs — follows Wood's deterministic network
  interdiction formulation; the greedy and exhaustive solvers here are
  self-contained (`wood1993`).
- **Coded communications.** Monoalphabetic keyword substitution with a
  frequency-attack solver (`stinson2019`) sits beside the drum code, a
  rhythm codec over a per-beat grid whose element and gap durations follow the
  normative International Morse timing ratios (`itu2009`) — a numerical
  treatment of the Caribbean drum telegraphy the film uses.
- **Narcotics market economics.** The farm-gate-to-street price and purity
  model, and its headline producer-share finding, follow the economic analysis
  of drug enforcement prices of Reuter & Kleiman and Caulkins & Reuter
  (`reuter1986`, `caulkins2010`).
- **Terrain pathfinding.** Grid Dijkstra is the standard cost-minimising planner
  for rasterized maps, applied to a hazard-labelled island.

The novel contribution is not the algorithms but their unification:
{{LALD_MODULE_COUNT}} film concepts, {{LALD_MODULE_COUNT}} pure modules exposed
as {{LALD_GADGET_COUNT}} named gadgets, one frozen mission protocol, one
provenance chain — reproducible end to end with no mocks and no external
services.
