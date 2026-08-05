"""Voodoo-coded message deciphering (symbol-substitution ciphers).

Kananga's operators hide their radio chatter behind a monoalphabetic symbol
substitution: a *keyword* builds a reshuffled cipher alphabet (the classic
keyword cipher), and messages encipher letter-by-letter as if each plaintext
letter were "spoken" as a voodoo symbol.

This module implements the real machinery — key construction, encipher /
decipher, letter-frequency tables, and a frequency-attack solver that guesses
an unknown substitution by matching ciphertext symbol frequencies against a
reference English distribution.

Pure, deterministic, stdlib-only; no ``infrastructure.*`` and no ``bond_api``.
"""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "ALPHABET",
    "ENGLISH_FREQUENCIES",
    "KEYWORD",
    "ROSTER_SYMBOLS",
    "SAN_MONIQUE_MESSAGE",
    "build_keyword_key",
    "decipher",
    "encipher",
    "frequency_table",
    "invert_key",
    "score_plaintext",
    "solve_substitution",
    "symbol_roster",
]

#: The cipher alphabet — 26 letters. Non-letter characters (spaces, punctuation)
#: pass through substitution untouched.
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

#: Voodoo loa whose name seeds the substitution key (Baron Samedi, guardian of
#: the crossroads and the dead — the film's voodoo motif).
KEYWORD = "BARON"

#: Canonical plaintext hidden in the intercepted communiqué (deterministic).
SAN_MONIQUE_PLAINTEXT = "KANANGA LETS THE SNAKE BITE"

#: Standard English letter frequencies (percent of running text), used as the
#: reference distribution for the frequency-attack solver.
ENGLISH_FREQUENCIES: dict[str, float] = {
    "E": 12.702,
    "T": 9.056,
    "A": 8.167,
    "O": 7.507,
    "I": 6.966,
    "N": 6.749,
    "S": 6.327,
    "H": 6.094,
    "R": 5.987,
    "D": 4.253,
    "L": 4.025,
    "C": 2.782,
    "U": 2.758,
    "M": 2.406,
    "W": 2.360,
    "F": 2.228,
    "G": 2.015,
    "Y": 1.974,
    "P": 1.929,
    "B": 1.492,
    "V": 0.978,
    "K": 0.772,
    "J": 0.153,
    "X": 0.150,
    "Q": 0.095,
    "Z": 0.074,
}

#: A deterministic voodoo *glyph* per letter, for flavor and the ciphertext
#: rendering. Letters A-Z map one-to-one onto a canonical roster of symbols.
ROSTER_SYMBOLS: dict[str, str] = {
    "A": "☉",
    "B": "△",
    "C": "☿",
    "D": "†",
    "E": "※",
    "F": "♆",
    "G": "ባ",
    "H": "ᚠ",
    "I": "☽",
    "J": "◬",
    "K": "ᛗ",
    "L": "🜂",
    "M": "◉",
    "N": "♃",
    "O": "◔",
    "P": "ᚱ",
    "Q": "✠",
    "R": "⊙",
    "S": "☯",
    "T": "ᛟ",
    "U": "☍",
    "V": "▲",
    "W": "☩",
    "X": "ᛉ",
    "Y": "✶",
    "Z": "☵",
}


def build_keyword_key(alphabet: str = ALPHABET, keyword: str = KEYWORD) -> dict[str, str]:
    """Build a plaintext -> cipher alphabet from a keyword.

    Duplicate letters in ``keyword`` are dropped and the remaining alphabet
    fills the tail, producing a bijective substitution over ``alphabet``.
    """
    if not alphabet:
        raise ValueError("alphabet must be non-empty")
    if not keyword:
        raise ValueError("keyword must be non-empty")
    order: list[str] = []
    seen: set[str] = set()
    for ch in keyword.upper():
        if ch in alphabet and ch not in seen:
            seen.add(ch)
            order.append(ch)
    for ch in alphabet:
        if ch not in seen:
            order.append(ch)
    if len(order) < len(alphabet):
        raise ValueError("keyword produced an incomplete cipher alphabet")
    return {plain: cipher for plain, cipher in zip(alphabet, order)}


def invert_key(key: Mapping[str, str]) -> dict[str, str]:
    """Invert a substitution mapping (cipher -> plaintext)."""
    inverse: dict[str, str] = {}
    for plain, cipher in key.items():
        if cipher in inverse:
            raise ValueError(f"substitution is not bijective at cipher symbol {cipher!r}")
        inverse[cipher] = plain
    return inverse


def encipher(text: str, key: Mapping[str, str]) -> str:
    """Encipher ``text`` with a substitution key; non-letters pass through."""
    return "".join(key.get(ch.upper(), ch) if ch.isalpha() else ch for ch in text)


def decipher(text: str, key: Mapping[str, str]) -> str:
    """Decipher ``text`` using the inverse of ``key``; non-letters pass through."""
    inverse = invert_key(key)
    return "".join(inverse.get(ch.upper(), ch) if ch.isalpha() else ch for ch in text)


def frequency_table(text: str) -> dict[str, int]:
    """Count occurrences of each A-Z letter in ``text`` (case-insensitive)."""
    counts: dict[str, int] = {}
    for ch in text.upper():
        if ch in ALPHABET:
            counts[ch] = counts.get(ch, 0) + 1
    return counts


def _normalized_frequencies(counts: Mapping[str, int]) -> dict[str, float]:
    total = sum(counts.values())
    if total == 0:
        return {}
    return {ch: count / total for ch, count in counts.items()}


def score_plaintext(text: str, reference: Mapping[str, float] | None = None) -> float:
    """Cosine similarity between the letter-frequency profile of ``text`` and a reference.

    ``reference`` defaults to :data:`ENGLISH_FREQUENCIES`. Returns 0.0 for
    empty/blank input.
    """
    ref: Mapping[str, float] = reference if reference is not None else ENGLISH_FREQUENCIES
    counts = frequency_table(text)
    if not counts:
        return 0.0
    observed = _normalized_frequencies(counts)
    dot = 0.0
    for ch in ALPHABET:
        dot += observed.get(ch, 0.0) * ref.get(ch, 0.0)
    obs_norm = sum(v * v for v in observed.values()) ** 0.5
    ref_norm = sum(v * v for v in ref.values()) ** 0.5
    if obs_norm == 0.0 or ref_norm == 0.0:
        return 0.0
    return float(dot / (obs_norm * ref_norm))


def solve_substitution(ciphertext: str, reference: Mapping[str, float] | None = None) -> tuple[str, float]:
    """Best-effort frequency attack on an unknown substitution cipher.

    Symbols are ranked by observed frequency and matched to reference letters
    ranked by expected frequency (most frequent first). Returns a candidate
    plaintext and its :func:`score_plaintext` cosine similarity.

    **This does not recover the plaintext of a short intercept.** On the
    canonical 27-character communiqué it returns
    ``"IEAEAHE LTON ORT NAEIT SDOT"`` — unreadable — while still scoring 0.926
    against the English reference, because at this length the observed
    frequency ranking is dominated by sampling noise and the score measures only
    the profile the substitution was *built* to have. Treat the score as a
    ranking heuristic over many candidates, never as evidence of recovery. Both
    the exact output and the misleadingly high score are pinned in
    ``tests/test_coded_comms.py`` so a regression in either is visible.
    """
    ref: Mapping[str, float] = reference if reference is not None else ENGLISH_FREQUENCIES
    counts = frequency_table(ciphertext)
    if not counts:
        return "", 0.0
    ranked_symbols = [ch for ch, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
    ranked_ref = [ch for ch, _ in sorted(ref.items(), key=lambda kv: (-kv[1], kv[0]))]
    guess: dict[str, str] = dict(zip(ranked_symbols, ranked_ref))
    candidate = "".join(guess.get(ch.upper(), ch) if ch.isalpha() else ch for ch in ciphertext)
    return candidate, score_plaintext(candidate, ref)


def symbol_roster(alphabet: str = ALPHABET) -> dict[str, str]:
    """The deterministic voodoo glyph roster (letter -> symbol).

    Guarantees a bijective mapping over the given alphabet so a message can be
    rendered entirely in glyphs and decoded back.
    """
    symbols = [ROSTER_SYMBOLS[ch] for ch in alphabet]
    if len(set(symbols)) != len(alphabet):
        raise ValueError("symbol roster is not bijective over the alphabet")
    return {ch: sym for ch, sym in zip(alphabet, symbols)}


def SAN_MONIQUE_MESSAGE(key: Mapping[str, str] | None = None) -> tuple[str, str]:
    """Return ``(plaintext, ciphertext)`` for the canonical San Monique message.

    Upper-cased like the canonical datasets it derives from, but a *function*,
    not a constant: the ciphertext depends on the key. If ``key`` is omitted the
    canonical keyword key is used, so the ciphertext is stable across calls.
    """
    resolved = key if key is not None else build_keyword_key()
    return SAN_MONIQUE_PLAINTEXT, encipher(SAN_MONIQUE_PLAINTEXT, resolved)
