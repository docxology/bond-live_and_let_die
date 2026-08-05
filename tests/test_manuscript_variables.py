"""Tests for manuscript variable hydration and the live cross-reference gate."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

from live_and_let_die.coded_comms import ALPHABET
from live_and_let_die.island_ops import SAN_MONIQUE_TERRAIN
from live_and_let_die.mission import FILM, GADGET_REGISTRY, MISSION_SEED
from live_and_let_die.manuscript_variables import (
    DEFAULT_CONFIG_PATH,
    _TOKEN_RE,
    domain_modules,
    generate_variables,
    load_manuscript_config,
    resolve_manuscript_tree,
)

PACKAGE_ROOT = Path(__file__).resolve().parent.parent


def test_load_existing_config() -> None:
    config = load_manuscript_config()
    assert config["paper"]["codename"] == "SAN MONIQUE"
    assert config["paper"]["year"] == 1973


def test_load_config_missing_and_malformed(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_manuscript_config(tmp_path / "nope.yaml")
    bad = tmp_path / "bad.yaml"
    bad.write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_manuscript_config(bad)


def test_generate_variables_hydrates_metrics() -> None:
    variables = generate_variables()
    assert variables["LALD_IDENTITY"] == "LIVE AND LET DIE"
    assert variables["LALD_CODENAME"] == "SAN MONIQUE"
    assert variables["LALD_BOTTLENECK"] == "airfield"
    assert variables["LALD_MAX_FLOW"] == "220"
    assert variables["LALD_CROCODILE_CELLS"] == "4"
    assert variables["LALD_ROUTE_COST"] == "41"
    assert variables["LALD_PLAINTEXT"] == "KANANGA LETS THE SNAKE BITE"
    assert variables["LALD_KEYWORD"] == "BARON"
    assert variables["LALD_SUPPLY_NODES"] == "7"
    # Deepened Phase-4 metrics.
    assert variables["LALD_BUDGET"] == "3"
    assert variables["LALD_GREEDY_REDUCTION"] == "220"
    assert variables["LALD_EXACT_REDUCTION"] == "220"
    assert variables["LALD_DRUM_BEATS"] == "195"
    assert variables["LALD_DRUM_ROUNDTRIP"] == "exact"
    assert variables["LALD_PRODUCER_SHARE"] == "1.7%"
    assert variables["LALD_SPREAD_RATIO"] == "59"


def test_domain_modules_are_discovered_from_the_package() -> None:
    """The pure-core module list is read off disk, not typed into a constant."""
    modules = domain_modules()
    assert modules == (
        "coded_comms",
        "interdiction",
        "island_ops",
        "market_flow",
        "supply_graph",
        "voodoo_drums",
    )
    # The adapter, the hydrator and the package marker are never domain modules.
    for excluded in ("mission", "manuscript_variables", "__init__"):
        assert excluded not in modules


def test_constant_tokens_track_their_source_of_truth() -> None:
    """Constants quoted in prose are derived from code, not written twice.

    Each assertion compares the token against the live definition rather than
    against a literal, so changing the code and forgetting the manuscript is a
    test failure rather than silent drift.
    """
    variables = generate_variables()
    assert variables["LALD_SEED"] == str(MISSION_SEED)
    assert variables["LALD_ALPHABET_SIZE"] == str(len(ALPHABET))
    assert variables["LALD_MODULE_COUNT"] == str(len(domain_modules()))
    assert variables["LALD_GADGET_COUNT"] == str(len(GADGET_REGISTRY.gadgets_for(FILM)))
    assert variables["LALD_TERRAIN_ROWS"] == str(len(SAN_MONIQUE_TERRAIN))
    assert variables["LALD_TERRAIN_COLS"] == str(len(SAN_MONIQUE_TERRAIN[0]))
    assert variables["LALD_TERRAIN_SHAPE"] == f"{len(SAN_MONIQUE_TERRAIN)}x{len(SAN_MONIQUE_TERRAIN[0])}"


def test_terrain_cost_table_names_every_terrain() -> None:
    """The rendered cost legend covers all terrains and states each real cost."""
    table = generate_variables()["LALD_TERRAIN_COSTS"]
    for name in ("road", "open ground", "beach", "mangrove", "swamp", "open water", "crocodile water"):
        assert name in table, f"terrain {name!r} missing from the rendered cost table"
    assert "crocodile water cost 7" in table
    assert "infinite" in table


def test_drum_timing_token_states_the_morse_ratios() -> None:
    timing = generate_variables()["LALD_DRUM_TIMING"]
    assert "dot = 1" in timing
    assert "dash = 3" in timing
    assert "inter-word gap 7" in timing


def test_num_objectives_reads_the_config_not_a_literal(tmp_path: Path) -> None:
    """LALD_NUM_OBJECTIVES counts the configured objectives, whatever they are."""
    live = generate_variables()
    config = load_manuscript_config()
    assert live["LALD_NUM_OBJECTIVES"] == str(len(config["mission"]["objectives"]))

    # A config declaring a different number must move the token — a hardcoded
    # "3" would survive this and is exactly what this test rejects.
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        "paper:\n  identity: X\nmission:\n  objectives:\n    - one\n    - two\n",
        encoding="utf-8",
    )
    assert generate_variables(config_path=cfg)["LALD_NUM_OBJECTIVES"] == "2"


def test_malformed_mission_section_is_rejected(tmp_path: Path) -> None:
    bad_mission = tmp_path / "bad_mission.yaml"
    bad_mission.write_text("paper: {}\nmission: not-a-mapping\n", encoding="utf-8")
    with pytest.raises(ValueError):
        generate_variables(config_path=bad_mission)

    bad_objectives = tmp_path / "bad_objectives.yaml"
    bad_objectives.write_text("paper: {}\nmission:\n  objectives: nope\n", encoding="utf-8")
    with pytest.raises(ValueError):
        generate_variables(config_path=bad_objectives)


def test_generate_variables_requires_paper_section(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text("mission: {}\n", encoding="utf-8")
    # Missing paper defaults to {}; a non-dict paper, however, must fail.
    bad = tmp_path / "bad_paper.yaml"
    bad.write_text("paper: not-a-mapping\n", encoding="utf-8")
    with pytest.raises(ValueError):
        generate_variables(config_path=bad)


def test_generate_variables_deterministic_with_now(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    # Minimal valid config (only the paper tokens we consult).
    cfg.write_text(
        "paper:\n  identity: X\n  codename: Y\n  year: 1973\n  version: v\n  title: T\n  subtitle: S\n",
        encoding="utf-8",
    )
    stamp = datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone.utc)
    v1 = generate_variables(config_path=cfg, now=stamp)
    v2 = generate_variables(config_path=cfg, now=stamp)
    assert v1 == v2
    assert v1["GENERATION_TIMESTAMP"] == "2026-08-04T12:00:00+00:00"


def test_all_prose_tokens_resolve() -> None:
    """Live cross-reference gate: every {{TOKEN}} in a numbered section resolves."""
    variables = generate_variables()
    for section in sorted(PACKAGE_ROOT.glob("manuscript/[0-9]*.md")):
        text = section.read_text(encoding="utf-8")
        tokens = set(_TOKEN_RE.findall(text))
        for token in tokens:
            name = token[2:-2]
            assert name in variables, f"unresolved token {token} in {section.name}: add it to generate_variables()"


def test_resolve_manuscript_tree_writes_sections(tmp_path: Path) -> None:
    variables = generate_variables()
    out_dir, files = resolve_manuscript_tree(variables, manuscript_dir=PACKAGE_ROOT / "manuscript", output_dir=tmp_path)
    assert files
    for name in files:
        rendered = (out_dir / name).read_text(encoding="utf-8")
        assert "{{" not in rendered
    assert DEFAULT_CONFIG_PATH.parent.name == "manuscript"


def test_resolve_strict_raises_on_unknown_token(tmp_path: Path) -> None:
    mdir = tmp_path / "m"
    mdir.mkdir()
    (mdir / "00_x.md").write_text("token {{LALD_UNKNOWN}} here\n", encoding="utf-8")
    variables = generate_variables()
    with pytest.raises(ValueError):
        resolve_manuscript_tree(variables, manuscript_dir=mdir, output_dir=tmp_path / "o", strict=True)


def test_resolve_non_strict_allows_unknown_token(tmp_path: Path) -> None:
    mdir = tmp_path / "m2"
    mdir.mkdir()
    (mdir / "00_y.md").write_text("token {{LALD_UNKNOWN}} here\n", encoding="utf-8")
    variables = generate_variables()
    _, files = resolve_manuscript_tree(variables, manuscript_dir=mdir, output_dir=tmp_path / "o2", strict=False)
    assert files == ["00_y.md"]


def test_regex_matches_expected_token() -> None:
    assert re.fullmatch(r"\{\{LALD_[A-Z0-9_]+\}\}", "{{LALD_BOTTLENECK}}")
