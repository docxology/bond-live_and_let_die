# Manuscript — LIVE AND LET DIE / SAN MONIQUE

Fully generated manuscript. `config.yaml` holds identity + mission metadata;
numbered sections `[0-9]*.md` use `{{TOKEN}}` placeholders hydrated by
`src/live_and_let_die/manuscript_variables.py`.

| File | Role |
| --- | --- |
| `config.yaml` | Paper + mission metadata (single config source) |
| `preamble.md` | Render preamble (sidecar, not token-scanned) |
| `00_abstract.md` … `07_scope_and_related_work.md`, `99_references.md` | Numbered sections (token-scanned, resolved to `output/manuscript/`) |
| `references.bib` | Bibliography records |
| `SYNTAX.md` / `AGENTS.md` / `README.md` / `layer_contract.yaml` | Sidecars (reference only) |

See `SYNTAX.md` for token conventions.
