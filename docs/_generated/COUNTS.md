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
| Tests passing | 111 |
| Tests failing | 0 |
| Tests skipped | 0 |
| Line + branch coverage on `src/` | 97.76% |
| Coverage gate (`--cov-fail-under`) | 90% |
| Statements / branches | 959 / 290 |
| ruff check + ruff format --check | clean on `src/`, `scripts/`, `tests/` |
| mypy | clean (20 source files) |

## Domain modules

| Module | Coverage |
| --- | --- |
| `src/live_and_let_die/coded_comms.py` | 96.49% |
| `src/live_and_let_die/figures/plots.py` | 100.00% |
| `src/live_and_let_die/interdiction.py` | 97.89% |
| `src/live_and_let_die/island_ops.py` | 96.09% |
| `src/live_and_let_die/manuscript_variables.py` | 97.27% |
| `src/live_and_let_die/market_flow.py` | 94.64% |
| `src/live_and_let_die/mission.py` | 100.00% |
| `src/live_and_let_die/supply_graph.py` | 98.30% |
| `src/live_and_let_die/voodoo_drums.py` | 97.70% |

## Canonical deterministic findings

- Supply graph: 7 nodes, 10 legs; max throughput 220, min-cut 220;
  critical transit node `airfield` (disruption 150 units to Miami).
- Interdiction: 3-leg plan collapses the operation (greedy 220 / exact 220);
  top target leg `field_works -> harbor` (50 units).
- Communiqué plaintext: `KANANGA LETS THE SNAKE BITE` (keyword BARON); drum code
  195 beats, exact round-trip.
- Market economics: producer share 1.7%, price spread ~59x, ~$3.89M revenue.
- Infiltration route: cost 41, 11 moves, 4 crocodile-water cells.

## Manuscript

| Metric | Value |
| --- | --- |
| Numbered sections hydrated in strict mode | 9 |
| Manuscript tokens produced by `generate_variables()` | 66 |
| Unresolved tokens | 0 |
| Figures rendered by `scripts/generate_figures.py` | 3 |
