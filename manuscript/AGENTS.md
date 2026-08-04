# AGENTS.md — manuscript

- Metrics are injected from `config.yaml` + `../src/live_and_let_die/manuscript_variables.py`;
  never hand-author metrics in prose.
- Only numbered sections (`[0-9]*.md`) are token-scanned and copied to
  `output/manuscript/`; sidecars (`SYNTAX.md`, `AGENTS.md`, `README.md`,
  `preamble.md`, `layer_contract.yaml`) are reference docs and may show literal
  placeholder examples.
- Every `{{TOKEN}}` used in a numbered section must exist in `generate_variables()`.
- Keep `references.bib` keyed and cited via `99_references.md`.
