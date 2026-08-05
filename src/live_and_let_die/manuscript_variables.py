"""Manuscript variable hydration for LIVE AND LET DIE / SAN MONIQUE.

Every ``{{TOKEN}}`` in ``manuscript/[0-9]*.md`` resolves through
:func:`generate_variables`, which reads ``manuscript/config.yaml`` and computes
every metric from the pure domain core (:func:`live_and_let_die.mission.run_analysis`).
Metrics are never hand-authored in prose — they flow through this module so the
manuscript cannot drift from the code.

The consuming orchestrator is ``scripts/z_generate_manuscript_variables.py``
(thin wrapper); the live cross-reference gate lives in
``tests/test_manuscript_variables.py``.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from live_and_let_die.mission import (
    CODENAME,
    FILM,
    input_digest,
    run_analysis,
)
from live_and_let_die.supply_graph import SUPER_SINK, SUPER_SOURCE

__all__ = ["generate_variables", "load_manuscript_config", "resolve_manuscript_tree"]

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PACKAGE_ROOT / "manuscript" / "config.yaml"

_TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")


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


def generate_variables(
    *,
    config_path: str | Path | None = None,
    require_outputs: bool = True,
    now: datetime | None = None,
) -> dict[str, str]:
    """Compute the ``{{TOKEN}}`` -> value mapping for the manuscript.

    Args:
        config_path: Override for ``manuscript/config.yaml``.
        require_outputs: When True (default), require the analysis report to
            populate — the strict-mode gate.
        now: Optional timestamp override for deterministic tests.
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

    stamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat(timespec="seconds")
    greedy = interdict["greedy"]
    exact = interdict["exact"]
    top_target = interdict["efficiency_ranking"][0]
    ranking_leg = top_target["leg"]
    ranking_drop = top_target["reduction"]
    markets = sorted(market["markets"])
    return {
        "LALD_IDENTITY": str(paper.get("identity", FILM)),
        "LALD_CODENAME": str(paper.get("codename", CODENAME)),
        "LALD_YEAR": str(paper.get("year", "1973")),
        "LALD_VERSION": str(paper.get("version", "")),
        "LALD_TITLE": str(paper.get("title", "")),
        "LALD_SUBTITLE": str(paper.get("subtitle", "")),
        "LALD_NUM_OBJECTIVES": "3",
        "LALD_MISSION_PHASES": "brief, recon, plan, execute, debrief",
        "LALD_SUPPLY_NODES": str(supply["nodes"]),
        "LALD_SUPPLY_EDGES": str(supply["edges"]),
        "LALD_MARKETS": ", ".join(supply["markets"]),
        "LALD_SHORTEST_MIAMI": f"{supply['shortest_path_miami'][0]:.0f}",
        "LALD_SHORTEST_MIAMI_PATH": _join_path(supply["shortest_path_miami"][1]),
        "LALD_SHORTEST_NYC": f"{supply['shortest_path_new_york'][0]:.0f}",
        "LALD_SHORTEST_NYC_PATH": _join_path(supply["shortest_path_new_york"][1]),
        "LALD_MAX_FLOW": f"{supply['max_flow_total']:.0f}",
        "LALD_MIN_CUT": f"{supply['min_cut_value']:.0f}",
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
        # Ops
        "LALD_ROUTE_COST": f"{ops['route_cost']:.0f}",
        "LALD_CROCODILE_CELLS": str(ops["crocodile_cells"]),
        "LALD_ROUTE_MOVES": str(ops["movement_cells"]),
        "LALD_ROUTE_START": f"({ops['start'][0]},{ops['start'][1]})",
        "LALD_ROUTE_GOAL": f"({ops['goal'][0]},{ops['goal'][1]})",
        "LALD_INPUT_HASH": input_digest()[:16],
        "GENERATION_TIMESTAMP": stamp,
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
    output_dir = Path(output_dir) if output_dir is not None else PACKAGE_ROOT / "output" / "manuscript"
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
