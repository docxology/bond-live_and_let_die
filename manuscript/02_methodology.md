# Methodology

## Supply-graph analytics

The San Monique operation is represented as a directed, weighted,
capacity-constrained graph `G = (V, E)`. Vertices are classified as
`production` (interior poppy fields, field processing works), `transit`
(airfield, harbor, smuggler's cove), or `market` (Miami, New York). Each edge
carries a unit cost (money, risk, time) and a throughput capacity (units per
reporting period).

- **Cheapest route.** Dijkstra's algorithm returns the minimal total cost and
  ordered node sequence from a production source to each market. Deterministic
  tie-breaking uses `(cost, node_id)` heap keys.
- **Maximum throughput.** Edmonds-Karp (BFS augmenting path) computes the
  maximum flow that can be pushed from a virtual super-source
  ({{LALD_SUPPLY_SOURCE}}) through the network to a virtual super-sink
  ({{LALD_SUPPLY_SINK}}). Production nodes are bounded by their crop capacity
  and markets by their demand ceilings.
- **Bottleneck.** The minimum cut (the set of forward edges leaving the
  residual-reachable set after max-flow) bounds throughput. A per-transit-node
  disruption probe re-computes flow after neutralizing each transit asset and
  reports the one whose loss costs the most — the highest-value interdiction
  target.

## Budgeted network interdiction

Beyond a single bottleneck, the operation asks *how much of the network can be
taken down with a limited strike budget*. This is the deterministic network
interdiction problem: with a budget `B` of transit legs that can be severed in
one coordinated operation, choose the legs that cost the enemy the most
throughput. Two solvers are provided:

- **Greedy** — myopically sever the leg with the largest marginal throughput
  drop, then repeat; deterministic tie-breaking on leg order.
- **Exact** — exhaustive enumeration of all `B`-subsets of severable legs
  (feasible at this scale) that maximises reduction; it is the correctness
  reference for the greedy heuristic.
- **Efficiency ranking** — each leg's *independent* throughput impact, ranked,
  forming the target list.

## Coded communiqués: symbol substitution and drum code

The voodoo "symbol substitution" is a monoalphabetic keyword cipher over the
{{LALD_ALPHABET_SIZE}}-letter alphabet: a keyword (here {{LALD_KEYWORD}}) seeds a reshuffled cipher
alphabet (duplicates dropped, remaining letters appended), and each plaintext
letter maps to the cipher symbol at its index. To handle an *unkeyed* intercept,
`solve_substitution` performs a frequency attack: ciphertext symbols are ranked
by observed frequency and matched to reference English letters ranked by
expected frequency; the candidate plaintext is scored by cosine similarity of
its frequency profile against the reference distribution.

Alongside the written cipher, the cult's **drum code** is a Morse-style rhythm
codec over a per-beat `0/1` grid, on standard International Morse timing
({{LALD_DRUM_TIMING}}). `signal_for_text` encodes any
message onto the beat grid and `decode_signal` recovers it exactly under strict
run-length validation. `rhythm_signature` / `signature_distance` give a numeric
traffic signature so two intercepted signals can be compared.

## Market-flow economics

The money side: the same legs that carry volume also mark prices up and dilute
purity from the farm gate ({{LALD_FARM_GATE_PRICE}} $/kg) to the street
({{LALD_MARKET_COUNT}} markets). Price and purity propagate along the cheapest
path (by arbitrage the lowest-cost channel sets the price), and the street stage
applies a retail markup and a purity dilution. The headline metric is the
**producer share** — the farm-gate value as a fraction of street price — and the
**price-spread ratio**, both driven by the per-leg economics dataset
`EDGE_ECONOMICS`.

## Island ops planning

San Monique is discretized as a {{LALD_TERRAIN_SHAPE}} terrain grid where each
cell is a terrain type with a movement cost ({{LALD_TERRAIN_COSTS}}). Dijkstra over the four cardinal
neighbours finds the lowest-cost route between the landing beach and the
airfield zone; the planner reports total cost, the path, and the number of
crocodile-water cells traversed as a hazard metric.
