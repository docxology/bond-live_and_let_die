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

## Coded-communiqué deciphering

The voodoo "symbol substitution" is a monoalphabetic keyword cipher over the
26-letter alphabet: a keyword (here {{LALD_KEYWORD}}) seeds a reshuffled cipher
alphabet (duplicates dropped, remaining letters appended), and each plaintext
letter maps to the cipher symbol at its index. Enciphering and deciphering are
pure dictionary lookups. To handle an *unkeyed* intercept, `solve_substitution`
performs a frequency attack: ciphertext symbols are ranked by observed
frequency and matched to reference English letters ranked by expected
frequency; the candidate plaintext is scored by the cosine similarity of its
frequency profile against the reference distribution.

## Island ops planning

San Monique is discretized as a terrain grid where each cell is a terrain type
with a movement cost (road/open/beach cost 1, mangrove 3, open water 3, swamp 5,
crocodile water 7, impassable cliff infinite). Dijkstra over the four cardinal
neighbours finds the lowest-cost route between the landing beach and the
airfield zone; the planner reports total cost, the path, and the number of
crocodile-water cells traversed as a hazard metric.
