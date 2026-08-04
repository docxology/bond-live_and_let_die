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

## Communiqué

The intercepted voodoo communiqué deciphers under the keyword substitution
({{LALD_KEYWORD}}) to:

> {{LALD_PLAINTEXT}}

The ciphertext after encipherment is `{{LALD_CIPHERTEXT}}`.

## Infiltration route

The terrain planner routes an agent from the south landing beach
({{LALD_ROUTE_START}}) to the airfield zone ({{LALD_ROUTE_GOAL}}) in
{{LALD_ROUTE_MOVES}} moves at total cost {{LALD_ROUTE_COST}}, crossing
{{LALD_CROCODILE_CELLS}} crocodile-water cells. Because the channel is walled by
impassable cliff on both flanks, any overland approach must wade the crocodile
water.
