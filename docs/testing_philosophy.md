# Testing philosophy — LIVE AND LET DIE / SAN MONIQUE

Tests here are **real-data, deterministic, and mock-free**. That combination is
not a style preference: it is what makes the manuscript's claims checkable.

## Why no mocks

A mock asserts that the code called something in a particular way. It says
nothing about whether the answer is right. Every algorithm in this package
produces a number that ends up in the manuscript, so the only test worth writing
is one that runs the real computation on real data and checks the real answer.

Concretely: no `unittest.mock`, no `MagicMock`, no `mocker.patch`, no
`create_autospec`, and no hand-rolled stand-in object that replaces a dependency.
`tests/test_scripts_smoke.py` enforces the lexical half of this on `scripts/`
directly.

Nothing in this package needs mocking anyway — there is no network, no database,
no clock in any artifact, and no external service. The heaviest dependency is
matplotlib, and it is exercised for real with the `Agg` backend into `tmp_path`.

## Why determinism makes exact assertions possible

Because every input is a fixed canonical dataset and every algorithm is pure with
deterministic tie-breaking, results are *stable values*, not distributions. So
tests assert exact numbers — route cost `41`, `4` crocodile cells, max flow
`220`, drum message `195` beats, producer share `1.7%` — rather than
`assert result > 0`, which passes for almost any bug.

This is the difference between a test that binds behaviour and a test that
merely runs it. A shape assertion (`assert isinstance(x, dict)`,
`assert len(rows) > 0`) can survive a wholesale corruption of the numbers. An
exact assertion cannot.

Determinism is maintained by:

- fixed canonical datasets embedded in the domain modules;
- deterministic tie-breaking in every search (`(cost, node_id)` and
  `(cost, row, col)` heap keys; sorted adjacency; sorted severable-leg order);
- no random draws anywhere and no wall-clock value in any persisted artifact
  (`Provenance.wall_time_s` is fixed at `0.0`, and `generate_variables` takes a
  `now=` override so timestamp handling itself is testable);
- provenance seed `MISSION_SEED = 8` recorded for suite parity.

## What each test file binds

| File | What it holds down |
| --- | --- |
| `test_supply_graph.py` | Dataclass validation, Dijkstra costs and paths, Edmonds-Karp flow, min-cut value and edges, per-edge and per-node disruption, critical-node selection, and the error branches (unknown node, unreachable target, duplicate id). Also the two model-coherence gates: that the reported disruption is measured on the *same* demand-capped flow graph as the reported throughput (the two models give 110 and 150 here, so the equality is not satisfiable by both), and that the min-cut classifier really separates physical legs from virtual capacity edges (positive control on a hand-built cut) |
| `test_interdiction.py` | Greedy and exact plans, the invariant that the exact optimum is never worse than greedy, the efficiency ranking order, budget-0 and budget-overflow edge cases, and negative-budget rejection |
| `test_coded_comms.py` | Keyword-key construction, encipher/decipher round-trip, non-bijective key rejection, frequency tables, cosine scoring bounds, and glyph-roster bijectivity. `solve_substitution` is pinned to its exact output string and score — and a second test records the limitation that at 27 characters the attack recovers nothing while still scoring 0.93, so the score is never mistaken for evidence of recovery |
| `test_voodoo_drums.py` | Morse table integrity, exact signal round-trip, strict run-length rejection of malformed signals, unencodable characters, and rhythm signature/distance |
| `test_market_flow.py` | Price and purity propagation, revenue aggregation, the missing-leg-economics `ValueError` path, and that `EDGE_ECONOMICS` covers exactly the canonical legs. The producer share is bound by *mechanism*, not by a band: the model is re-run on substituted parameter sets (neutral markups, doubled markups, doubled farm gate) and the share must move exactly as the path structure predicts. A band like `0.01 < share < 0.05` on hand-tuned constants is green by construction and was removed |
| `test_island_ops.py` | Grid validation, route cost and path, crocodile exposure, and out-of-bounds / untraversable / unreachable errors. Separately, `min_crocodile_exposure` — the lower bound over the whole route space that licenses the manuscript's universal claim — with a positive control (a crocodile shortcut beside a crocodile-free detour) where the cheapest route's exposure and the true minimum differ |
| `test_mission.py` | The full `MissionProvider` lifecycle, protocol conformance, provenance stability, gadget registration, and that brief/recon report values **derived** from the live graph rather than literals |
| `test_manuscript_variables.py` | The live cross-reference gate: every `{{TOKEN}}` used in `manuscript/[0-9]*.md` resolves through `generate_variables()`, strict-mode failure on unknown tokens, and hydration determinism. Plus the figure-embed gate: figures are rendered, the manuscript is resolved into an `output/`-shaped tree, and every `![](...)` path is opened — a manuscript that only *mentions* its figures fails |
| `test_figures.py` | That all three figures render to non-empty files, at a custom path and at the default output directory |
| `test_scripts_smoke.py` | Every thin CLI runs as a subprocess with exit code 0 and writes the artifacts it claims to |

## The gate

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

Line **and** branch coverage on `src/`, floor 90% (`branch = true` in
`pyproject.toml`). Measured numbers live in `_generated/COUNTS.md` — regenerated
from a real run, never hand-written.

Coverage is a floor, not the goal. A suite can reach 100% and prove nothing if
its assertions are vacuous. The intent here is that error branches are reached by
*triggering the error*, not by suppressing it.

## Anti-patterns this suite rejects

- **Shape-only assertions.** `assert result` where an exact value is knowable.
- **A gate that cannot fail.** A bare `assert` in a `scripts/` verification path
  vanishes under `python -O`; conditions there are explicit `if`/`return 1`.
- **A hand-authored expected value that is really a copy of the code.** Expected
  values are film-domain facts (the route wades the channel; the strike collapses
  the network), pinned as numbers.
- **Tests that dirty the tree.** Artifact-writing tests use `tmp_path`, or write
  under the git-ignored `output/`.

## Conventions

- `conftest.py` sets `MPLBACKEND=Agg` before any rendering import and puts the
  package root and `src/` on `sys.path`, so tests run identically whether or not
  the package is installed.
- Subprocess tests invoke `sys.executable` from the package root, so they use the
  same interpreter as the suite.
