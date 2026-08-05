"""Tests for manuscript variable hydration and the live cross-reference gate."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

from live_and_let_die.manuscript_variables import (
    DEFAULT_CONFIG_PATH,
    _TOKEN_RE,
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
