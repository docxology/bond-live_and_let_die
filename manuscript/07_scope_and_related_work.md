# Scope and Related Work

This package is one film in the PROJECT BOND suite of 33 packages: 27 film
packages implementing a shared, FROZEN mission protocol
(`bond_api.MissionProvider`) over pure domain cores, plus six infrastructure
packages (api, utilities, coordinator, orchestrator, cli, ops). It is a local
working exemplar developed from the template computing-project scaffold — lineage
is documented, not reproduced as source.

The three analytical techniques are classical and deliberately textbook-grade:

- **Max-flow / min-cut** (Edmonds-Karp, residual-cut theorem) underpins
  bottleneck and single-point-of-failure analysis in transportation and
  network survivability.
- **Monoalphabetic substitution + frequency analysis** is the entry point of
  classical cryptanalysis; the keyword cipher and frequency-attack solver here
  are self-contained and deterministic.
- **Grid Dijkstra / terrain pathfinding** is the standard cost-minimising
  planner for rasterized maps, here applied to a hazard-labelled island.

The novel contribution is not the algorithms but their unification: three film
concepts, three pure modules, one frozen mission protocol, one provenance
chain — reproducible end to end with no mocks and no external services.
