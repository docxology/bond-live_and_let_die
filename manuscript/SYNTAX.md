# Manuscript syntax

This manuscript uses Pandoc-style markdown with `{{TOKEN}}` placeholders.

- Every metric is a `{{UPPERCASE_TOKEN}}` resolved by
  `src/live_and_let_die/manuscript_variables.py` from the pure domain core.
- Only `[0-9]*.md` section files are rendered and token-checked; sidecars
  (`SYNTAX.md`, `AGENTS.md`, `README.md`, `preamble.md`) are reference docs and
  may show literal placeholder examples.
- Config lives in `manuscript/config.yaml` (`paper:` + `mission:` blocks).
- Citations use `references.bib` keys (see `99_references.md`).
- Inline code uses single backticks; math can use `$...$` where the renderer
  requires.
