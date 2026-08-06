"""Voodoo drum-code signaling (San Monique coded comms).

Across the Caribbean, voodoo drums carry messages too fast for speech — a real
phenomenon the film leans on (the cult's drums telegraph Kananga's movements).
This module implements a deterministic drum-rhythm codec and its traffic
analysis:

* :func:`signal_for_text` — encode a message onto a per-beat ``0/1`` grid using
  standard Morse timing on a drum (dot = 1 sounding beat, dash = 3; intra-letter
  gap 1, inter-letter gap 3, inter-word gap 7).
* :func:`decode_signal` — recover the plaintext from a drum-beat signal, with
  strict validation of symbol/gap run lengths.
* :func:`rhythm_signature` / :func:`signature_distance` — quantitative traffic
  signature (density, longest run) so two intercepted signals can be compared.

Pure, deterministic, stdlib-only; no ``infrastructure.*`` and no ``bond_api``.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "DRUM_MESSAGE",
    "MORSE",
    "REVERSE_MORSE",
    "decode_signal",
    "drum_report",
    "encode_morse",
    "rhythm_signature",
    "signal_for_text",
    "signature_distance",
]

#: Standard International Morse code (ITU) table — letters only.
MORSE: dict[str, str] = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
}

#: Inverted table: morse symbol string -> letter.
REVERSE_MORSE: dict[str, str] = {symbol: letter for letter, symbol in MORSE.items()}

#: Timing, in beats. Sound runs are 1 (dot) or 3 (dash); silence gaps are
#: 1 (within a letter), 3 (between letters), or 7 (between words).
DOT = 1
DASH = 3
GAP_INTRA = 1
GAP_LETTER = 3
GAP_WORD = 7

#: Canonical plaintext tapped on the drums (deterministic).
DRUM_MESSAGE = "KANANGA LETS THE SNAKE BITE"


def encode_morse(text: str) -> list[list[str]]:
    """Map a message to a nested morse structure: words -> letters -> symbols."""
    words: list[list[str]] = []
    for word in text.split():
        letters: list[str] = []
        for ch in word.upper():
            if ch not in MORSE:
                raise ValueError(f"cannot drum-encode character {ch!r}")
            letters.append(MORSE[ch])
        words.append(letters)
    return words


def signal_for_text(text: str) -> tuple[int, ...]:
    """Encode ``text`` onto a per-beat ``0/1`` drum grid (see module docs).

    Returns a tuple where ``1`` = drum sounding, ``0`` = silence, one entry per
    beat. Round-trips exactly through :func:`decode_signal`.
    """
    words = encode_morse(text)
    beats: list[int] = []
    for wi, word in enumerate(words):
        for li, letter in enumerate(word):
            code = letter
            for ei, element in enumerate(code):
                duration = DOT if element == "." else DASH
                beats.extend([1] * duration)
                if ei < len(code) - 1:
                    beats.extend([0] * GAP_INTRA)
            if li < len(word) - 1:
                beats.extend([0] * GAP_LETTER)
        if wi < len(words) - 1:
            beats.extend([0] * GAP_WORD)
    return tuple(beats)


def _run_lengths(signal: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    """Compact a signal into ``(bit, run_length)`` segments (deterministic)."""
    runs: list[tuple[int, int]] = []
    i = 0
    n = len(signal)
    while i < n:
        bit = signal[i]
        start = i
        while i < n and signal[i] == bit:
            i += 1
        runs.append((bit, i - start))
    return tuple(runs)


def _morse_to_char(symbols: str) -> str:
    try:
        return REVERSE_MORSE[symbols]
    except KeyError:
        raise ValueError(f"unknown morse symbol sequence {symbols!r}") from None


def decode_signal(signal: tuple[int, ...]) -> str:
    """Decode a drum-beat signal back to plaintext (strict run validation).

    Raises ``ValueError`` on malformed symbol (`run` not 1 or 3) or gap
    (``run`` not 1, 3, or 7) lengths.
    """
    if not signal:
        return ""
    # Trim leading/trailing silence (drummers start and stop on a beat).
    start = 0
    end = len(signal)
    while start < end and signal[start] == 0:
        start += 1
    while end > start and signal[end - 1] == 0:
        end -= 1
    if start >= end:
        return ""

    runs = _run_lengths(tuple(signal[start:end]))
    words: list[str] = []
    word: list[str] = []
    letter: list[str] = []
    for bit, length in runs:
        if bit == 1:
            if length == DOT:
                letter.append(".")
            elif length == DASH:
                letter.append("-")
            else:
                raise ValueError(f"invalid drum symbol run length {length}")
        else:
            if length == GAP_INTRA:
                pass  # within a letter
            elif length == GAP_LETTER:
                word.append(_morse_to_char("".join(letter)))
                letter = []
            elif length == GAP_WORD:
                word.append(_morse_to_char("".join(letter)))
                words.append("".join(word))
                word = []
                letter = []
            else:
                raise ValueError(f"invalid drum gap run length {length}")
    # Flush any trailing letter/word.
    if letter:
        word.append(_morse_to_char("".join(letter)))
    if word:
        words.append("".join(word))
    return " ".join(words)


def rhythm_signature(signal: tuple[int, ...]) -> dict[str, float]:
    """A deterministic numeric signature of a drum signal.

    Returns beat count, sounding density (fraction of beats struck), and the
    longest continuous drum run (a rhythmic "emphasis" marker).
    """
    if not signal:
        return {"beats": 0.0, "density": 0.0, "longest_run": 0.0}
    beats = len(signal)
    struck = sum(signal)
    density = float(struck / beats)
    longest = 0
    current = 0
    for bit in signal:
        if bit == 1:
            current += 1
            if current > longest:
                longest = current
        else:
            current = 0
    return {"beats": float(beats), "density": density, "longest_run": float(longest)}


def signature_distance(first: tuple[int, ...], second: tuple[int, ...]) -> float:
    """Euclidean distance between two signals' rhythm signatures.

    Correlated messages (same words) land closer than unrelated messages.
    """
    a = rhythm_signature(first)
    b = rhythm_signature(second)
    return float(
        (
            (a["beats"] - b["beats"]) ** 2
            + (a["density"] - b["density"]) ** 2
            + (a["longest_run"] - b["longest_run"]) ** 2
        )
        ** 0.5
    )


def drum_report() -> dict[str, Any]:
    """Run the canonical San Monique drum-traffic analysis (deterministic)."""
    signal = signal_for_text(DRUM_MESSAGE)
    decoded = decode_signal(signal)
    return {
        "plaintext": DRUM_MESSAGE,
        "decoded": decoded,
        "roundtrip_exact": decoded == DRUM_MESSAGE,
        "beats": len(signal),
        "density": rhythm_signature(signal)["density"],
        "longest_run": int(rhythm_signature(signal)["longest_run"]),
        "signature": rhythm_signature(signal),
    }
