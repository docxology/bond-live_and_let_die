"""Shared test configuration for the SAN MONIQUE package.

Sets a headless matplotlib backend before any rendering import, and makes the
package root and ``src/`` importable from tests regardless of the installed
entry point.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Headless: tests must never open a display window.
os.environ.setdefault("MPLBACKEND", "Agg")

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
for _path in (str(PACKAGE_ROOT), str(PACKAGE_ROOT / "src")):
    if _path not in sys.path:
        sys.path.insert(0, _path)
