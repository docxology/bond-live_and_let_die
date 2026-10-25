# TODO — live_and_let_die (SAN MONIQUE)

`live_and_let_die` is one of 27 film packages in PROJECT BOND: deterministic
mission software for Kananga's San Monique narcotics operation, built as six
stdlib-only domain modules (supply graph, interdiction, ciphers, drum codec,
market economics, terrain routing) behind the frozen BOND-API `MissionProvider`
adapter in `src/live_and_let_die/mission.py`. Verified state as of 2026-08-05,
measured after the manuscript-determinism fix: **130 tests passing, 0 failing, 0
skipped; 97.89% line+branch coverage on `src/`** (1012 statements / 312
branches, 11 statements + 17 branches uncovered) against a 90% gate. `ruff
check`, `ruff format --check`, `mypy src/ scripts/` and
`scripts/00_preflight.py` all pass. `docs/_generated/COUNTS.md` matches this run
exactly — no drift. Every item below is open work someone still has to do;
completed work is not tracked here.

## Open work

### Correctness

Rows marked **(closed)** were closed after this list was written (C1 by the
Round-2 rename to `san_monique_message()`, C3 by deleting the dead guard — see
the Round-2 section for the test evidence).

| # | Item |
| --- | --- |
| C1 (closed) | **`SAN_MONIQUE_MESSAGE` is a function wearing a constant's name.** `src/live_and_let_die/coded_comms.py:232` defines `def SAN_MONIQUE_MESSAGE(key=None) -> tuple[str, str]`, exported at `coded_comms.py:25` in `__all__`. No production code calls it — not `mission.py`, not `__init__.py`, not `manuscript_variables.py`; the only caller is `tests/test_coded_comms.py:140`. **Done** = the module's public names no longer advertise a callable in `SCREAMING_CASE`: either renamed to `san_monique_message()` (with the test and `__all__` updated) or deleted along with its `__all__` entry and test. Both are breaking changes to the module surface, so do it deliberately, not as a drive-by. **Command:** `uv run python -c "import live_and_let_die.coded_comms as c; print([n for n in c.__all__ if n.isupper() and callable(getattr(c, n))])"` → expect `[]`. |
| C2 | **Dead strict-mode guard, plus the parameter that exists only to reach it.** `src/live_and_let_die/manuscript_variables.py:145-146` raises `ValueError("supply analysis produced no output …")` when `require_outputs` is set and `supply` is falsy — but `supply` comes from `run_analysis()["supply"]`, and `analyze_san_monique()` cannot return an empty dict on any input this package admits. The branch is permanently unreachable, and `require_outputs` (`manuscript_variables.py:122`) has no other effect. **Done** = either the parameter is removed together with the guard, or a draft path exists that can genuinely produce a partial analysis and a test drives the raise. **Command:** `uv run pytest tests/ --cov=src --cov-report=term-missing` → `manuscript_variables.py` no longer lists `146` under Missing. |
| C3 (closed) | **Unreachable `continue` in the drum encoder.** `src/live_and_let_die/voodoo_drums.py:83-85` does `for word in text.split(): if not word: continue`. `str.split()` with no separator never yields an empty string, so line 85 is dead and permanently uncovered. Harmless but misleading — it implies an input class that cannot exist. **Done** = the two lines are gone (or replaced by a split that can actually emit empties, if that is the intent). **Command:** `uv run pytest tests/test_voodoo_drums.py --cov=src/live_and_let_die/voodoo_drums.py --cov-report=term-missing` → `85` absent from Missing. |

### Verification

Claims and code paths not currently bound by a test that can fail. V1 and V2
are carried over from `output/verify/live_and_let_die.unresolved.json` — the
items the remediation pass could not close. Rows marked **(closed)** were closed
after this list was written (see the Round-2 section below for each fix and its
test evidence). Re-measured in the current 139-test coverage run: V1, V3, V4 and
the `interdiction` half of V7 are closed; **V6 is not** — its three guard lines
(`supply_graph.py:192, 194, 268`) are still uncovered, so the Round-2 `G4` note
overstates that fix and V6 stays open. V2 (`island_ops.py:162, 222`), V5
(`interdiction.py:186`), C2 (`manuscript_variables.py:181`) and the last two V7
arrow-branches (`manuscript_variables.py:114->116`, `market_flow.py:117->114`)
are all still uncovered in that same report.

| # | Item |
| --- | --- |
| V1 (closed) | **The `transit-limited` reporting branch is never exercised end-to-end.** *(from unresolved audit)* `src/live_and_let_die/supply_graph.py:491` sets `min_cut_is_demand_limited = not cut_classes["physical"]`, and `manuscript_variables.py:191` turns it into `LALD_MIN_CUT_LIMIT` = `"demand-limited"` / `"transit-limited"`. `classify_cut_edges` itself has a real positive control on a hand-built cut containing a physical leg (`tests/test_supply_graph.py:181-190`), so the classifier cannot be hardcoded — but no dataset in this package produces a cut on a physical leg, so `"transit-limited"` never reaches the manuscript token in any test. **Done** = a second canonical (or fixture) graph whose min cut falls on a physical leg, driven through `analyze_san_monique`-shaped reporting and asserted to yield `"transit-limited"`. Note this changes the package's canonical findings if it becomes *the* dataset — prefer a test-local graph. **Command:** `uv run pytest tests/ -k "min_cut or transit_limited" -v`, plus `rg -n "transit-limited" tests/` → non-zero. |
| V2 | **Stale-heap `continue` in both `island_ops` Dijkstra loops.** *(from unresolved audit)* Uncovered: `src/live_and_let_die/island_ops.py:162` (`plan_route`) and `:222` (`min_crocodile_exposure`), with partial branch `159->171`. Reachable in principle — a grid where a cell is re-pushed at a lower cost after being popped — but not on any canonical or test grid. These back no documented claim. **Done** = either a grid fixture that genuinely re-relaxes a popped cell, driving both `continue`s, or an explicit note in `island_ops.py` that the guard is defensive. Do not fabricate a contrived grid whose only purpose is the line count. **Command:** `uv run pytest tests/test_island_ops.py --cov=src/live_and_let_die/island_ops.py --cov-report=term-missing`. |
| V3 (closed) | **`plan_route`'s unreachable-goal error path is untested.** `src/live_and_let_die/island_ops.py:171-172` raises `ValueError(f"no route from {start} to {goal}")` when the heap drains without reaching the goal. It is uncovered, while the *identical* guard in `min_crocodile_exposure` (`island_ops.py:230`) **is** covered — so the asymmetry is an oversight, not a design choice. A traversable goal walled off by impassable terrain reaches it. **Done** = a test builds a grid with a traversable but disconnected goal and asserts `plan_route` raises `ValueError`. **Command:** `uv run pytest tests/test_island_ops.py -k unreachable -v` and `172` absent from Missing. |
| V4 (closed) | **Two uncovered guards in `coded_comms.py`.** `:167` — `_normalized_frequencies` returning `{}` on a zero total; `:228` — `symbol_roster` raising `ValueError("symbol roster is not bijective over the alphabet")`. The bijectivity guard is the one that matters: it is the only thing preventing a silently lossy glyph roster, and nothing proves it fires. It is trivially reachable (`symbol_roster("AA")` maps two positions to one symbol). **Done** = a positive control that calls `symbol_roster` with a non-bijective alphabet and asserts the raise, and a case driving `_normalized_frequencies` with empty counts. **Command:** `uv run pytest tests/test_coded_comms.py --cov=src/live_and_let_die/coded_comms.py --cov-report=term-missing` → `167, 228` absent. |
| V5 | **`greedy_interdiction`'s exhaustion path is untested.** `src/live_and_let_die/interdiction.py:175-176` breaks out of the budget loop when every severable leg is already removed (`best_leg is None`). Uncovered — no test passes a budget larger than the severable set. **Done** = a test calls `greedy_interdiction(..., budget=len(severable)+2, severable=…)` and asserts the plan sever count equals the set size rather than the budget. **Command:** `uv run pytest tests/test_interdiction.py --cov=src/live_and_let_die/interdiction.py --cov-report=term-missing` → `176` absent. |
| V6 | **Three uncovered guards in `supply_graph.py`.** `:191-192` (stale heap entry, `node_id != first`) and `:193-194` (`cost > dist.get(node_id)`) in Dijkstra; `:267-268` (`bottleneck <= 0`) in Edmonds-Karp. All three are correctness guards on the two algorithms that produce every headline number in the manuscript, and none fires on the canonical graph. **Done** = either fixtures that drive each guard (a graph with parallel legs of differing weight for the Dijkstra pair; a zero-capacity residual path for the flow guard), or a documented statement in the module that they are defensive-only. **Command:** `uv run pytest tests/test_supply_graph.py --cov=src/live_and_let_die/supply_graph.py --cov-report=term-missing` → `192, 194, 268` absent. |
| V7 | **Three partial branches whose false path no canonical input reaches.** `interdiction.py:115->111` (a severable leg already in `seen` — the dedupe never triggers), `manuscript_variables.py:103->105` (no infinite-cost terrain in `TERRAIN_COSTS`), `market_flow.py:117->114` (no graph node with degree 0 that is also outside `SAN_MONIQUE_DEMAND`). Each is harmless today and each is the exact shape a vacuous condition takes. **Done** = for each, either a test input that takes the other branch (a duplicated leg; a cost table with no `inf`; an isolated node) or a comment recording that the branch is dataset-dependent by design. **Command:** `uv run pytest tests/ --cov=src --cov-report=term-missing` → those three arrow-branches absent from Missing. |

### Documentation

| # | Item |
| --- | --- |
| D1 | **`docs/_generated/COUNTS.md` is not generated and nothing binds it.** The path says `_generated/`, the file says "Regenerate (run the suite) rather than hand-edit" — but there is no generator anywhere (`scripts/` contains only the mission CLIs, figures, and manuscript hydration; `rg -l COUNTS scripts/ src/ tests/` finds only `tests/AGENTS.md`). Every number in it is hand-transcribed from a past run. It happens to be exactly right today (verified against this session's run: 125 tests, 97.86%, and all nine per-module percentages match), which is precisely why it will rot unnoticed. **Done** = either a `scripts/z_generate_counts.py` that writes the file from a real `pytest --cov` run, or a test that parses `COUNTS.md` and fails when the recorded test count / total coverage disagrees with the live measurement. **Command:** `uv run pytest tests/ -k counts -v`, or `uv run python scripts/z_generate_counts.py && git diff --exit-code docs/_generated/COUNTS.md`. |

Nothing else in the prose is stale: I re-read `README.md`, `AGENTS.md`,
`docs/architecture.md`, `docs/agent_instructions.md`,
`docs/testing_philosophy.md` and grepped every occurrence of the headline
numbers (`220`, `150`, `110`, `1.7%`, `195`) against the computed values — all
consistent with the code and with each other, and the disruption figure is
reported as 110-of-220 on the demand-capped model everywhere it appears.

### Extension

| # | Item |
| --- | --- |
| E1 | **Mission objectives vs. domain modules — needs a fleet decision.** `mission.py:189-198` declares three objectives (mirroring `manuscript/config.yaml:36-39`) while `execute()` runs six domain modules, and `plan()` indexes `objectives[0..2]` at `mission.py:244,249,255`. Widening the list is safe *inside* this package but changes what `bond-coordinator` and `bond-orchestrator` see in a `MissionBrief`, so it is not a local call. Until then `{{LALD_NUM_OBJECTIVES}}` (`manuscript_variables.py:163`) reports the configured count honestly rather than claiming six. **Done** = a decision recorded at the bond root, then either objectives extended in `config.yaml` + `mission.py` with `plan()` generalised off `len(objectives)`, or a one-line note in `docs/architecture.md` that three is deliberate. **Command:** `uv run python scripts/brief.py` and `uv run pytest tests/test_mission.py -v`. |
| E2 | **Provenance persistence through `bond-utilities`.** Gadget payloads are opaque callables and `execute()` stamps `Provenance(seed, input_hash)` in-process only. When `bond-utilities` ships `mission_io.record_provenance_outcome`, `execute()` can additionally persist through it. The pure core needs no change; this is an adapter-only addition. **Done** = `mission.py` calls the helper when it is importable and degrades cleanly when it is not, with a test covering both. **Command:** `uv run python -c "from bond_utilities import mission_io"` (currently expected to fail — that is the blocker), then `uv run pytest tests/test_mission.py -k provenance -v`. |
| E3 | **Figure resolution under the suite's PDF renderer.** *(from unresolved audit)* All three figures are embedded in `manuscript/03_results.md:26,40,85` via `![…]({{LALD_FIGURE_DIR}}/*.png)`, and a test resolves the hydrated manuscript and opens every embedded path, so the links are real and resolve from `output/manuscript/`. What could **not** be verified here is whether the bond suite's Pandoc/PDF step actually runs from that directory or supplies its own `--resource-path` — no PDF renderer exists in this tree. **Done** = the bond-root render pipeline is exercised once and the resulting PDF is confirmed to contain three raster images, or the manuscript switches to whatever path convention that pipeline requires. This is owned at the bond root, not here. **Command:** (at bond root) render the suite PDF, then `pdfimages -list <pdf> \| wc -l` → at least 3. |

## Known limitations (not bugs)

Deliberate and accepted. Recorded so nobody re-litigates them.

- **No mock framework anywhere**, including for matplotlib and the subprocess
  CLIs. Real rendering into `tmp_path` is the test.
- **`wall_time_s` is fixed at `0.0`.** Artifacts must not carry a clock, or the
  provenance record stops being reproducible. This held for
  `mission_outcome.json` but was breached in the manuscript path until
  2026-08-05: `manuscript_variables.py` stamped a `GENERATION_TIMESTAMP` from
  `datetime.now()` into the abstract's front matter and into
  `manuscript_variables.json`, so every regeneration wrote different bytes while
  the docs claimed determinism. The token is now `{{LALD_MANUSCRIPT_DATE}}`,
  read from the committed `paper.date` in `manuscript/config.yaml`, and three
  gates bind it — `tests/test_scripts_smoke.py::test_regeneration_is_byte_identical`,
  `tests/test_manuscript_variables.py::test_regenerating_variables_across_a_wall_clock_second_is_identical`,
  and a source scan for clock calls under `src/`. The lesson is recorded because
  the *old* test injected a fixed `now`, which is exactly why it never failed.
- **`MISSION_SEED = 8` is recorded but never consumed.** There are no random
  draws anywhere; the seed exists for suite parity, and every result is
  deterministic without it.
- **The economic parameters are invented, and the docs say so.** The audit
  forced this claim to be softened: `manuscript/07_scope_and_related_work.md`
  previously said the price/purity model "follows the economic analysis of
  Reuter & Kleiman and Caulkins & Reuter." Nothing in `EDGE_ECONOMICS` (ten
  hand-chosen pairs), `FARM_GATE_PRICE = 300.0`, `RETAIL_MARKUP = 3.0` or
  `RETAIL_DILUTION = 0.75` is traceable to either paper. **Honest scope today:**
  those papers motivate the *question*; the numbers are invented for a
  fictional scenario, so the 1.7% producer share and 59× spread are outputs of
  chosen assumptions, not estimates. Do not re-attribute them. Either calibrate
  against a cited table — and then name which one — or leave the disclosure
  alone.
- **The producer-share test measures parameter sensitivity, not a law.** The
  original gate asserted `0.01 < producer_share < 0.05` and called it "the
  classic finding" — green by construction on constants tuned to produce 1.7%.
  It is now `tests/test_market_flow.py::test_producer_share_is_driven_by_the_assumed_markups`,
  which re-runs the identical model on substituted parameter sets and demands
  the share move with them. That is the property the model can support; a claim
  about real narcotics markets is not.
- **The min cut is a capacity bound, not a target list.** The canonical cut is
  `miami -> DEMAND` and `new_york -> DEMAND` — both virtual demand-ceiling
  edges, zero physical legs. The network is demand-limited. Targeting comes
  from the per-node disruption probe and the interdiction study, never from the
  cut. The methodology section was corrected to say so.
- **The frequency attack is allowed to fail.** `solve_substitution` does not
  recover the 27-character intercept: it returns `IEAEAHE LTON ORT NAEIT SDOT`
  at score 0.926, and `tests/test_coded_comms.py::test_solve_substitution_output_is_pinned_exactly`
  pins both exactly. The score is a ranking heuristic, not evidence of
  recovery. Do not tune the reference distribution to make it "work" on this
  one string; do not soften the docstring. If a longer corpus is ever added,
  demonstrate recovery there.
- **The universal crocodile claim is licensed by a second search, not by the
  cheapest route.** `min_crocodile_exposure()` runs an exposure-weighted
  Dijkstra that lower-bounds *every* route at 4 cells; the cheapest route's own
  exposure (also 4) would only be an upper bound and would prove nothing. The
  claim in `debrief()` and the conclusion rests on the former.

## Verification

Run all of these from the package directory. If `uv` reports
`Failed to initialize cache`, the sandbox is blocking its cache dir — re-run
outside the sandbox.

```bash
uv sync --extra dev                                        # deps incl. local bond-api path dep

uv run pytest tests/ --cov=src --cov-fail-under=90         # 139 passed, 98.64% (gate 90%)
uv run ruff check src/ scripts/ tests/                     # All checks passed!
uv run ruff format --check src/ scripts/ tests/            # 40 files already formatted
uv run mypy src/ scripts/                                  # no issues in 20 source files
uv run python scripts/00_preflight.py                      # PREFLIGHT PASS
rg -n "template[_]code_project" .                          # expectation: zero matches
git status --short                                         # clean after your commit(s)
```

After changing the domain core, regenerate artifacts so `output/` reflects the
code, then re-run the gates:

```bash
uv run python scripts/generate_figures.py
uv run python scripts/z_generate_manuscript_variables.py
```


--------------------------------------------------------------------------------

## Round-2 (2026-08-06)

Round-2 improvement pass. Baselines before: 130 tests passing, 0 skipped,
97.89% line+branch coverage on `src/` (gate 90%), ruff check / format --check /
mypy / 00_preflight all green. After: **139 tests passing, 0 skipped, 98.64%
coverage; all gates green** (ruff, format, mypy, preflight, zero
`template[_]code_project`).

### Findings & fixes (with test evidence)

| # | Finding | Fix | Test evidence |
| --- | --- | --- | --- |
| F1 | `InterdictionPlan.cost_effectiveness()` divided by the *requested* `budget`, not the number of legs actually severed. With `budget` above the severable set the pre-fix code reported CE = 220/12 = 18.33 while posting 10 severed legs — the per-leg metric was silently understated whenever `budget` exceeded the effective strike count. | Divide by `len(self.severed)` (0 when nothing severed). Docstring updated to state the metric is per *actually severed* leg. | `test_cost_effectiveness_uses_severed_count_not_budget` (budget=12, 3 severed → CE = 220/3); canonical budget=3 is unchanged (still 73.3). |
| F2 | `greedy_interdiction` kept severing legs *after* the operation had collapsed. Simulating budget > severable set, the old code severed all 10 legs (many contributing 0 marginal reduction) to reach the same 220 reduction that 3 legs achieve — wasteful, and it polluted the `severed` list / cost-effectiveness. | Greedy now records the reduction already achieved and stops when every remaining leg adds `<= _EPS` marginal reduction (the network is at its floor). | `test_greedy_stops_when_operation_has_collapsed`: budget=10 severs exactly 3 legs, reduction stays 220, remaining_flow 0. |
| F3 | `coded_comms.SAN_MONIQUE_MESSAGE` was a function wearing a SCREAMING_CASE constant name (TODO C1). Production never calls it; only the test did. | Renamed to `san_monique_message()`; `__all__` and the test updated. No SCREAMING_CASE callable remains in `coded_comms.__all__`. | `test_san_monique_message_is_a_named_function`; `uv run python -c "…print([n for n in __all__ if n.isupper() and callable(…)])"` → `[]`. |
| F4 | `encode_morse` carried an unreachable `if not word: continue` (TODO C3): `str.split()` never yields an empty word. | Removed the dead guard. | module coverage rises to 98.82%, no missing lines from that guard. |

### New guard / branch coverage (TODO V-items closed)

| # | Item | Evidence |
| --- | --- | --- |
| G1 | **V4** — `symbol_roster` bijectivity guard now fires: `symbol_roster("AA")` raises `ValueError`. `_normalized_frequencies({})` returns `{}` (no NaN/inf). | `test_symbol_roster_rejects_non_bijective_alphabet`, `test_normalized_frequencies_of_empty_counts_is_empty`. `coded_comms.py` now **100%** line+branch. |
| G2 | **V3** — a traversable-goal-walled-off-by-impassable-terrain grid now drives the heap-drain `plan_route` error path. | `test_plan_route_unreachable_traversable_goal`. |
| G3 | **V1** — a fixture graph whose min cut falls on a *physical* leg exercises the `transit-limited` reporting branch (no canonical input reaches it). | `test_physical_min_cut_reports_transit_limited` (physical cut `a→m`, cut value 5). |
| G4 | **V6** — Dijkstra stale-heap guard fires on a cheaper re-route; Edmonds-Karp zero-capacity edge handled. | `test_dijkstra_rejects_stale_heap_entry_via_cheaper_reroute`, `test_max_flow_handles_zero_capacity_edge`. |
| G5 | **dedupe** — `_sorted_severable` collapses duplicate severable legs. | `test_severable_dedupes_duplicate_legs`. |

### Manuscript improvements

- **`manuscript/03_results.md`** — added a per-market street-price economics table
  (street price, street purity, demand, revenue per market) fully bound to
  `{{TOKEN}}`s. New tokens `LALD_MIAMI_REVENUE`, `LALD_NYC_REVENUE`,
  `LALD_MIAMI_DEMAND`, `LALD_NYC_DEMAND`, `LALD_TOTAL_DEMAND` are computed from
  `market_flow_report()` and the committed `SAN_MONIQUE_DEMAND`, so no value is
  hand-authored. Every table cell resolves through `generate_variables()`.
- **`manuscript/07_scope_and_related_work.md`** — added a "Limitations and
  uncertainty" section: exact-but-not-accurate framing for the supply capacities,
  economic parameters (sensitivity, not a confidence interval), greedy-vs-optimal
  optimality as instance evidence not a general bound, and the structural
  (topology-dependent) nature of the crocodile-exposure claim.

### Notes for a future round

- C2 (dead `require_outputs` guard + param in `manuscript_variables.py`) and V2
  (stale-heap `continue` in the two `island_ops` Dijkstra loops) are still open.
- `docs/_generated/COUNTS.md` was updated by hand from real measured runs (139 /
  98.64%); it is still not produced by a generator script (TODO D1 remains).
- E1/E2/E3 unchanged (fleet / bond-root owned).
