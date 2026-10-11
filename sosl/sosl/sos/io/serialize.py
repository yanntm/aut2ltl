"""Canonical text serialization of invariants (`.sos`).

The `.sos` form is a byte-canonical normal form: two invariants over the same AP
denote the same language iff their `dump_invariant` outputs are byte-equal (the
soundness criterion of the whole tool). Canonicity is inherited from the
invariant — classes in id order, letters in mask order, accept pairs sorted — so
`dump` only has to be deterministic; it does not re-key.

Only non-empty-word classes are stored, with IDs ``1..n``. The fresh identity
at internal ID 0 is implicit; loading restores its key, row and column.

A letter is written as a Boolean cube over *all* the propositions in canonical
order — each proposition, or its negation, joined by ``&`` (``a&!b``); the
0-proposition alphabet's one letter is ``t``. A word is its letters joined by
``;`` (``eps`` for the empty word). This is the cube form of
sos_format.md; a letter names every proposition, so it is
unambiguous over a multi-AP alphabet (``a&!b``, not ``{a}``).
"""
from __future__ import annotations

from typing import List, Tuple

from ..alphabet import EMPTY, Alphabet, Letter, Word
from ..invariant import Invariant

SOS_MAGIC = "SOS v1"


# --- letters and words -----------------------------------------------------

def render_letter(ab: Alphabet, a: Letter) -> str:
    """``a&!b`` — a Boolean cube naming every proposition (``t`` for a 0-AP
    alphabet)."""
    if not ab.aps:
        return "t"
    trues = set(ab.true_aps(a))
    return "&".join(name if name in trues else f"!{name}" for name in ab.aps)


def parse_letter(ab: Alphabet, tok: str) -> Letter:
    """Inverse of `render_letter`."""
    tok = tok.strip()
    if tok == "t":
        return ab.letter_of([])
    trues = [lit for lit in tok.split("&") if not lit.startswith("!")]
    return ab.letter_of(trues)


def render_word(ab: Alphabet, w: Word) -> str:
    """``{a};{}`` — letters joined by ``;`` (``eps`` for the empty word)."""
    return ";".join(render_letter(ab, a) for a in w) if w else "eps"


def parse_word(ab: Alphabet, s: str) -> Word:
    """Inverse of `render_word`."""
    s = s.strip()
    if s == "eps":
        return EMPTY
    return tuple(parse_letter(ab, t) for t in s.split(";"))


# --- shared parse helper ---------------------------------------------------

def _nonblank(text: str) -> List[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def _read_header(lines: List[str], magic: str) -> Tuple[Alphabet, int, int]:
    """Consume the common prefix (magic, ap, classes); return the alphabet, the
    class count, and the index of the first class line."""
    assert lines[0] == magic, lines[0]
    assert lines[1].startswith("ap:"), lines[1]
    ab = Alphabet.of(lines[1][len("ap:"):].split())
    assert lines[2].startswith("classes:"), lines[2]
    n = int(lines[2].split(":")[1])
    return ab, n, 3


def _read_keys(ab: Alphabet, lines: List[str], i: int, n: int) -> Tuple[List[Word], int]:
    keys: List[Word] = [EMPTY] * (n + 1)
    for cid in range(1, n + 1):
        cid_str, _, key_str = lines[i].partition(" ")
        assert int(cid_str) == cid, lines[i]
        key = parse_word(ab, key_str)
        assert key != EMPTY, lines[i]
        keys[cid] = key
        i += 1
    return keys, i


# --- invariant (.sos) ------------------------------------------------------

def dump_invariant(inv: Invariant) -> str:
    """The canonical `.sos` text for ``inv`` (trailing newline included)."""
    ab = inv.alphabet
    assert inv.identity == 0 and inv.keys[0] == EMPTY
    out: List[str] = [SOS_MAGIC, "ap: " + " ".join(ab.aps), f"classes: {inv.class_count}"]
    for c in range(1, inv.n):
        out.append(f"{c} {render_word(ab, inv.keys[c])}")
    out.append(
        "letters: "
        + " ".join(f"{render_letter(ab, Letter(a))}->{inv.letter_class[a]}"
                   for a in range(ab.size))
    )
    out.append("mult:")
    for c in range(1, inv.n):
        out.append(f"{c}: " + " ".join(str(v) for v in inv.mult[c][1:]))
    out.append("accept:")
    for s, e in sorted(inv.accept):
        out.append(f"{s} {e}")
    return "\n".join(out) + "\n"


def load_invariant(text: str) -> Invariant:
    """Parse `.sos`, adjoining the implicit identity at internal class 0.

    Every nonblank line after ``accept:`` must be an accepting pair.
    """
    lines = _nonblank(text)
    ab, n, i = _read_header(lines, SOS_MAGIC)
    keys, i = _read_keys(ab, lines, i, n)

    assert lines[i].startswith("letters:"), lines[i]
    letter_class = [0] * ab.size
    for tok in lines[i][len("letters:"):].split():
        lhs, _, rhs = tok.partition("->")
        letter_class[parse_letter(ab, lhs)] = int(rhs)
    assert all(1 <= c <= n for c in letter_class), letter_class
    i += 1

    assert lines[i] == "mult:", lines[i]
    i += 1
    mult: List[Tuple[int, ...]] = [tuple(range(n + 1))]
    for cid in range(1, n + 1):
        cid_str, _, rest = lines[i].partition(":")
        assert int(cid_str) == cid, lines[i]
        row = tuple(int(x) for x in rest.split())
        assert len(row) == n and all(1 <= c <= n for c in row), lines[i]
        mult.append((cid,) + row)
        i += 1

    assert lines[i] == "accept:", lines[i]
    i += 1
    accept = set()
    while i < len(lines):
        parts = lines[i].split()
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            raise ValueError(f"Expected accepting pair, got {lines[i]!r}")
        pair = (int(parts[0]), int(parts[1]))
        assert all(1 <= c <= n for c in pair), lines[i]
        accept.add(pair)
        i += 1

    return Invariant(
        alphabet=ab,
        keys=tuple(keys),
        letter_class=tuple(letter_class),
        mult=tuple(mult),
        accept=frozenset(accept),
        identity=0,
    )
