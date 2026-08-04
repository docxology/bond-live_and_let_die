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


def test_recon_shape() -> None:
    report = MissionProvider().recon(ReconRequest("survey the island"))
    assert isinstance(report, ReconReport)
    assert len(report.findings) == 5


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
    assert len(debrief.lessons) == 3


def test_debrief_lessons() -> None:
    provider = MissionProvider()
    outcome = provider.execute(provider.plan(provider.brief()))
    debrief = provider.debrief(outcome)
    assert "airfield" in debrief.lessons[0]
    assert any("crocodile" in lesson for lesson in debrief.lessons)


def test_run_analysis_deterministic_and_rich() -> None:
    first = run_analysis()
    second = run_analysis()
    assert first == second
    assert set(first) >= {"supply", "comms", "ops", "input_hash"}
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
