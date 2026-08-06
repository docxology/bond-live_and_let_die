"""Manuscript variable hydration for LIVE AND LET DIE / SAN MONIQUE.

Every ``{{TOKEN}}`` in ``manuscript/[0-9]*.md`` resolves through
:func:`generate_variables`, which reads ``manuscript/config.yaml`` and computes
every metric from the pure domain core (:func:`live_and_let_die.mission.run_analysis`).
Metrics are never hand-authored in prose — they flow through this module so the
manuscript cannot drift from the code.

The consuming orchestrator is ``scripts/z_generate_manuscript_variables.py``
(thin wrapper); the live cross-reference gate lives in
``tests/test_manuscript_variables.py``.

**No wall clock.** Everything this module emits is persisted — into
``output/data/manuscript_variables.json`` and every resolved section under
``output/manuscript/`` — and those bytes are covered by the byte-identical
regeneration claim in ``manuscript/06_reproducibility.md``. So every value here
comes from a committed source: the domain core, or ``manuscript/config.yaml``.
The manuscript date is ``paper.date`` in that config, never ``datetime.now``.
Until 2026-08-05 this module stamped ``GENERATION_TIMESTAMP`` from the system
clock, which made every regeneration differ; the gates are
``tests/test_manuscript_variables.py::test_regenerating_variables_across_a_wall_clock_second_is_identical``
and ``tests/test_scripts_smoke.py::test_regeneration_is_byte_identical``.
"""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from live_and_let_die.coded_comms import ALPHABET
from live_and_let_die.island_ops import SAN_MONIQUE_TERRAIN, TERRAIN_COSTS, TERRAIN_NAMES, TerrainGrid
from live_and_let_die.mission import (
    CODENAME,
    FILM,
    GADGET_REGISTRY,
    MISSION_SEED,
    input_digest,
    run_analysis,
)
from live_and_let_die.supply_graph import SUPER_SINK, SUPER_SOURCE
from live_and_let_die.voodoo_drums import DASH, DOT, GAP_INTRA, GAP_LETTER, GAP_WORD

__all__ = [
    "domain_modules",
    "generate_variables",
    "load_manuscript_config",
    "resolve_manuscript_tree",
]

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PACKAGE_ROOT / "manuscript" / "config.yaml"
DEFAULT_MANUSCRIPT_OUTPUT_DIR = PACKAGE_ROOT / "output" / "manuscript"
DEFAULT_FIGURE_DIR = PACKAGE_ROOT / "output" / "figures"

#: Figure directory as seen *from the resolved manuscript*, derived from the two
#: real paths rather than typed. Prose embeds figures as
#: ``![caption]({{LALD_FIGURE_DIR}}/name.png)`` so the rendered section carries a
#: path that actually resolves; ``tests/test_manuscript_variables.py`` opens
#: every embedded path and fails if one is missing.
FIGURE_DIR_RELATIVE = os.path.relpath(DEFAULT_FIGURE_DIR, DEFAULT_MANUSCRIPT_OUTPUT_DIR)

_TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")

#: Modules that are *not* part of the pure domain core: the protocol adapter,
#: this hydration module, and the package marker.
_NON_DOMAIN_MODULES = frozenset({"__init__", "mission", "manuscript_variables"})


def domain_modules() -> tuple[str, ...]:
    """Names of the pure domain-core modules, discovered from the package dir.

    Derived rather than listed, so adding a domain module updates the manuscript
    count without anyone remembering to edit prose. ``mission.py`` (the protocol
    adapter), this module, and ``__init__.py`` are excluded; ``figures/`` is a
    rendering subpackage, not a domain module.
    """
    package_dir = Path(__file__).resolve().parent
    return tuple(sorted(path.stem for path in package_dir.glob("*.py") if path.stem not in _NON_DOMAIN_MODULES))


def load_manuscript_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load and validate ``manuscript/config.yaml`` (or an explicit path)."""
    path = Path(config_path) if config_path is not None else DEFAULT_CONFIG_PATH
    if not path.is_file():
        raise FileNotFoundError(f"manuscript config not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"manuscript config must be a top-level mapping, got {type(data).__name__}")
    return data


def _join_path(segments: list[str]) -> str:
    return " -> ".join(segments)


def _terrain_cost_table() -> str:
    """Render the terrain cost legend from :data:`TERRAIN_COSTS` (never typed).

    Finite costs are grouped so equal-cost terrains read naturally ("road /
    open ground / beach cost 1"); impassable glyphs are named as such.
    """
    grouped: dict[float, list[str]] = {}
    for glyph, cost in TERRAIN_COSTS.items():
        grouped.setdefault(cost, []).append(TERRAIN_NAMES[glyph])
    parts: list[str] = []
    for cost in sorted(c for c in grouped if c != float("inf")):
        parts.append(f"{' / '.join(grouped[cost])} cost {cost:.0f}")
    if float("inf") in grouped:
        parts.append(f"{' / '.join(grouped[float('inf')])} infinite")
    return ", ".join(parts)


def _mission_objectives(config: dict[str, Any]) -> list[str]:
    """The declared mission objectives from ``manuscript/config.yaml``."""
    mission = config.get("mission", {})
    if not isinstance(mission, dict):
        raise ValueError("manuscript config 'mission' section must be a mapping")
    objectives = mission.get("objectives", [])
    if not isinstance(objectives, list):
        raise ValueError("manuscript config 'mission.objectives' must be a list")
    return [str(item) for item in objectives]


def _manuscript_date(paper: dict[str, Any]) -> str:
    """The manuscript's publication date, read from the committed ``paper`` block.

    Deliberately *not* a wall clock. This value is written into
    ``output/data/manuscript_variables.json`` and into the resolved abstract's
    front matter, both of which the reproducibility section claims regenerate
    byte-for-byte — so it must come from a source that is committed and does
    not move between runs. ``paper.date`` in ``manuscript/config.yaml`` is that
    source; it is required, because a silent default would put an
    unprovenanced date on the manuscript.
    """
    raw = paper.get("date")
    if raw is None:
        raise ValueError("manuscript config 'paper.date' is required — a committed ISO date, e.g. 2026-08-05")
    if isinstance(raw, date):  # YAML parses a bare ``2026-08-05`` into a date
        return raw.isoformat()
    try:
        return date.fromisoformat(str(raw).strip()).isoformat()
    except ValueError as exc:
        raise ValueError(f"manuscript config 'paper.date' must be an ISO date (YYYY-MM-DD), got {raw!r}") from exc


def generate_variables(
    *,
    config_path: str | Path | None = None,
    require_outputs: bool = True,
) -> dict[str, str]:
    """Compute the ``{{TOKEN}}`` -> value mapping for the manuscript.

    The mapping is a pure function of committed inputs (the domain core plus
    ``manuscript/config.yaml``): calling it twice, any distance apart in time,
    returns an equal dict. Nothing here reads the system clock.

    Args:
        config_path: Override for ``manuscript/config.yaml``.
        require_outputs: When True (default), require the analysis report to
            populate — the strict-mode gate.
    """
    config = load_manuscript_config(config_path)
    paper = config.get("paper", {})
    if not isinstance(paper, dict):
        raise ValueError("manuscript config 'paper' section must be a mapping")

    analysis = run_analysis()
    supply = analysis["supply"]
    comms = analysis["comms"]
    ops = analysis["ops"]
    interdict = analysis["interdiction"]
    drums = analysis["drums"]
    market = analysis["market"]
    if require_outputs and not supply:
        raise ValueError("supply analysis produced no output — cannot hydrate manuscript")

    manuscript_date = _manuscript_date(paper)
    greedy = interdict["greedy"]
    exact = interdict["exact"]
    top_target = interdict["efficiency_ranking"][0]
    ranking_leg = top_target["leg"]
    ranking_drop = top_target["reduction"]
    markets = sorted(market["markets"])
    terrain = TerrainGrid(SAN_MONIQUE_TERRAIN)
    return {
        "LALD_IDENTITY": str(paper.get("identity", FILM)),
        "LALD_CODENAME": str(paper.get("codename", CODENAME)),
        "LALD_YEAR": str(paper.get("year", "1973")),
        "LALD_VERSION": str(paper.get("version", "")),
        "LALD_TITLE": str(paper.get("title", "")),
        "LALD_SUBTITLE": str(paper.get("subtitle", "")),
        "LALD_NUM_OBJECTIVES": str(len(_mission_objectives(config))),
        "LALD_MISSION_PHASES": "brief, recon, plan, execute, debrief",
        "LALD_FIGURE_DIR": FIGURE_DIR_RELATIVE,
        # Configuration constants: reported through tokens so a change to the
        # code moves the prose with it (no hand-authored constants either).
        "LALD_SEED": str(MISSION_SEED),
        "LALD_MODULE_COUNT": str(len(domain_modules())),
        "LALD_GADGET_COUNT": str(len(GADGET_REGISTRY.gadgets_for(FILM))),
        "LALD_ALPHABET_SIZE": str(len(ALPHABET)),
        "LALD_TERRAIN_ROWS": str(terrain.nrows),
        "LALD_TERRAIN_COLS": str(terrain.ncols),
        "LALD_TERRAIN_SHAPE": f"{terrain.nrows}x{terrain.ncols}",
        "LALD_TERRAIN_COSTS": _terrain_cost_table(),
        "LALD_DRUM_TIMING": (
            f"dot = {DOT} sounding beat, dash = {DASH}; intra-letter gap "
            f"{GAP_INTRA}, inter-letter gap {GAP_LETTER}, inter-word gap {GAP_WORD}"
        ),
        "LALD_SUPPLY_NODES": str(supply["nodes"]),
        "LALD_SUPPLY_EDGES": str(supply["edges"]),
        "LALD_MARKETS": ", ".join(supply["markets"]),
        "LALD_SHORTEST_MIAMI": f"{supply['shortest_path_miami'][0]:.0f}",
        "LALD_SHORTEST_MIAMI_PATH": _join_path(supply["shortest_path_miami"][1]),
        "LALD_SHORTEST_NYC": f"{supply['shortest_path_new_york'][0]:.0f}",
        "LALD_SHORTEST_NYC_PATH": _join_path(supply["shortest_path_new_york"][1]),
        "LALD_MAX_FLOW": f"{supply['max_flow_total']:.0f}",
        "LALD_MIN_CUT": f"{supply['min_cut_value']:.0f}",
        "LALD_MIN_CUT_EDGES": ", ".join(f"{s}→{d}" for s, d in supply["min_cut_edges"]),
        "LALD_MIN_CUT_PHYSICAL_COUNT": str(len(supply["min_cut_physical_edges"])),
        "LALD_MIN_CUT_LIMIT": ("demand-limited" if supply["min_cut_is_demand_limited"] else "transit-limited"),
        "LALD_BOTTLENECK": supply["critical_transit_node"],
        "LALD_DISRUPTION": f"{supply['disruption_units']:.0f}",
        "LALD_SUPPLY_SOURCE": SUPER_SOURCE,
        "LALD_SUPPLY_SINK": SUPER_SINK,
        # Interdiction
        "LALD_BUDGET": str(interdict["budget"]),
        "LALD_BASE_FLOW": f"{interdict['base_flow']:.0f}",
        "LALD_GREEDY_SEVERED": ", ".join(f"{s}→{d}" for s, d in greedy["severed"]),
        "LALD_GREEDY_REDUCTION": f"{greedy['reduction']:.0f}",
        "LALD_GREEDY_CE": f"{greedy['cost_effectiveness']:.0f}",
        "LALD_REMAINING_FLOW": f"{greedy['remaining_flow']:.0f}",
        "LALD_EXACT_SEVERED": ", ".join(f"{s}→{d}" for s, d in exact["severed"]),
        "LALD_EXACT_REDUCTION": f"{exact['reduction']:.0f}",
        "LALD_EFFICIENCY_TOP_LEG": f"{ranking_leg[0]}→{ranking_leg[1]}",
        "LALD_EFFICIENCY_TOP_DROP": f"{ranking_drop:.0f}",
        # Drum / comms
        "LALD_KEYWORD": comms["keyword"],
        "LALD_PLAINTEXT": comms["plaintext"],
        "LALD_CIPHERTEXT": comms["ciphertext"],
        "LALD_DRUM_MESSAGE": drums["plaintext"],
        "LALD_DRUM_DECODED": drums["decoded"],
        "LALD_DRUM_ROUNDTRIP": "exact" if drums["roundtrip_exact"] else "inexact",
        "LALD_DRUM_BEATS": str(drums["beats"]),
        "LALD_DRUM_DENSITY": f"{drums['density']:.3f}",
        "LALD_DRUM_LONGEST": str(drums["longest_run"]),
        # Market economics
        "LALD_FARM_GATE_PRICE": f"{market['farm_gate_price']:.0f}",
        "LALD_MIAMI_STREET_PRICE": f"{market['markets']['miami']['street_price']:.0f}",
        "LALD_MIAMI_STREET_PURITY": f"{market['markets']['miami']['street_purity'] * 100:.0f}%",
        "LALD_NYC_STREET_PRICE": f"{market['markets']['new_york']['street_price']:.0f}",
        "LALD_NYC_STREET_PURITY": f"{market['markets']['new_york']['street_purity'] * 100:.0f}%",
        "LALD_AVG_STREET_PRICE": f"{market['avg_street_price']:.0f}",
        "LALD_PRODUCER_SHARE": f"{market['producer_share'] * 100:.1f}%",
        "LALD_SPREAD_RATIO": f"{market['spread_ratio']:.0f}",
        "LALD_TOTAL_REVENUE": f"{market['total_revenue']:.0f}",
        "LALD_MARKET_COUNT": str(len(markets)),
        "LALD_MIAMI_REVENUE": f"{market['markets']['miami']['revenue']:.0f}",
        "LALD_NYC_REVENUE": f"{market['markets']['new_york']['revenue']:.0f}",
        "LALD_MIAMI_DEMAND": f"{market['markets']['miami']['demand']:.0f}",
        "LALD_NYC_DEMAND": f"{market['markets']['new_york']['demand']:.0f}",
        "LALD_TOTAL_DEMAND": f"{market['markets']['miami']['demand'] + market['markets']['new_york']['demand']:.0f}",
        # Ops
        "LALD_ROUTE_COST": f"{ops['route_cost']:.0f}",
        "LALD_CROCODILE_CELLS": str(ops["crocodile_cells"]),
        "LALD_MIN_CROCODILE_CELLS": str(ops["min_crocodile_cells"]),
        "LALD_ROUTE_MOVES": str(ops["movement_cells"]),
        "LALD_ROUTE_START": f"({ops['start'][0]},{ops['start'][1]})",
        "LALD_ROUTE_GOAL": f"({ops['goal'][0]},{ops['goal'][1]})",
        "LALD_INPUT_HASH": input_digest()[:16],
        "LALD_MANUSCRIPT_DATE": manuscript_date,
    }


def resolve_manuscript_tree(
    variables: dict[str, str],
    *,
    manuscript_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    strict: bool = True,
) -> tuple[Path, list[str]]:
    """Copy each manuscript section to ``output/manuscript/``, substituting tokens.

    Only ``NN_*.md`` section files are copied (not sidecars). In strict mode a
    leftover ``{{TOKEN}}`` fails resolution. Returns the output dir and the
    sorted list of resolved file names.
    """
    manuscript_dir = Path(manuscript_dir) if manuscript_dir is not None else PACKAGE_ROOT / "manuscript"
    output_dir = Path(output_dir) if output_dir is not None else DEFAULT_MANUSCRIPT_OUTPUT_DIR
    resolved: list[str] = []
    for source in sorted(manuscript_dir.glob("[0-9][0-9]_*.md")):
        text = source.read_text(encoding="utf-8")
        for token, value in variables.items():
            text = text.replace("{{" + token + "}}", value)
        unresolved = sorted(set(_TOKEN_RE.findall(text)))
        if unresolved and strict:
            raise ValueError(f"unresolved manuscript tokens in {source.name}: {unresolved}")
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / source.name).write_text(text, encoding="utf-8")
        resolved.append(source.name)
    return output_dir, resolved
