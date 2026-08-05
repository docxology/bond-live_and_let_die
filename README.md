# LIVE AND LET DIE (1973) — SAN MONIQUE

**PROJECT BOND · film package (deepened, Phase 4)** · mission codename **SAN MONIQUE**

Deterministic special-agent mission software for Kananga's narcotics operation
on the Caribbean island of San Monique, built as one of 27 film packages in the
BOND suite. It implements the FROZEN BOND-API `MissionProvider` protocol over a
pure, infrastructure-free domain core.

## Concepts

Six film concepts, six pure domain modules:

| Module | Concept | Real algorithms & data |
| --- | --- | --- |
| `supply_graph.py` | Narcotics supply-graph analytics (production → transit → market) | Dijkstra shortest paths; Edmonds-Karp max-flow; residual minimum cut; per-transit-node disruption (critical-bottleneck) analysis |
| `interdiction.py` | Budgeted network interdiction | Deterministic network-interdiction: greedy + exact (exhaustive) solvers, efficiency target list over max-flow impact |
| `coded_comms.py` | Voodoo-coded communiqué deciphering | Keyword (symbol-substitution) cipher; encipher/decipher; letter-frequency attack solver with cosine scoring; glyph roster |
| `voodoo_drums.py` | Voodoo drum-code signaling | Morse-style rhythm codec over a per-beat grid; strict run-length decode; traffic signature + distance |
| `market_flow.py` | Farm-gate-to-street economics | Per-leg price markup & purity dilution; producer share, price-spread ratio, gross revenue |
| `island_ops.py` | Caribbean island ops planner (mangrove/crocodile terrain) | Weighted terrain grid; 4-neighbour Dijkstra routing; crocodile-exposure hazard tracking |

The film's mission adapter, `mission.py`, layers the frozen BOND-API protocol
(`brief` / `recon` / `plan` / `execute` / `debrief`) over this core and registers
six analysers as gadgets. The protocol surface is stable across phases —
downstream coordinators / CLI / orchestrator keep working unchanged.

## Canonical findings (computed, never hand-authored)

- Supply graph: 7 nodes, 10 legs; cheapest Miami route `poppy_fields -> airfield
  -> miami` (cost 13); max throughput 220 units, min-cut 220.
- **Interdiction**: an optimal 3-leg strike plan (greedy 220 units, exact 220)
  collapses the whole operation; the top target leg
  `field_works -> harbor` is worth 50 units alone.
- The voodoo communiqué deciphers under the BARON keyword to
  *"KANANGA LETS THE SNAKE BITE"*; the drums carry a 195-beat message that
  decodes exactly to the same plaintext.
- **Market economics**: producer share is 1.7% of street value; a 59×
  farm-gate-to-street price spread; ~$3.89M gross revenue.
- Infiltration route (cost 41) wades 4 crocodile-water cells to the airfield.

## Install

From the repository root:

```bash
uv sync --extra dev        # installs deps incl. the local bond-api path dep
```

## Run the mission

```bash
uv run python scripts/00_preflight.py              # verify readiness
uv run python scripts/run_mission.py               # full five-stage mission
uv run python scripts/{brief,recon,plan,execute,debrief}.py   # per-phase CLIs
uv run python scripts/generate_figures.py          # output/figures/*.png
uv run python scripts/z_generate_manuscript_variables.py
```

Regenerable artifacts are written under `output/` (git-ignored).

## Manuscript

`manuscript/config.yaml` (identity + mission block) drives
`src/live_and_let_die/manuscript_variables.py`, which computes every `{{TOKEN}}`
from the pure domain core — no metric is hand-authored in prose.
`scripts/z_generate_manuscript_variables.py` hydrates and copies the numbered
sections to `output/manuscript/`; strict mode fails on any unresolved token.

## Verification gates

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format src/ scripts/ tests/
uv run mypy src/ scripts/
rg -n "template[_]code_project" .     # expectation: zero
```

See `docs/_generated/COUNTS.md` for the live test count and coverage.

## License

MIT — see `LICENSE`.
