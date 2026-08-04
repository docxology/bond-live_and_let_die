"""LIVE AND LET DIE (1973) — SAN MONIQUE · PROJECT BOND film package.

Pure domain core for special-agent mission software on Kananga's San Monique:

* :mod:`live_and_let_die.supply_graph` — narcotics supply-graph analytics
  (production -> transit -> market): shortest paths, max flow / min cut, and
  critical-transit disruption analysis.
* :mod:`live_and_let_die.coded_comms` — voodoo-coded message deciphering via
  keyword (symbol-substitution) ciphers and frequency-attack solving.
* :mod:`live_and_let_die.island_ops` — Caribbean island ops planning over a
  mangrove / crocodile terrain grid.
* :mod:`live_and_let_die.mission` — the BOND-API ``MissionProvider`` adapter
  (codename SAN MONIQUE) that layers the frozen protocol over the domain core.

The domain modules are infrastructure-free and importable without ``bond_api``;
``mission.py`` is the thin protocol adapter.
"""

from __future__ import annotations

from live_and_let_die.coded_comms import (
    ALPHABET,
    ENGLISH_FREQUENCIES,
    KEYWORD,
    SAN_MONIQUE_PLAINTEXT,
    build_keyword_key,
    decipher,
    encipher,
    frequency_table,
    invert_key,
    score_plaintext,
    solve_substitution,
)
from live_and_let_die.island_ops import (
    ROUTE_GOAL,
    ROUTE_START,
    SAN_MONIQUE_TERRAIN,
    TERRAIN_COSTS,
    TerrainGrid,
    plan_san_monique_route,
)
from live_and_let_die.supply_graph import (
    SAN_MONIQUE_GRAPH,
    SUPER_SINK,
    SUPER_SOURCE,
    SupplyGraph,
    analyze_san_monique,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "ALPHABET",
    "KEYWORD",
    "ENGLISH_FREQUENCIES",
    "SAN_MONIQUE_PLAINTEXT",
    "build_keyword_key",
    "decipher",
    "encipher",
    "frequency_table",
    "invert_key",
    "score_plaintext",
    "solve_substitution",
    "SAN_MONIQUE_GRAPH",
    "SUPER_SOURCE",
    "SUPER_SINK",
    "SupplyGraph",
    "analyze_san_monique",
    "TerrainGrid",
    "SAN_MONIQUE_TERRAIN",
    "ROUTE_START",
    "ROUTE_GOAL",
    "TERRAIN_COSTS",
    "plan_san_monique_route",
]
