# src — pure domain core + thin adapter

`src/live_and_let_die/` is the importable package. The three pure modules carry
all business logic and the film's canonical datasets; `mission.py` is the thin
BOND-API protocol adapter; `manuscript_variables.py` hydrates tokens.

| Module | Responsibility |
| --- | --- |
| `supply_graph.py` | Supply-graph analytics: Dijkstra, Edmonds-Karp max-flow, min-cut, disruption; `SAN_MONIQUE_GRAPH` + `analyze_san_monique()` |
| `coded_comms.py` | Keyword substitution cipher, encipher/decipher, frequency analysis, solver, glyph roster |
| `island_ops.py` | Terrain grid + 4-neighbour Dijkstra routing, crocodile exposure |
| `mission.py` | `MissionProvider` (SABLE-style reference shape) + gadget registration + `run_analysis` |
| `manuscript_variables.py` | `generate_variables` / `resolve_manuscript_tree` |
| `figures/plots.py` | Deterministic matplotlib figures (supply graph, island route) |

Dependency rule: the three pure modules import only stdlib; only `mission.py`
and `manuscript_variables.py` touch the protocol/config surface. No
`infrastructure.*` anywhere.
