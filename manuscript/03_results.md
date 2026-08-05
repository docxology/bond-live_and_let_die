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
capped by destination-market demand. The min cut is {{LALD_MIN_CUT_EDGES}} —
both virtual demand edges, {{LALD_MIN_CUT_PHYSICAL_COUNT}} physical legs — so
the network is {{LALD_MIN_CUT_LIMIT}} and the cut is a bound, not a target list.

The production flow into {{LALD_MARKETS}} is nonetheless sharply exposed to a
single asset. Probing the same demand-capped model node by node, the most
critical transit node is the **{{LALD_BOTTLENECK}}**: neutralizing it removes
{{LALD_DISRUPTION}} of the {{LALD_MAX_FLOW}} units the network moves — the
highest-value single interdiction on the island.

![The San Monique supply network: cheapest production-to-Miami route and the
critical transit node highlighted.]({{LALD_FIGURE_DIR}}/supply_graph.png)

## Interdiction

Against a base flow of {{LALD_BASE_FLOW}} units, a coordinated strike plan is
frighteningly effective. The greedy plan severs
{{LALD_GREEDY_SEVERED}} for a simultaneous {{LALD_GREEDY_REDUCTION}}-unit
reduction (cost-effectiveness {{LALD_GREEDY_CE}} units per leg, leaving
{{LALD_REMAINING_FLOW}}); the exhaustive optimum severs {{LALD_EXACT_SEVERED}}
for the same {{LALD_EXACT_REDUCTION}}-unit total — the entire operation
collapses. The single most valuable leg on the target list is
{{LALD_EFFICIENCY_TOP_LEG}} ({{LALD_EFFICIENCY_TOP_DROP}} units alone).

![Greedy versus exhaustive-optimal throughput reduction across strike
budgets.]({{LALD_FIGURE_DIR}}/interdiction_curve.png)

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
producer retains **{{LALD_PRODUCER_SHARE}}** of the street value. Across
{{LALD_MARKET_COUNT}} markets the operation grosses about
{{LALD_TOTAL_REVENUE}} $. These are outputs of invented parameters, not
measurements: they establish that multiplicative per-leg markups compress the
producer's share, and nothing about the size of that share in any real market.

## Infiltration route

The terrain planner routes an agent from the south landing beach
({{LALD_ROUTE_START}}) to the airfield zone ({{LALD_ROUTE_GOAL}}) in
{{LALD_ROUTE_MOVES}} moves at total cost {{LALD_ROUTE_COST}}, crossing
{{LALD_CROCODILE_CELLS}} crocodile-water cells.

The exposure-minimising search puts the floor over *all* routes at
{{LALD_MIN_CROCODILE_CELLS}} cells: the channel is walled by impassable cliff on
both flanks, so no overland approach to the airfield — at any movement cost —
wades fewer than {{LALD_MIN_CROCODILE_CELLS}}. The cheapest route achieves that
floor exactly.

![The terrain grid with the planned infiltration route
overlaid.]({{LALD_FIGURE_DIR}}/island_route.png)
