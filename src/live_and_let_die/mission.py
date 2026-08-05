"""SAN MONIQUE — the BOND-API MissionProvider adapter for LIVE AND LET DIE.

This is the film's thin protocol adapter. It implements the frozen
:class:`bond_api.protocol.MissionProvider` contract (brief / recon / plan /
execute / debrief) and binds the pure domain core — narcotics supply-graph
analytics and interdiction, voodoo-coded communiqué and drum-code deciphering,
market-flow economics, and Caribbean island ops planning — to the BOND-API
mission lifecycle.

The heavy lifting lives in the domain modules (:mod:`~.supply_graph`,
:mod:`~.coded_comms`, :mod:`~.island_ops`, :mod:`~.interdiction`,
:mod:`~.voodoo_drums`, :mod:`~.market_flow`); this module only orchestrates them
and packages results with provenance, so it stays thin and deterministic. The
pure core remains importable without ``bond_api``.

Discovery contract: a film package is a top-level module named by its slug
exposing ``MissionProvider`` at module top level (see ``bond_api.discovery``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from bond_api.protocol import (
    Asset,
    Constraint,
    Debrief,
    Finding,
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    Provenance,
    ReconReport,
    ReconRequest,
    Step,
)
from bond_api.registry import GadgetRegistry

from live_and_let_die.coded_comms import (
    KEYWORD,
    SAN_MONIQUE_PLAINTEXT,
    build_keyword_key,
    decipher,
    encipher,
)
from live_and_let_die.interdiction import interdict_san_monique
from live_and_let_die.island_ops import (
    ROUTE_GOAL,
    ROUTE_START,
    SAN_MONIQUE_TERRAIN,
    plan_san_monique_route,
)
from live_and_let_die.market_flow import EDGE_ECONOMICS, market_flow_report
from live_and_let_die.supply_graph import (
    SAN_MONIQUE_GRAPH,
    analyze_san_monique,
)
from live_and_let_die.voodoo_drums import DRUM_MESSAGE, drum_report

__all__ = [
    "CODENAME",
    "FILM",
    "GADGET_REGISTRY",
    "MISSION_SEED",
    "MissionProvider",
    "decipher_field_communique",
    "input_digest",
    "register_gadgets",
    "run_analysis",
]

#: Film identity and mission codename.
FILM = "live_and_let_die"
CODENAME = "SAN MONIQUE"

#: Deterministic mission seed (no random draws anywhere; seed is recorded for
#: provenance parity with the suite convention).
MISSION_SEED = 8

#: Canonical version string carried in every provenance record.
PACKAGE_VERSION = "0.1.0"


# ---------------------------------------------------------------------------
# Provenance fingerprint.
# ---------------------------------------------------------------------------
def _canonical_inputs() -> str:
    """A canonical, order-stable serialization of every analysis input."""
    supply = sorted(f"{e.source}->{e.target}:{e.weight}:{e.capacity}" for e in SAN_MONIQUE_GRAPH.edges())
    comms = f"{KEYWORD}|{SAN_MONIQUE_PLAINTEXT}"
    terrain = "|".join(SAN_MONIQUE_TERRAIN)
    ops = f"{ROUTE_START[0]},{ROUTE_START[1]}:{ROUTE_GOAL[0]},{ROUTE_GOAL[1]}"
    economics = sorted(f"{src}->{dst}:{m}:{d}" for (src, dst), (m, d) in EDGE_ECONOMICS.items())
    drums = DRUM_MESSAGE
    return "||".join([";".join(supply), comms, terrain, ops, ";".join(economics), drums])


def input_digest() -> str:
    """sha256 fingerprint of the canonical mission inputs (auditable outcome)."""
    return hashlib.sha256(_canonical_inputs().encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Domain orchestration.
# ---------------------------------------------------------------------------
def decipher_field_communique() -> dict[str, Any]:
    """Decipher the intercepted communiqué with the recovered voodoo keyword key."""
    key = build_keyword_key()
    ciphertext = encipher(SAN_MONIQUE_PLAINTEXT, key)
    return {
        "keyword": KEYWORD,
        "ciphertext": ciphertext,
        "plaintext": decipher(ciphertext, key),
        "deciphered": decipher(ciphertext, key) == SAN_MONIQUE_PLAINTEXT,
    }


def run_analysis() -> dict[str, Any]:
    """Run all three San Monique analyses and merge them into one report dict.

    Deterministic by construction: every sub-analysis is pure and the merged
    dict is built without any random or wall-clock dependence.
    """
    supply = analyze_san_monique()
    comms = decipher_field_communique()
    route = plan_san_monique_route()
    ops = {
        "start": ROUTE_START,
        "goal": ROUTE_GOAL,
        "route_cost": route.cost,
        "movement_cells": route.edge_count(),
        "crocodile_cells": route.crocodile_cells,
        "path": [list(cell) for cell in route.path],
    }
    return {
        "supply": supply,
        "comms": comms,
        "ops": ops,
        "interdiction": interdict_san_monique(budget=3),
        "drums": drum_report(),
        "market": market_flow_report(),
        "input_hash": input_digest(),
    }


# ---------------------------------------------------------------------------
# Gadget registration (BOND-API Layer 2 registry).
# ---------------------------------------------------------------------------
GADGET_REGISTRY = GadgetRegistry()


def register_gadgets(registry: GadgetRegistry | None = None) -> GadgetRegistry:
    """Register the film's analysers as named gadgets (idempotent by default)."""
    target = registry if registry is not None else GADGET_REGISTRY
    # Re-registration merges; lookup remains stable. Register alongside the
    # pure-domain callables so coordinators can invoke them directly.
    target.register(
        FILM,
        {
            "supply_graph_analyzer": analyze_san_monique,
            "communique_decipher": decipher_field_communique,
            "island_route_planner": plan_san_monique_route,
            "interdiction_planner": interdict_san_monique,
            "drum_traffic_reporter": drum_report,
            "market_flow_reporter": market_flow_report,
        },
    )
    return target


register_gadgets(GADGET_REGISTRY)


# ---------------------------------------------------------------------------
# The MissionProvider protocol implementation.
# ---------------------------------------------------------------------------
class MissionProvider:  # noqa: N801 — name fixed by the discovery contract
    """Deterministic SAN MONIQUE mission for the LIVE AND LET DIE film package."""

    film = FILM

    def brief(self) -> MissionBrief:
        """Declare the SAN MONIQUE mission: three analytic objectives."""
        return MissionBrief(
            film=self.film,
            codename=CODENAME,
            objectives=(
                "map the narcotics supply graph and identify the critical transit bottleneck",
                "decipher the voodoo-coded communiqué by symbol-substitution",
                "plan an infiltration route across crocodile terrain to the airfield",
            ),
            assets=(
                Asset(kind="dataset", name="san_monique_supply_graph", payload={"nodes": 7, "edges": 10}),
                Asset(kind="dataset", name="voodoo_communique", payload={"keyword": KEYWORD}),
                Asset(kind="dataset", name="san_monique_terrain", payload={"rows": len(SAN_MONIQUE_TERRAIN)}),
            ),
            constraints=(
                Constraint(kind="determinism", detail="no random draws, no wall-clock dependence in any artifact"),
                Constraint(kind="no-mocks", detail="real data and computation only"),
            ),
        )

    def recon(self, request: ReconRequest) -> ReconReport:
        """Survey the mission goal, the available assets, and the terrain."""
        supply_markets = [node.id for node in SAN_MONIQUE_GRAPH.nodes_of_kind("market")]
        return ReconReport(
            findings=(
                Finding(label="goal", detail=request.goal),
                Finding(label="markets", detail=", ".join(sorted(supply_markets))),
                Finding(label="supply_graph", detail="7 nodes / 10 legs production-to-market"),
                Finding(label="terrain", detail="crocodile channel walls off the airfield approach"),
                Finding(label="constraints", detail="deterministic, real-data-only execution"),
            )
        )

    def plan(self, brief: MissionBrief) -> MissionPlan:
        """Plan the four deterministic steps: three analyses plus a merged report."""
        objectives = brief.objectives
        return MissionPlan(
            steps=(
                Step(
                    name="supply",
                    action="analyze_supply_graph",
                    params={"objective": objectives[0], "source": "poppy_fields"},
                ),
                Step(
                    name="comms",
                    action="decipher_voodoo_communique",
                    params={"objective": objectives[1], "keyword": KEYWORD},
                ),
                Step(
                    name="ops",
                    action="plan_island_route",
                    params={
                        "objective": objectives[2],
                        "start": list(ROUTE_START),
                        "goal": list(ROUTE_GOAL),
                    },
                ),
                Step(name="combine", action="build_mission_report", params={}),
            )
        )

    def execute(self, plan: MissionPlan) -> MissionOutcome:
        """Run all three analyses and return a fully-provenanced outcome."""
        results = run_analysis()
        results["steps_completed"] = len(plan.steps)
        return MissionOutcome(
            success=True,
            results=results,
            provenance=Provenance(
                package_version=PACKAGE_VERSION,
                seed=MISSION_SEED,
                input_hash=input_digest(),
                wall_time_s=0.0,
            ),
        )

    def debrief(self, outcome: MissionOutcome) -> Debrief:
        """Distil actionable lessons from the executed outcome."""
        supply = outcome.results["supply"]
        ops = outcome.results["ops"]
        interdict = outcome.results["interdiction"]
        market = outcome.results["market"]
        return Debrief(
            outcome=outcome,
            lessons=(
                f"interdict the {supply['critical_transit_node']} — neutralizing it "
                f"stops {supply['disruption_units']:.0f} units of Miami throughput",
                f"a {interdict['budget']}-leg strike plan achieves an optimal "
                f"{interdict['exact']['reduction']:.0f}-unit reduction (greedy "
                f"{interdict['greedy']['reduction']:.0f}) — collapse the operation",
                f"the farm-gate producer keeps only {market['producer_share'] * 100:.1f}% "
                "of street value — the whole chain must be disrupted, not the field",
                f"any overland approach to the airfield wades at least {ops['crocodile_cells']} crocodile-water cells",
                "the communiqué deciphers under the voodoo keyword substitution",
            ),
        )
