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
- **Narcotics market economics.** The *question* — who captures the value
  between farm gate and street, and what that implies for enforcement — is the
  one posed by Reuter & Kleiman and by Caulkins & Reuter (`reuter1986`,
  `caulkins2010`). The *parameters* are not theirs and are not anyone's data:
  the farm-gate price, the retail markup and dilution, and all ten per-leg
  markup/dilution pairs in `EDGE_ECONOMICS` were chosen for this fictional
  scenario. Nothing here estimates, calibrates against, or reproduces a
  published figure, and the producer share reported in §Results should not be
  read as agreeing or disagreeing with any empirical estimate. The model
  contributes a mechanism — multiplicative per-leg markups compress the
  producer's share — exercised on invented numbers.
- **Terrain pathfinding.** Grid Dijkstra is the standard cost-minimising planner
  for rasterized maps, applied to a hazard-labelled island.

The novel contribution is not the algorithms but their unification:
{{LALD_MODULE_COUNT}} film concepts, {{LALD_MODULE_COUNT}} pure modules exposed
as {{LALD_GADGET_COUNT}} named gadgets, one frozen mission protocol, one
provenance chain — reproducible end to end with no mocks and no external
services.


## Limitations and uncertainty

The analytical machinery is exact and deterministic (integer-capacity graphs,
closed-form economics, fixed terrain), so it carries no sampling error — but
that precision is not accuracy. Every headline number in §Results inherits the
uncertainty of the *inputs* it is computed from, which are assumptions, not
measurements:

- **Supply-graph capacities, crop ceilings, and demand ceilings** are invented
  scale figures for the fictional scenario. The throughput ({{LALD_MAX_FLOW}})
  and disruption ({{LALD_DISRUPTION}}) figures are exact arithmetic on those
  chosen numbers; changing any capacity changes both. The analysis establishes
  *structure* — the network is demand-limited, hinges on one transit asset —
  not a measured magnitude.
- **Economic parameters** (farm-gate price, retail markup/dilution, all ten
  per-leg markup/dilution pairs) are invented. The producer share
  ({{LALD_PRODUCER_SHARE}}) and the price spread ({{LALD_SPREAD_RATIO}}×) are
  the exact reciprocals of chosen products of markups; re-run the model under
  different parameters and they move exactly as the assumptions dictate. The
  test suite binds this as sensitivity, not as a confidence interval, because
  there is no sampling distribution to quantify — only the chosen inputs.
- **Interdiction** greedy-vs-optimal: the greedy and exhaustive solvers agree
  at {{LALD_BUDGET}}-leg reduction here ({{LALD_GREEDY_REDUCTION}} /
  {{LALD_EXACT_REDUCTION}}), but greedy is a heuristic and its optimality is
  *not* guaranteed in general. On this instance the exhaustive optimum
  confirms the greedy plan is exact — that is evidence for this graph, not a
  general bound.
- **Terrain costs** are unit figures chosen for the scenario; the route cost
  ({{LALD_ROUTE_COST}}) and crocodile exposure ({{LALD_CROCODILE_CELLS}}) are
  exact on those costs. The universal claim (any route wades at least
  {{LALD_MIN_CROCODILE_CELLS}}) is a structural fact of the committed grid
  (impassable cliff walls), so it is robust to the cost *numbers*, though it
  does depend on the grid topology being the island's.

In short: the package's contribution is deterministic, reproducible
computation over explicitly declared assumptions. Figures are recomputable to
the last unit, but they should be read as "exact given these invented
parameters", never as empirical estimates. This is the honest scope of the
whole suite, and it is enforced by the test gates rather than stated once.
