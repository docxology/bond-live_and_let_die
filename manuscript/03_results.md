# Results

All figures below are deterministic and regenerable from the source tree.

## Supply graph

The canonical San Monique network has {{LALD_SUPPLY_NODES}} nodes and
{{LALD_SUPPLY_EDGES}} legs. The cheapest production-to-market routes are:

| Destination | Cost | Route |
| --- | --- | --- |
| Miami | {{LALD_SHORTEST_MIAMI}} | {{LALD_SHORTEST_MIAMI_PATH}} |
| New York | {{LALD_SHORTEST_NYC}} | {{LALD_SHORTEST_NYC_PATH}} |

Total maximum throughput is {{LALD_MAX_FLOW}} units ({{LALD_MIN_CUT}} bound),
capped by destination-market demand. The same production flow into
{{LALD_MARKETS}} is, however, sharply exposed to a single asset: the most
critical transit node is the **{{LALD_BOTTLENECK}}**, and neutralizing it cuts
{{LALD_DISRUPTION}} units of Miami throughput — the highest-value single
interdiction on the island.

## Interdiction

Against a base flow of {{LALD_BASE_FLOW}} units, a coordinated strike plan is
frighteningly effective. The greedy plan severs
{{LALD_GREEDY_SEVERED}} for a simultaneous {{LALD_GREEDY_REDUCTION}}-unit
reduction (cost-effectiveness {{LALD_GREEDY_CE}} units per leg, leaving
{{LALD_REMAINING_FLOW}}); the exhaustive optimum severs {{LALD_EXACT_SEVERED}}
for the same {{LALD_EXACT_REDUCTION}}-unit total — the entire operation
collapses. The single most valuable leg on the target list is
{{LALD_EFFICIENCY_TOP_LEG}} ({{LALD_EFFICIENCY_TOP_DROP}} units alone). Figure
`interdiction_curve` shows the trade-off across budgets.

## Communiqués

The intercepted voodoo communiqué deciphers under the keyword substitution
({{LALD_KEYWORD}}) to:

> {{LALD_PLAINTEXT}}

The ciphertext after encipherment is `{{LALD_CIPHERTEXT}}`.

The cult's drums carry a {{LALD_DRUM_BEATS}}-beat message that decodes exactly
(density {{LALD_DRUM_DENSITY}}, longest run {{LALD_DRUM_LONGEST}}) to:

> {{LALD_DRUM_MESSAGE}}

(decoding verified **{{LALD_DRUM_ROUNDTRIP}}**).

## Market economics

From a farm-gate price of {{LALD_FARM_GATE_PRICE}} $/kg, street-level prices
reach {{LALD_MIAMI_STREET_PRICE}} $/kg at {{LALD_MIAMI_STREET_PURITY}} purity in
Miami and {{LALD_NYC_STREET_PRICE}} $/kg at {{LALD_NYC_STREET_PURITY}} purity in
New York. The demand-weighted average street price is {{LALD_AVG_STREET_PRICE}}
$/kg — a {{LALD_SPREAD_RATIO}}× farm-gate-to-street spread — and the farm-gate
producer retains only **{{LALD_PRODUCER_SHARE}}** of the street value. Across
{{LALD_MARKET_COUNT}} markets the operation grosses about
{{LALD_TOTAL_REVENUE}} $.

## Infiltration route

The terrain planner routes an agent from the south landing beach
({{LALD_ROUTE_START}}) to the airfield zone ({{LALD_ROUTE_GOAL}}) in
{{LALD_ROUTE_MOVES}} moves at total cost {{LALD_ROUTE_COST}}, crossing
{{LALD_CROCODILE_CELLS}} crocodile-water cells. Because the channel is walled by
impassable cliff on both flanks, any overland approach must wade the crocodile
water.
