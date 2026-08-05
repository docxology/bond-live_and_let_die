"""Real-data tests for the voodoo drum-code signaling module."""

from __future__ import annotations

import pytest
from live_and_let_die.voodoo_drums import (
    DRUM_MESSAGE,
    MORSE,
    REVERSE_MORSE,
    decode_signal,
    drum_report,
    encode_morse,
    rhythm_signature,
    signal_for_text,
    signature_distance,
)


def test_morse_tables_are_consistent_and_bijective() -> None:
    assert len(MORSE) == 26
    assert set(MORSE.values()) == set(REVERSE_MORSE)
    assert REVERSE_MORSE["..."] == "S"


def test_encode_morse_structure() -> None:
    words = encode_morse("SOS")
    assert words == [["...", "---", "..."]]  # single word, three letters


def test_encode_morse_unknown_char() -> None:
    with pytest.raises(ValueError):
        encode_morse("SOS 1")  # digit cannot be drum-encoded


def test_signal_roundtrip() -> None:
    for text in (DRUM_MESSAGE, "SOS", "A B C", "MAMBO"):  # single-letter words
        signal = signal_for_text(text)
        assert decode_signal(signal) == text


def test_signal_for_text_all_upper() -> None:
    assert DRUM_MESSAGE == DRUM_MESSAGE.upper()
    assert signal_for_text(DRUM_MESSAGE.lower()) == signal_for_text(DRUM_MESSAGE)


def test_drum_report() -> None:
    report = drum_report()
    assert report["roundtrip_exact"] is True
    assert report["plaintext"] == DRUM_MESSAGE
    assert report["decoded"] == DRUM_MESSAGE
    assert report["beats"] == 195
    assert report["longest_run"] == 3
    assert 0.0 < report["density"] < 1.0


def test_rhythm_signature_empty() -> None:
    assert rhythm_signature(()) == {"beats": 0.0, "density": 0.0, "longest_run": 0.0}


def test_rhythm_signature_longest_run() -> None:
    sig = rhythm_signature((1, 1, 1, 0, 1, 0, 0))
    assert sig["longest_run"] == 3.0
    assert sig["beats"] == 7.0


def test_signature_distance_self_zero_and_tolerance() -> None:
    sig = signal_for_text(DRUM_MESSAGE)
    assert signature_distance(sig, sig) == pytest.approx(0.0)
    other = signal_for_text("THE AIRFIELD IS AWAKE")
    # A genuinely different message is measurably farther than an identical one.
    assert signature_distance(sig, other) > 0.0


def test_decode_invalid_symbol_run() -> None:
    # A 2-beat sound run is neither a dot (1) nor a dash (3).
    with pytest.raises(ValueError):
        decode_signal((1, 1))


def test_decode_invalid_gap_run() -> None:
    # A 4-beat silence in the middle of a signal is not a valid gap (1/3/7).
    with pytest.raises(ValueError):
        decode_signal((1, 0, 0, 0, 0, 1))


def test_decode_unknown_morse_letter() -> None:
    # Five dashes ("-----") is not a letter in the ITU table.
    dash = (1, 1, 1)
    signal = tuple(bit for _ in range(4) for bit in dash + (0,)) + dash
    with pytest.raises(ValueError):
        decode_signal(signal)


def test_decode_empty_and_blank_signals() -> None:
    assert decode_signal(()) == ""
    assert decode_signal((0, 0, 0)) == ""


def test_decode_trims_leading_trailing_silence() -> None:
    # Leading and trailing silence must be ignored.
    sig = signal_for_text(DRUM_MESSAGE)
    padded = (0, 0) + sig + (0, 0)
    assert decode_signal(padded) == DRUM_MESSAGE
