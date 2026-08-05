# COUNTS — LIVE AND LET DIE / SAN MONIQUE (generated)

Live numbers for the verification gates. Regenerate (run the suite) rather than
hand-edit; these are volatile measurements that drift as the code evolves.

Measured with:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

## Test suite

| Metric | Value |
| --- | --- |
| Tests passing | 130 |
| Tests failing | 0 |
| Tests skipped | 0 |
| Line + branch coverage on `src/` | 97.89% |
| Coverage gate (`--cov-fail-under`) | 90% |
| Statements / branches | 1012 / 312 |
| ruff check + ruff format --check | clean on `src/`, `scripts/`, `tests/` |
| mypy | clean (11 source files under `src/`) |

## Domain modules

| Module | Coverage |
| --- | --- |
| `src/live_and_let_die/coded_comms.py` | 96.49% |
| `src/live_and_let_die/figures/plots.py` | 100.00% |
| `src/live_and_let_die/interdiction.py` | 97.89% |
| `src/live_and_let_die/island_ops.py` | 95.81% |
| `src/live_and_let_die/manuscript_variables.py` | 97.66% |
| `src/live_and_let_die/market_flow.py` | 98.41% |
| `src/live_and_let_die/mission.py` | 100.00% |
| `src/live_and_let_die/supply_graph.py` | 98.35% |
| `src/live_and_let_die/voodoo_drums.py` | 97.70% |

## Canonical deterministic findings

- Supply graph: 7 nodes, 10 legs; max throughput 220, min-cut 220;
  critical transit node `airfield`, disruption 110 of those 220 units. Both
  numbers come from the same demand-capped `SUPPLY -> DEMAND` flow model.
- Min cut: `miami -> DEMAND`, `new_york -> DEMAND` — 0 physical legs. The
  network is demand-limited; the cut bounds throughput and names no target.
- Interdiction: 3-leg plan collapses the operation (greedy 220 / exact 220);
  top target leg `field_works -> harbor` (50 units).
- Communiqué plaintext: `KANANGA LETS THE SNAKE BITE` (keyword BARON). The
  unkeyed frequency attack returns `IEAEAHE LTON ORT NAEIT SDOT` at score 0.926
  — it does not recover this intercept. Drum code 195 beats, exact round-trip.
- Market economics: producer share 1.7%, price spread ~59x, ~$3.89M revenue —
  all outputs of invented scenario parameters, not empirical estimates.
- Infiltration route: cost 41, 11 moves, 4 crocodile-water cells; minimum
  crocodile exposure over *all* routes is also 4 (the universal-claim floor).

## Manuscript

| Metric | Value |
| --- | --- |
| Numbered sections hydrated in strict mode | 9 |
| Manuscript tokens produced by `generate_variables()` | 71 |
| Unresolved tokens | 0 |
| Figures rendered by `scripts/generate_figures.py` | 3 |
| Figures embedded in the rendered manuscript | 3 |
| Embedded figure paths that resolve on disk | 3 / 3 |
