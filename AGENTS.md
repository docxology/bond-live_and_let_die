# AGENTS.md — LIVE AND LET DIE / SAN MONIQUE

This is a PROJECT BOND film package (codename **SAN MONIQUE**) implementing the
FROZEN BOND-API mission protocol over a pure, deterministic domain core.

## Build

```bash
uv sync --extra dev        # deps incl. the vendored bond-api (vendor/bond-api)
```

`bond-api` is a local path dependency declared in `pyproject.toml`
(`[tool.uv.sources]`) and resolved against the copy recorded in
`vendor/bond-api`; `scripts/vendor.py --check` verifies every recorded digest
offline, and `tests/test_vendor_provenance.py` runs that inside the suite — no
sibling checkout is needed. If `uv` reports `Failed to initialize cache`, the
sandbox is blocking its cache directory; re-run outside the sandbox.

## Test

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90     # the gate: 90% line+branch on src/
uv run pytest tests/test_supply_graph.py -v            # one module
uv run pytest tests/ -k interdiction -v                # one topic
```

Measured counts and per-module coverage live in
[`docs/_generated/COUNTS.md`](docs/_generated/COUNTS.md) — regenerate from a real
run rather than quoting a figure from memory.

## Verify (run all of these before declaring done)

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/
uv run python scripts/00_preflight.py          # protocol conformance + full run
rg -n "template[_]code_project" .              # expectation: zero
git status --short                             # clean after your commit(s)
```

Read the output, not just the exit code. After changing the domain core,
regenerate artifacts so `output/` reflects the code:

```bash
uv run python scripts/generate_figures.py
uv run python scripts/z_generate_manuscript_variables.py
```

## Layer contract

- **Pure core** — `supply_graph.py`, `interdiction.py`, `coded_comms.py`,
  `voodoo_drums.py`, `market_flow.py`, `island_ops.py`: stdlib only. No
  `infrastructure.*`, no `bond_api`. Importable in isolation.
- **`mission.py`** is the *only* `bond_api` importer: the thin protocol adapter.
  It orchestrates the core and stamps provenance; it holds no algorithms.
- **`manuscript_variables.py`** hydrates manuscript tokens from
  `manuscript/config.yaml` + the pure core.
- **`figures/plots.py`** renders three deterministic figures.
- **`scripts/`** are thin orchestrators only: `sys.path` bootstrap, one call into
  `src/`, print, `raise SystemExit(main())`. Verification checks there use
  explicit `if ...: return 1` — never bare `assert`, which `python -O` strips.

## Protocol stability

`src/live_and_let_die/mission.py` exposes `MissionProvider` (film
`live_and_let_die`, codename `SAN MONIQUE`) at module top level with
`brief`/`recon`/`plan`/`execute`/`debrief`, plus `GADGET_REGISTRY` and
`register_gadgets(registry=None)`. **Do not change this public shape** —
bond-cli, the coordinator reconcile, and the orchestrator consume it across
packages. Deepen inside the package (new modules, richer `execute` internals),
never by breaking discovery.

## Behavior notes

- **Deterministic**: fixed provenance seed 8, no random draws anywhere, zero
  wall-clock in artifacts, canonical SHA-256 input hash covering the graph,
  ciphers, drum message, terrain, route endpoints, and per-leg economics.
  "Zero wall-clock" is literal and gated: no module under `src/` may call
  `datetime.now`, `date.today`, or `time.time`, because the manuscript
  artifacts (`output/data/manuscript_variables.json` and `output/manuscript/`)
  must regenerate byte-for-byte. The manuscript's publication date is
  `paper.date` in `manuscript/config.yaml` — a committed value you bump by
  hand. If you need a real timestamp, it goes in a run-scoped record outside
  those two paths, and you amend the scope statement in
  `manuscript/06_reproducibility.md` to say so. Gates:
  `tests/test_scripts_smoke.py::test_regeneration_is_byte_identical` plus the
  two determinism tests in `tests/test_manuscript_variables.py`.
- **No mock framework**: real data and real computation only.
- **Derive, never type**: any value the code can compute is interpolated —
  including figure captions, `Asset` payloads, and `Finding` details. A literal
  there silently rots when the dataset moves.
- Do not change the FROZEN bond-api protocol types; code against them.

## Reading order for agents

1. [`docs/agent_instructions.md`](docs/agent_instructions.md) — operational constraints & verification.
2. [`docs/architecture.md`](docs/architecture.md) — module-by-module design and the MissionProvider mapping.
3. [`docs/testing_philosophy.md`](docs/testing_philosophy.md) — how tests are written here.
4. [`manuscript/SYNTAX.md`](manuscript/SYNTAX.md) — manuscript token conventions.
5. [`TODO.md`](TODO.md) — what is actually left.
