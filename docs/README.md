# Docs — LIVE AND LET DIE / SAN MONIQUE

Agent- and maintainer-facing documentation for the SAN MONIQUE film package:
one of the 27 film packages in the PROJECT BOND suite, implementing the frozen
`bond_api.MissionProvider` protocol over a pure, deterministic domain core.

This directory explains *how the package is built and how to work in it*. It is
not the research write-up — that is `../manuscript/`, whose every metric is a
`{{TOKEN}}` computed by `src/live_and_let_die/manuscript_variables.py`.

## What is here

| File | Purpose |
| --- | --- |
| [`agent_instructions.md`](agent_instructions.md) | The operational contract: hard constraints (scope, determinism, no-mocks, frozen protocol), what may and may not change, and the verification checklist to run before declaring done |
| [`architecture.md`](architecture.md) | Module-by-module architecture of `src/`: what each of the six domain modules computes, how they compose, and exactly how `mission.py` implements the frozen `MissionProvider` |
| [`testing_philosophy.md`](testing_philosophy.md) | Why there are no mocks, how determinism makes exact assertions possible, what each test file binds, and the anti-patterns this suite rejects |
| [`AGENTS.md`](AGENTS.md) | Read-order and working protocol for an agent entering this directory |
| [`_generated/COUNTS.md`](_generated/COUNTS.md) | Measured test count and per-module coverage — regenerated from a real run, never hand-edited |

## Where the rest of the truth lives

| Question | Authority |
| --- | --- |
| What does this package do, and how do I run it? | [`../README.md`](../README.md) |
| Build / test / verify commands | [`../AGENTS.md`](../AGENTS.md) |
| What work is genuinely left? | [`../TODO.md`](../TODO.md) |
| Manuscript token conventions | [`../manuscript/SYNTAX.md`](../manuscript/SYNTAX.md) |
| Layer + scope rules for the whole fleet | the suite's `SCOPE.md` at the bond root |

## The one rule that outranks the others

The public shape of `src/live_and_let_die/mission.py` — `MissionProvider` with
`brief` / `recon` / `plan` / `execute` / `debrief`, plus `GADGET_REGISTRY` and
`register_gadgets` — is **frozen**. `bond-cli`, `bond-coordinator`, and
`bond-orchestrator` discover and drive it across all 27 film packages. Deepen
*inside* the package; never change the surface they consume.
