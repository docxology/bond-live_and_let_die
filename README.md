# LIVE AND LET DIE (1973) — SAN MONIQUE

**PROJECT BOND · film package** · mission codename **SAN MONIQUE**

Deterministic special-agent mission software for Kananga's narcotics operation
on the Caribbean island of San Monique, built as one of 27 film packages in the
BOND suite. It implements the FROZEN BOND-API `MissionProvider` protocol over a
pure, infrastructure-free domain core.

## Film → software

*Live and Let Die* gives us a villain who is a head of state by day and a
narcotics baron by night, moving product from an island's interior poppy fields
to American streets, coordinating through voodoo ritual and drum signalling, and
sheltered behind a mangrove coast and a crocodile channel. Every one of those is
a computation problem an analyst would really run:

| Film element | Question it poses | Module that answers it |
| --- | --- | --- |
| Poppy fields → airfield/harbor → Miami/New York | What moves, how cheaply, how much, and what is the single point of failure? | `supply_graph.py` |
| "Take the whole operation down" | Which legs, on a fixed strike budget, cost the enemy the most? | `interdiction.py` |
| Voodoo symbol-coded communiqués | What does the intercept say — with and without the key? | `coded_comms.py` |
| The cult's drums | The drums are a channel: encode, decode, and fingerprint the traffic | `voodoo_drums.py` |
| Kananga's real business | Who captures the value between farm gate and street? | `market_flow.py` |
| Mangrove, swamp, crocodile lagoon | What is the cheapest infiltration route, and what does it cost in exposure? | `island_ops.py` |

## The source tree

Six pure domain modules (stdlib only, no `bond_api`, no `infrastructure.*`),
plus the protocol adapter and two supporting modules:

| Module | What it computes |
| --- | --- |
| `src/live_and_let_die/supply_graph.py` | Directed capacity-constrained supply graph: Dijkstra shortest paths, Edmonds-Karp max-flow, residual min-cut, per-edge and per-node disruption, critical-transit-node selection, and the canonical San Monique dataset |
| `src/live_and_let_die/interdiction.py` | Budgeted network interdiction: greedy and exact (exhaustive) strike-plan solvers over max-flow impact, plus an independent-impact efficiency target list |
| `src/live_and_let_die/coded_comms.py` | Keyword (symbol-substitution) cipher: key construction, encipher/decipher, letter-frequency tables, cosine scoring, an unkeyed frequency-attack solver, and the voodoo glyph roster |
| `src/live_and_let_die/voodoo_drums.py` | Drum-code signalling: Morse-timed rhythm codec over a per-beat grid, strict run-length decode, and rhythm signature/distance for traffic comparison |
| `src/live_and_let_die/market_flow.py` | Farm-gate-to-street economics: per-leg price markup and purity dilution, producer share, price-spread ratio, and gross revenue |
| `src/live_and_let_die/island_ops.py` | Terrain planning: validated weighted grid, 4-neighbour Dijkstra routing, and crocodile-water exposure as a hazard metric |
| `src/live_and_let_die/mission.py` | **The protocol adapter** — the only module importing `bond_api`. Implements `MissionProvider`, owns `GADGET_REGISTRY`, computes the provenance seed and canonical SHA-256 input hash |
| `src/live_and_let_die/manuscript_variables.py` | Hydrates every manuscript `{{TOKEN}}` from `manuscript/config.yaml` + the domain core; resolves sections to `output/manuscript/` |
| `src/live_and_let_die/figures/plots.py` | Three deterministic matplotlib figures: supply graph, interdiction trade-off curve, island route |

## The MissionProvider surface

`src/live_and_let_die/mission.py` exposes, at module top level:

```python
MissionProvider          # film = "live_and_let_die", codename "SAN MONIQUE"
  .brief()      -> MissionBrief     # objectives, datasets as Assets, constraints
  .recon(req)   -> ReconReport      # goal, markets, live graph size, terrain, constraints
  .plan(brief)  -> MissionPlan      # four deterministic steps
  .execute(pl)  -> MissionOutcome   # all six analyses + Provenance(seed, input_hash)
  .debrief(out) -> Debrief          # lessons interpolated from computed values

GADGET_REGISTRY          # six named analysers, registered at import
register_gadgets(registry=None)     # merge them into an external registry
```

This shape is **frozen**: `bond-cli`, `bond-coordinator`, and `bond-orchestrator`
discover and drive it across all 27 film packages. Deepen inside the package,
never by changing what they consume.

## Canonical findings (computed, never hand-authored)

Every number below is produced by the code and reported in the manuscript through
a `{{TOKEN}}`; none is typed into prose. Re-derive them with
`uv run python scripts/execute.py`.

- Supply graph: 7 nodes, 10 legs; cheapest Miami route `poppy_fields -> airfield
  -> miami` (cost 13); max throughput 220 units, min-cut 220; the critical
  transit node is the **airfield** (110 of those 220 units). Throughput and
  disruption are measured on the same demand-capped flow model, so the second
  number is bounded by the first.
- The min cut is `miami -> DEMAND` and `new_york -> DEMAND` — both *virtual*
  demand-ceiling edges, zero physical legs. The network is demand-limited, and
  the cut is a capacity bound that names no severable asset. Targeting comes
  from the per-node disruption probe and the interdiction study, never the cut.
- **Interdiction**: an optimal 3-leg strike plan (greedy 220, exact 220)
  collapses the whole operation; the top target leg `field_works -> harbor` is
  worth 50 units alone.
- The voodoo communiqué deciphers under the BARON keyword to
  *"KANANGA LETS THE SNAKE BITE"*. The unkeyed frequency attack does **not**
  recover it at this length — it returns `IEAEAHE LTON ORT NAEIT SDOT` while
  scoring 0.93 against the English reference, which is why the score is a
  ranking heuristic and not evidence of recovery. The drums carry a 195-beat
  message that decodes exactly to the plaintext.
- **Market economics**: producer share 1.7% of street value, 59×
  farm-gate-to-street spread, ~$3.89M gross revenue. Every economic parameter
  (`FARM_GATE_PRICE`, `RETAIL_MARKUP`, `RETAIL_DILUTION`, all ten
  `EDGE_ECONOMICS` pairs) is **invented for this fictional scenario** — none is
  fitted to data, so these are outputs of chosen assumptions, not estimates.
- Infiltration route (cost 41, 11 moves) wades 4 crocodile-water cells. A
  separate exposure-minimising search puts the floor over *every* route at 4,
  which is what licenses the claim that any overland approach must wade at
  least that many.

## Install

From this package directory:

```bash
uv sync --extra dev        # installs deps incl. the local bond-api path dep
```

## Run the mission

```bash
uv run python scripts/00_preflight.py              # verify readiness
uv run python scripts/run_mission.py               # full five-stage mission
uv run python scripts/{brief,recon,plan,execute,debrief}.py   # per-phase CLIs
uv run python scripts/generate_figures.py          # all three output/figures/*.png
uv run python scripts/z_generate_manuscript_variables.py
```

Regenerable artifacts are written under `output/` (git-ignored).

## Manuscript

`manuscript/config.yaml` (identity + mission block) drives
`src/live_and_let_die/manuscript_variables.py`, which computes every `{{TOKEN}}`
from the pure domain core — no metric is hand-authored in prose, down to the
provenance seed, terrain grid shape, and drum timing constants.
`scripts/z_generate_manuscript_variables.py` hydrates and copies the numbered
sections to `output/manuscript/`; strict mode fails on any unresolved token, and
`tests/test_manuscript_variables.py` fails on any token used in prose that
`generate_variables()` does not produce.

All three figures are **embedded** in the results section via
`![caption]({{LALD_FIGURE_DIR}}/name.png)`. `LALD_FIGURE_DIR` is derived from the
real `output/figures` and `output/manuscript` paths, so the rendered section
carries a link that resolves; a test renders the figures, resolves the
manuscript, and opens every embedded path, failing if one is missing or renamed.

## Verification gates

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
rg -n "template[_]code_project" .     # expectation: zero
```

The coverage gate is **90% line + branch on `src/`**; the suite currently runs
well above it. Measured test count and per-module coverage — from an actual run,
never hand-written — are in [`docs/_generated/COUNTS.md`](docs/_generated/COUNTS.md).

## Documentation

| Read | For |
| --- | --- |
| [`docs/architecture.md`](docs/architecture.md) | Module-by-module design and how `mission.py` implements the frozen protocol |
| [`docs/agent_instructions.md`](docs/agent_instructions.md) | Hard constraints and the verification checklist |
| [`docs/testing_philosophy.md`](docs/testing_philosophy.md) | No-mocks / real-data / determinism doctrine |
| [`AGENTS.md`](AGENTS.md) | Build, test, and verify instructions |
| [`TODO.md`](TODO.md) | What is genuinely left |

## License

MIT — see `LICENSE`.
