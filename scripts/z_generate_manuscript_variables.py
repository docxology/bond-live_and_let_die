#!/usr/bin/env python3
"""SAN MONIQUE — hydrate manuscript variables and resolve the section tree.

Strict by default: any unresolved {{TOKEN}} fails. Generates
output/data/manuscript_variables.json and copies resolved sections to
output/manuscript/. Pass --allow-draft to relax strictness.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))  # noqa: E402

from live_and_let_die.manuscript_variables import (  # noqa: E402
    generate_variables,
    resolve_manuscript_tree,
)


def main() -> int:
    allow_draft = "--allow-draft" in sys.argv[1:]
    variables = generate_variables(require_outputs=not allow_draft)

    data_dir = ROOT / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    data_target = data_dir / "manuscript_variables.json"
    data_target.write_text(json.dumps(variables, sort_keys=True, indent=2), encoding="utf-8")

    resolved_dir, files = resolve_manuscript_tree(variables, strict=not allow_draft)
    print(f"wrote {data_target}")
    print(f"resolved {len(files)} sections -> {resolved_dir}")
    for name in files:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
