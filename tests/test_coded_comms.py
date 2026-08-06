"""Real-data tests for the voodoo-coded communiqué deciphering module."""

from __future__ import annotations

import pytest

from live_and_let_die.coded_comms import (
    ALPHABET,
    ENGLISH_FREQUENCIES,
    KEYWORD,
    san_monique_message,
    SAN_MONIQUE_PLAINTEXT,
    build_keyword_key,
    decipher,
    encipher,
    frequency_table,
    invert_key,
    score_plaintext,
    solve_substitution,
    symbol_roster,
)


def test_keyword_key_is_bijective_over_alphabet() -> None:
    key = build_keyword_key()
    assert len(key) == 26
    assert set(key) == set(ALPHABET)
    assert set(key.values()) == set(ALPHABET)
    assert len(set(key.values())) == 26


def test_keyword_key_known_prefix() -> None:
    key = build_keyword_key()
    assert key["A"] == "B"
    assert key["B"] == "A"
    assert key["C"] == "R"
    assert key["D"] == "O"
    assert key["E"] == "N"


def test_keyword_guardrails() -> None:
    with pytest.raises(ValueError):
        build_keyword_key(alphabet="")
    with pytest.raises(ValueError):
        build_keyword_key(keyword="")
    with pytest.raises(ValueError):
        build_keyword_key(alphabet="AAAA")  # incomplete cipher alphabet


def test_invert_key_and_non_bijective() -> None:
    key = build_keyword_key()
    inverse = invert_key(key)
    for plain, cipher in key.items():
        assert inverse[cipher] == plain
    with pytest.raises(ValueError):
        invert_key({"A": "X", "B": "X"})


def test_encipher_decipher_roundtrip() -> None:
    key = build_keyword_key()
    ct = encipher(SAN_MONIQUE_PLAINTEXT, key)
    assert ct == "HBKBKDB INTS TEN SKBHN AFTN"
    assert decipher(ct, key) == SAN_MONIQUE_PLAINTEXT


def test_encipher_passes_non_letters() -> None:
    key = build_keyword_key()
    assert encipher("A-B C!", key) == f"{key['A']}-{key['B']} {key['C']}!"
    assert encipher("abc", key) == encipher("ABC", key)


def test_decipher_roundtrip_arbitrary() -> None:
    key = build_keyword_key()
    message = "THE SNAKE BITE"
    assert decipher(encipher(message, key), key) == message


def test_frequency_table() -> None:
    counts = frequency_table("AABbC c")
    assert counts["A"] == 2
    assert counts["B"] == 2
    assert counts["C"] == 2
    assert set(counts) <= set(ALPHABET)


def test_score_plaintext_reference() -> None:
    # English-shaped text scores higher against the English reference than a
    # uniform-frequency string.
    english = score_plaintext("THE SNAKE BITES BOTH THE HANGMAN AND THE BOY")
    uniform = score_plaintext("QZJX QZJX QZJX QZJX QZJX QZJX")
    assert english > uniform
    assert score_plaintext("") == 0.0
    assert score_plaintext("!!!") == 0.0
    assert score_plaintext("ABC", {}) == 0.0  # empty reference


def test_solve_substitution_output_is_pinned_exactly() -> None:
    """``solve_substitution`` is pure and deterministic — pin what it returns.

    The previous assertions were ``isinstance(guess, str) and guess`` plus
    ``score > 0.0``, which the function satisfies for literally any non-empty
    ciphertext. They could not distinguish a working frequency attack from a
    broken one. These pin the exact string and score.
    """
    key = build_keyword_key()
    ct = encipher(SAN_MONIQUE_PLAINTEXT, key)
    guess, score = solve_substitution(ct)
    assert guess == "IEAEAHE LTON ORT NAEIT SDOT"
    assert score == pytest.approx(0.926339967518, abs=1e-9)
    assert len(guess) == len(ct)

    empty_guess, empty_score = solve_substitution("")
    assert empty_guess == "" and empty_score == 0.0


def test_frequency_attack_does_not_recover_a_short_intercept() -> None:
    """State the limitation as a test, not as a hope.

    On a 27-character intercept the attack recovers nothing — and still scores
    0.93 against the English reference. The score is a ranking heuristic, not
    evidence of recovery, and this test fails loudly if anyone starts treating
    it as the latter.
    """
    key = build_keyword_key()
    ct = encipher(SAN_MONIQUE_PLAINTEXT, key)
    guess, score = solve_substitution(ct)
    assert guess != SAN_MONIQUE_PLAINTEXT
    assert score > 0.9, "a high score coexists with a failed recovery — that is the point"
    # Recovery *is* possible with the key; the attack is the weaker instrument.
    assert decipher(ct, key) == SAN_MONIQUE_PLAINTEXT


def test_symbol_roster_bijective() -> None:
    roster = symbol_roster()
    assert len(roster) == 26
    assert len(set(roster.values())) == 26


def test_san_monique_message_is_a_named_function() -> None:
    plaintext, ciphertext = san_monique_message()
    assert plaintext == SAN_MONIQUE_PLAINTEXT
    assert ciphertext == "HBKBKDB INTS TEN SKBHN AFTN"
    assert KEYWORD == "BARON"
    assert ENGLISH_FREQUENCIES["E"] == pytest.approx(12.702)


def test_symbol_roster_rejects_non_bijective_alphabet() -> None:
    """Two alphabet positions mapped to one glyph must fail loudly.

    Without the bijectivity guard a lossy glyph roster would silently make
    decoding ambiguous. ``AA`` maps both A's positions to the same glyph, so the
    guard must fire rather than return a lossy mapping.
    """
    with pytest.raises(ValueError, match="not bijective"):
        symbol_roster("AA")


def test_normalized_frequencies_of_empty_counts_is_empty() -> None:
    """Zero denominator must not produce a NaN/inf frequency vector."""
    from live_and_let_die.coded_comms import _normalized_frequencies

    assert _normalized_frequencies({}) == {}
