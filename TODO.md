# TODO — LIVE AND LET DIE / SAN MONIQUE

Genuinely remaining work. Completed build history is not tracked here — the code
is the record, and `docs/architecture.md` describes what exists. Items are listed
because someone still has to do them.

## Open — inside this package

- **`SAN_MONIQUE_MESSAGE` is misnamed.** It is a *function* in `coded_comms.py`
  wearing a constant's name (upper case). It is exported in the module's
  `__all__` but consumed by no production code — not `mission.py`, not
  `__init__.py`; only `tests/test_coded_comms.py::test_san_monique_message_constant`
  calls it. Either rename it to `san_monique_message()` or drop it; both are
  breaking changes to the module's public names, so do it deliberately rather
  than as a drive-by.
- **Unreachable strict-mode guard.** `manuscript_variables.generate_variables`
  raises when `require_outputs` is set and the supply analysis is empty, but
  `analyze_san_monique()` cannot return an empty dict, so the branch is dead and
  permanently uncovered. Either give `--allow-draft` a path that can actually
  produce a partial analysis, or remove the guard and the parameter with it.
- **Two partial branches with no reachable false path** —
  `interdiction.py:115->111` and `manuscript_variables.py:103->105`. Both are loop
  or membership guards that hold for every canonical input. Harmless, but they
  are the shape a vacuous condition takes; if either module grows a dataset with
  no infinite-cost terrain or an empty severable set, add the case.
- **`island_ops.py` is now the coverage floor** (95.81%). The uncovered lines are
  the stale-heap-entry `continue` in both Dijkstra loops — reachable in principle
  but not on any canonical or test grid. Not a claim about anything; left alone
  rather than papered over with a contrived grid.
- **The min-cut classification is only asserted on one instance.** The canonical
  cut is entirely virtual, so `min_cut_is_demand_limited` is True and the
  *transit-limited* branch of that report field is never exercised end-to-end.
  `classify_cut_edges` itself has a positive control, but a second canonical
  dataset whose cut falls on a physical leg would bind the reporting path too.

## Open — needs a decision outside this package

- **Mission objectives vs. domain modules.** `brief()` declares three objectives
  while six domain modules run in `execute()`; `plan()` indexes
  `objectives[0..2]`. Widening the objective list is safe *within* this package
  but changes what a coordinator sees in a `MissionBrief`, so it needs a fleet
  decision, not a local one. Until then `{{LALD_NUM_OBJECTIVES}}` reports the
  configured count honestly rather than pretending it is six.
- **Provenance persistence.** Gadget payloads are opaque callables. When
  `bond-utilities` ships `mission_io.record_provenance_outcome`, `execute()` can
  additionally persist through it. The pure core needs no change.
- **Manuscript rendering.** Sections hydrate to `output/manuscript/` and embed
  their three figures at `{{LALD_FIGURE_DIR}}/*.png`, which resolves correctly
  from that directory. Whether the suite's Pandoc PDF pipeline runs from
  `output/manuscript/` (it must, for those paths to hold) or supplies its own
  `--resource-path` is a shared follow-up owned at the bond root, not here.

## Not open (deliberate, do not "fix")

- **No mocks anywhere**, including for matplotlib and the subprocess CLIs. Real
  rendering into `tmp_path` is the test.
- **`wall_time_s` is fixed at `0.0`.** Artifacts must not carry a clock, or the
  provenance record stops being reproducible.
- **`MISSION_SEED = 8` with no random draws.** The seed is recorded for suite
  parity, not consumed — every result is deterministic without it.
- **The economic parameters are invented, and the docs say so.** Do not
  "improve" `EDGE_ECONOMICS`, `FARM_GATE_PRICE`, `RETAIL_MARKUP` or
  `RETAIL_DILUTION` by attributing them to Reuter & Kleiman or Caulkins &
  Reuter. Those papers motivate the question; they did not supply these numbers,
  and claiming otherwise is the exact overclaim §Scope now rules out. Either
  genuinely calibrate against a cited table — and then say which one — or leave
  the disclosure alone.
- **The frequency attack is allowed to fail.** `solve_substitution` does not
  recover the 27-character intercept, and two tests pin that. Do not tune the
  reference distribution to make it "work" on this one string; do not soften the
  docstring. If a longer corpus is ever added, demonstrate recovery there.

## Verification

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/ && uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
rg -n "template[_]code_project" .   # expectation: zero
```
