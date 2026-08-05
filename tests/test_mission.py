"""End-to-end tests for the SAN MONIQUE MissionProvider (BOND-API protocol)."""

from __future__ import annotations

from bond_api.protocol import (
    MissionBrief,
    MissionOutcome,
    MissionProvider as ProviderProtocol,
    MissionPlan,
    ReconReport,
    ReconRequest,
    run_mission,
)
from bond_api.registry import GadgetRegistry
from bond_api.serialization import from_json, to_json

from live_and_let_die.island_ops import min_san_monique_crocodile_exposure
from live_and_let_die.supply_graph import SAN_MONIQUE_GRAPH, Edge, Node, SupplyGraph
from live_and_let_die.mission import (
    CODENAME,
    FILM,
    GADGET_REGISTRY,
    MISSION_SEED,
    MissionProvider,
    decipher_field_communique,
    input_digest,
    register_gadgets,
    run_analysis,
)


def test_film_identity() -> None:
    assert FILM == "live_and_let_die"
    assert CODENAME == "SAN MONIQUE"
    provider = MissionProvider()
    assert provider.film == "live_and_let_die"


def test_provider_satisfies_protocol() -> None:
    assert isinstance(MissionProvider(), ProviderProtocol)


def test_brief_shape() -> None:
    brief = MissionProvider().brief()
    assert isinstance(brief, MissionBrief)
    assert len(brief.objectives) == 3
    assert len(brief.assets) == 3
    assert len(brief.constraints) == 2
    assert brief.codename == CODENAME


def test_brief_graph_asset_is_derived_not_literal() -> None:
    """The supply-graph asset payload must be read off the live graph.

    Binding test for a real defect: the payload used to be the literals
    ``{"nodes": 7, "edges": 10}``, which would have kept reporting 7/10 after any
    dataset change. Comparing against a freshly-measured graph — not against 7
    and 10 — is what makes this test able to fail.
    """
    brief = MissionProvider().brief()
    payload = next(a.payload for a in brief.assets if a.name == "san_monique_supply_graph")
    assert payload["nodes"] == len(SAN_MONIQUE_GRAPH.node_ids())
    assert payload["edges"] == len(SAN_MONIQUE_GRAPH.edges())
    # A literal would not track a differently-sized graph; prove the measurement
    # itself discriminates by checking it against an independently built graph.
    other = SupplyGraph(
        [Node("a", "production", "A", capacity=1.0), Node("b", "market", "B")],
        [Edge("a", "b", 1.0, 1.0)],
    )
    assert (len(other.node_ids()), len(other.edges())) != (payload["nodes"], payload["edges"])


def test_recon_shape() -> None:
    report = MissionProvider().recon(ReconRequest("survey the island"))
    assert isinstance(report, ReconReport)
    assert len(report.findings) == 5


def test_recon_supply_graph_finding_is_derived() -> None:
    """The recon graph-size finding interpolates the live graph, never literals."""
    report = MissionProvider().recon(ReconRequest("survey the island"))
    detail = next(f.detail for f in report.findings if f.label == "supply_graph")
    expected = f"{len(SAN_MONIQUE_GRAPH.node_ids())} nodes / {len(SAN_MONIQUE_GRAPH.edges())} legs production-to-market"
    assert detail == expected


def test_plan_shape() -> None:
    provider = MissionProvider()
    plan = provider.plan(provider.brief())
    assert isinstance(plan, MissionPlan)
    assert [s.name for s in plan.steps] == ["supply", "comms", "ops", "combine"]


def test_execute_outcome_and_provenance() -> None:
    provider = MissionProvider()
    outcome = provider.execute(provider.plan(provider.brief()))
    assert isinstance(outcome, MissionOutcome)
    assert outcome.success
    assert outcome.provenance.seed == MISSION_SEED
    assert outcome.results["steps_completed"] == 4
    assert outcome.results["supply"]["critical_transit_node"] == "airfield"


def test_run_mission_flow_order() -> None:
    provider = MissionProvider()
    debrief = run_mission(provider, ReconRequest("full flow"))
    assert debrief.outcome.success
    assert len(debrief.lessons) == 5


def test_debrief_lessons() -> None:
    provider = MissionProvider()
    outcome = provider.execute(provider.plan(provider.brief()))
    debrief = provider.debrief(outcome)
    assert "airfield" in debrief.lessons[0]
    assert any("crocodile" in lesson for lesson in debrief.lessons)


def test_debrief_disruption_lesson_is_bounded_by_the_reported_throughput() -> None:
    """The headline lesson must be sayable in the model that produced it.

    It previously read "stops 150 units of Miami throughput" while the operative
    model caps Miami at a demand ceiling of 120 — a number the model could not
    support. The lesson now quotes the demand-capped disruption against the
    demand-capped total, and both are asserted from the outcome payload.
    """
    provider = MissionProvider()
    outcome = provider.execute(provider.plan(provider.brief()))
    supply = outcome.results["supply"]
    lesson = provider.debrief(outcome).lessons[0]

    assert supply["disruption_units"] <= supply["max_flow_total"]
    assert f"{supply['disruption_units']:.0f}" in lesson
    assert f"{supply['max_flow_total']:.0f}" in lesson
    assert "Miami throughput" not in lesson


def test_debrief_universal_crocodile_claim_uses_the_all_routes_minimum() -> None:
    """ "At least N" must quote the route-space floor, not one route's exposure."""
    provider = MissionProvider()
    outcome = provider.execute(provider.plan(provider.brief()))
    ops = outcome.results["ops"]
    lesson = next(lesson for lesson in provider.debrief(outcome).lessons if "crocodile" in lesson)

    assert ops["min_crocodile_cells"] == min_san_monique_crocodile_exposure()
    assert ops["min_crocodile_cells"] <= ops["crocodile_cells"]
    assert f"at least {ops['min_crocodile_cells']}" in lesson


def test_run_analysis_deterministic_and_rich() -> None:
    first = run_analysis()
    second = run_analysis()
    assert first == second
    assert set(first) >= {"supply", "comms", "ops", "interdiction", "drums", "market", "input_hash"}
    assert first["comms"]["plaintext"] == "KANANGA LETS THE SNAKE BITE"
    assert first["ops"]["crocodile_cells"] == 4
    assert first["ops"]["route_cost"] == 41.0


def test_decipher_field_communique() -> None:
    report = decipher_field_communique()
    assert report["deciphered"] is True
    assert report["keyword"] == "BARON"


def test_input_digest_stable() -> None:
    assert input_digest() == input_digest()
    assert len(input_digest()) == 64


def test_gadget_registry_default() -> None:
    assert FILM in GADGET_REGISTRY
    names = GADGET_REGISTRY.gadgets_for(FILM)
    assert "supply_graph_analyzer" in names
    assert "island_route_planner" in names
    gadget = GADGET_REGISTRY.lookup(FILM, "supply_graph_analyzer")
    assert callable(gadget)


def test_register_gadgets_custom_registry() -> None:
    registry = GadgetRegistry()
    register_gadgets(registry)
    assert registry.lookup(FILM, "communique_decipher") is not None
    assert len(registry.films()) == 1
    assert registry.contains(FILM, "island_route_planner")


def test_outcome_json_round_trip() -> None:
    provider = MissionProvider()
    outcome = provider.execute(provider.plan(provider.brief()))
    text = to_json(outcome)
    decoded = from_json(text, expected=MissionOutcome)
    assert decoded == outcome
    assert decoded.provenance.input_hash == outcome.provenance.input_hash
