# Architecture — LIVE AND LET DIE / SAN MONIQUE

How `src/live_and_let_die/` is organised, what each module computes, and how the
film plugs into the frozen BOND-API protocol.

## Layer contract

Dependency direction is strictly downward. Nothing in the pure core knows that
`bond_api` — or this package's own manuscript — exists.

```
┌─────────────────────────────────────────────────────────────────────┐
│ scripts/  thin orchestrators only                                   │
│   00_preflight · brief · recon · plan · execute · debrief           │
│   run_mission · generate_figures · z_generate_manuscript_variables  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│ mission.py — the ONLY module that imports bond_api                  │
│   implements the frozen MissionProvider · owns GADGET_REGISTRY      │
│   computes the provenance seed + canonical SHA-256 input hash       │
└──────┬───────────────────────────────────────┬──────────────────────┘
       │                                       │
┌──────▼──────────────────┐   ┌────────────────▼────────────────┐
│ manuscript_variables.py │   │ figures/plots.py                │
│  reads manuscript/      │   │  supply graph · interdiction    │
│  config.yaml, computes  │   │  curve · island route           │
│  every {{TOKEN}}        │   │  (matplotlib, Agg, deterministic)│
└──────┬──────────────────┘   └────────────────┬────────────────┘
       │                                       │
   ┌───▼───────────────────────────────────────▼─────────────────────┐
   │ PURE DOMAIN CORE — stdlib only, no bond_api, no infrastructure.*│
   │   supply_graph.py   interdiction.py   coded_comms.py            │
   │   voodoo_drums.py   market_flow.py    island_ops.py             │
   └─────────────────────────────────────────────────────────────────┘
```

The pure core is importable in isolation: `python -c "import sys;
sys.path.insert(0,'src'); import live_and_let_die.supply_graph"` succeeds with
`bond_api` uninstalled. That property is what lets the algorithms be tested,
cited, and reused independently of the suite.

## The six domain modules

### `supply_graph.py` — the substrate

The narcotics chain as a directed, weighted, capacity-constrained graph.
Everything else in the package is built on it.

- `Node` / `Edge` — frozen, self-validating dataclasses. Nodes are classified
  `production` / `transit` / `market`; edges carry a unit cost and a capacity.
- `SupplyGraph.shortest_path` — Dijkstra with `(cost, node_id)` heap keys, so
  ties break deterministically. Raises on an unreachable target.
- `SupplyGraph.max_flow` — Edmonds-Karp (BFS augmenting paths) over a residual
  network built fresh per call.
- `SupplyGraph.min_cut` — the residual-reachable set after max flow; returns the
  cut value and the original-graph edges crossing it.
- `SupplyGraph.disruption` / `node_disruption` / `critical_node` — throughput
  lost when a leg or an asset is neutralised, and which *transit* asset costs
  the most (production and market nodes are not severable targets).
- `SAN_MONIQUE_GRAPH`, `SAN_MONIQUE_DEMAND`, `analyze_san_monique()` — the
  canonical dataset and the packaged analysis every downstream number derives
  from.

### `interdiction.py` — campaign planning on top of the graph

Deterministic budgeted network interdiction: with a budget of `B` legs severable
in one coordinated strike, which set costs the enemy the most throughput?

- `canonical_flow_graph()` — the network wrapped with a super-source bounded by
  crop capacity and a super-sink bounded by market demand, leaving the real
  transit legs severable.
- `greedy_interdiction` — myopic: repeatedly sever the leg with the largest
  marginal drop. Ties break on sorted leg order.
- `exact_interdiction` — exhaustive enumeration of leg subsets; the correctness
  reference that bounds the greedy heuristic from above.
- `efficiency_ranking` — each candidate leg's *independent* impact, ranked: the
  target list.
- `InterdictionPlan` — frozen result (severed legs, marginal gains, cumulative
  reduction, remaining flow, cost-effectiveness).

### `coded_comms.py` — the written cipher

The voodoo "symbol substitution" as what it actually is: a monoalphabetic
keyword cipher.

- `build_keyword_key` — keyword seeds a reshuffled cipher alphabet (duplicates
  dropped, remainder appended); `invert_key` rejects a non-bijective mapping.
- `encipher` / `decipher` — letter-wise substitution; non-letters pass through.
- `frequency_table` / `score_plaintext` — observed letter frequencies and their
  cosine similarity against `ENGLISH_FREQUENCIES`.
- `solve_substitution` — the unkeyed fallback: rank ciphertext symbols by
  frequency, match against reference-ranked English letters, score the candidate.
- `symbol_roster` — the deterministic glyph roster, verified bijective.

### `voodoo_drums.py` — the rhythm channel

The cult's drums treated as a real signalling channel, on normative
International Morse timing ratios (ITU-R M.1677-1).

- `encode_morse` / `signal_for_text` — message to a per-beat `0/1` grid
  (dot = 1 sounding beat, dash = 3; gaps 1 / 3 / 7 for intra-letter, letter, word).
- `decode_signal` — strict run-length decode; an out-of-spec run is an error,
  not a best guess, so a round-trip failure cannot pass silently.
- `rhythm_signature` / `signature_distance` — density and run statistics that
  make two intercepted transmissions numerically comparable.
- `drum_report()` — the canonical transmission plus its verified round-trip.

### `market_flow.py` — the money

Price and purity propagation along the same legs that carry volume.

- `EDGE_ECONOMICS` — per-leg markup multiplier and purity dilution factor.
- `node_prices` — price/purity at each node along its cheapest path from the
  farm gate (by arbitrage, the lowest-cost channel sets the price). Raises on a
  leg with no defined economics rather than silently skipping it.
- `market_flow_report()` — street price/purity per market, demand-weighted
  average, **producer share**, price-spread ratio, and gross revenue.

### `island_ops.py` — the ground

The island as a weighted terrain grid, and the infiltration route across it.

- `TerrainGrid` — validated rectangular grid (equal row lengths, known glyphs);
  `TERRAIN_COSTS` gives per-cell movement cost, with `X` impassable.
- `plan_route` — Dijkstra over the four cardinal neighbours, deterministic
  `(cost, row, col)` keys; raises on out-of-bounds, untraversable, or
  unreachable endpoints.
- `crocodile_exposure` — the hazard metric: how many crocodile-water cells the
  route wades.
- `SAN_MONIQUE_TERRAIN`, `ROUTE_START`, `ROUTE_GOAL`, `plan_san_monique_route()`
  — the canonical island and its infiltration problem.

## How `mission.py` implements the frozen `MissionProvider`

`mission.py` is the *only* module that imports `bond_api`. It is an adapter: it
holds no algorithms, and every value it reports is computed by the pure core.

**Discovery contract.** `bond_api.discovery` finds a film package by importing a
top-level module named for its slug and reading `MissionProvider` off it. So
`MissionProvider` must stay a module-level name in `live_and_let_die.mission`,
and `MissionProvider.film` must equal `"live_and_let_die"`.

**Structural typing.** `bond_api.protocol.MissionProvider` is a `Protocol`, so
this class does not inherit from it — it satisfies it by shape. `scripts/00_preflight.py`
asserts that with a runtime `isinstance` check against the protocol, which is
what catches an accidental signature change.

| Protocol method | What this film does | Returns |
| --- | --- | --- |
| `brief()` | Declares the mission: objectives, the three canonical datasets as `Asset`s (graph, communiqué, terrain), and the `determinism` / `no-mocks` `Constraint`s. Asset payloads are **derived** from `SAN_MONIQUE_GRAPH`, never typed. | `MissionBrief` |
| `recon(request)` | Surveys ground truth: the request goal, the market node ids, the live graph size, the terrain obstacle, and the execution constraints. | `ReconReport` of `Finding`s |
| `plan(brief)` | Schedules four deterministic `Step`s — supply, comms, ops, and a combining report step — parameterised from the brief's objectives. | `MissionPlan` |
| `execute(plan)` | Calls `run_analysis()` (all six analyses merged) and stamps `Provenance`: package version, seed `MISSION_SEED = 8`, the canonical `input_digest()`, and `wall_time_s = 0.0` so no artifact carries a clock. | `MissionOutcome` |
| `debrief(outcome)` | Distils the outcome into actionable lessons, each interpolated from computed values (bottleneck, strike reduction, producer share, crocodile exposure). | `Debrief` |

**Provenance.** `_canonical_inputs()` serialises every analysis input in a
canonical, order-stable form — sorted graph legs with weights and capacities, the
cipher keyword and plaintext, the terrain rows, the route endpoints, the sorted
per-leg economics, and the drum message — and `input_digest()` is its SHA-256.
Any change to any input moves the hash, so an audited outcome can be tied back to
exactly the data that produced it.

**Gadgets.** `GADGET_REGISTRY` is a module-level `bond_api.registry.GadgetRegistry`,
populated at import time by `register_gadgets()`. It maps six names —
`supply_graph_analyzer`, `communique_decipher`, `island_route_planner`,
`interdiction_planner`, `drum_traffic_reporter`, `market_flow_reporter` — to the
pure-domain callables, so a coordinator can invoke any single analyser without
running a full mission. `register_gadgets(registry)` also accepts an external
registry, which is how a coordinator merges the whole fleet into one namespace.

## Supporting modules

- `manuscript_variables.py` — reads `manuscript/config.yaml`, runs the domain
  core, and returns the `{{TOKEN}}` map; `resolve_manuscript_tree` copies the
  numbered sections to `output/manuscript/` with tokens substituted, failing in
  strict mode on any unresolved token. `domain_modules()` discovers the pure-core
  module list from the package directory, so counts quoted in the manuscript
  cannot drift from the tree.
- `figures/plots.py` — three deterministic matplotlib figures (`Agg` backend
  forced at import). Captions interpolate computed values rather than naming
  them literally.
- `scripts/` — thin orchestrators. `sys.path` bootstrap, one call into `src/`,
  print the result, `raise SystemExit(main())`. No business logic, and no bare
  `assert` used as a gate.

## The dependency rule, restated

The six domain modules import stdlib only. `figures/plots.py` adds matplotlib and
numpy; `manuscript_variables.py` adds PyYAML. `mission.py` is where — and the
only place where — protocol coupling lives. If you find yourself importing
`bond_api` into a domain module, the design has gone wrong.
