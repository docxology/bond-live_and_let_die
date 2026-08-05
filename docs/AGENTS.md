# AGENTS.md — working inside the SAN MONIQUE package

How an agent should operate in this package. Read this before editing anything;
it is the shortest path from "I have a task" to "I changed the right file and
proved it".

## 1. Read in this order

1. [`agent_instructions.md`](agent_instructions.md) — the hard constraints. Scope,
   determinism, no-mocks, the frozen protocol, and the verification checklist.
2. [`architecture.md`](architecture.md) — which module owns what. Read this
   *before* deciding where your change goes; putting domain logic in the wrong
   layer is the most common defect in this fleet.
3. [`testing_philosophy.md`](testing_philosophy.md) — how to write a test that
   actually binds behaviour here.
4. [`../manuscript/SYNTAX.md`](../manuscript/SYNTAX.md) — only if your change
   touches a number that appears in the manuscript (it usually does).

## 2. Decide where the change belongs

| If you are... | It goes in |
| --- | --- |
| Adding or changing an algorithm | a pure module in `src/live_and_let_die/` (no `bond_api`, no `infrastructure.*`) |
| Exposing an algorithm to the fleet | the `register_gadgets` map in `mission.py` — never a new top-level symbol |
| Enriching what a mission reports | `run_analysis()` in `mission.py`, keeping the protocol methods' signatures fixed |
| Reporting a new number in the manuscript | `generate_variables()` in `manuscript_variables.py`, then reference the `{{TOKEN}}` in prose |
| Adding a CLI entry point | a thin wrapper in `scripts/` — `sys.path` bootstrap, call into `src/`, print, `raise SystemExit(main())`. No logic. |
| Adding a figure | `figures/plots.py`, then wire it into `scripts/generate_figures.py` (a figure the generator never renders is a documentation lie) |

## 3. Never do these

- **Never change the public shape of `mission.py`.** `MissionProvider` with
  `brief`/`recon`/`plan`/`execute`/`debrief`, `GADGET_REGISTRY`, and
  `register_gadgets` are consumed by `bond-cli`, `bond-coordinator`, and
  `bond-orchestrator` across all 27 film packages.
- **Never hand-author a metric.** Not in the manuscript, not in a figure title,
  not in a `Finding` or `Asset` payload. Derive it, or it will silently rot when
  the dataset moves. (This has already happened here once — see `TODO.md`.)
- **Never use a mock.** No `unittest.mock`, `MagicMock`, or `mocker.patch`.
- **Never use a bare `assert` as a verification gate in `scripts/`.** `python -O`
  strips asserts and the gate becomes an unconditional pass.
- **Never touch a sibling package**, the bond root, or the template repo.

## 4. Prove it

Run the full checklist in [`agent_instructions.md`](agent_instructions.md) and
read the output — not just the exit code. Then refresh
[`_generated/COUNTS.md`](_generated/COUNTS.md) from the numbers you actually
measured. That file is generated evidence: regenerate it, never hand-edit it,
and never quote a coverage figure elsewhere that you did not just observe.
