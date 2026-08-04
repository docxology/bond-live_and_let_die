"""Real-data tests for the voodoo-coded communiqué deciphering module."""

from __future__ import annotations

import pytest

from live_and_let_die.coded_comms import (
    ALPHABET,
    ENGLISH_FREQUENCIES,
    KEYWORD,
    SAN_MONIQUE_MESSAGE,
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


def test_solve_substitution_returns_guess_and_score() -> None:
    key = build_keyword_key()
    ct = encipher(SAN_MONIQUE_PLAINTEXT, key)
    guess, score = solve_substitution(ct)
    assert isinstance(guess, str) and guess
    assert score > 0.0
    empty_guess, empty_score = solve_substitution("")
    assert empty_guess == "" and empty_score == 0.0


def test_symbol_roster_bijective() -> None:
    roster = symbol_roster()
    assert len(roster) == 26
    assert len(set(roster.values())) == 26


def test_san_monique_message_constant() -> None:
    plaintext, ciphertext = SAN_MONIQUE_MESSAGE()
    assert plaintext == SAN_MONIQUE_PLAINTEXT
    assert ciphertext == "HBKBKDB INTS TEN SKBHN AFTN"
    assert KEYWORD == "BARON"
    assert ENGLISH_FREQUENCIES["E"] == pytest.approx(12.702)
