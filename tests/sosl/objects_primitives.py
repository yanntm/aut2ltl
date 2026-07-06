"""Property checks for the sosl.objects primitives (alphabet + lasso).

Self-contained, no external input. Run from the repo root:

    python3 -m tests.sosl.objects_primitives

Prints one OK line per checked property, or raises AssertionError on the first
violation.
"""
from __future__ import annotations

from sosl.objects import EMPTY, Alphabet, Lasso, shortlex_key


def check_canonical_order() -> None:
    # Proposition names are sorted and de-duplicated regardless of input order.
    ab = Alphabet.of(["b", "a", "b"])
    assert ab.aps == ("a", "b"), ab.aps
    assert ab.size == 4, ab.size
    print("OK canonical AP order + size")


def check_letter_roundtrip() -> None:
    ab = Alphabet.of(["a", "b", "c"])
    # Every letter round-trips through its set of true propositions.
    for a in ab.letters():
        assert ab.letter_of(ab.true_aps(a)) == a, a
    # First AP is the most significant bit: a=bit2, b=bit1, c=bit0.
    assert ab.true_aps(ab.letter_of(["a"])) == ["a"]
    assert ab.letter_of(["a"]) == 0b100
    assert ab.letter_of(["c"]) == 0b001
    assert ab.letter_of(["a", "c"]) == 0b101
    print("OK letter <-> true-AP round trip")


def check_canonical_letter_order() -> None:
    # Two APs: canonical order is by characteristic tuple, a most significant,
    # absent<present: {} < {b} < {a} < {a,b} (research_notes/sos_format.md).
    ab = Alphabet.of(["a", "b"])
    order = [ab.true_aps(a) for a in ab.letters()]
    assert order == [[], ["b"], ["a"], ["a", "b"]], order
    print("OK canonical letter order (char-tuple, a most significant)")


def check_shortlex() -> None:
    ab = Alphabet.of(["a"])  # letters: 0 = {}, 1 = {a}
    z, o = ab.letters()
    words = [(o,), EMPTY, (z, o), (z,), (o, z)]
    ordered = sorted(words, key=shortlex_key)
    # Shorter first; equal length by letterwise mask order (0 before 1).
    assert ordered == [EMPTY, (z,), (o,), (z, o), (o, z)], ordered
    print("OK shortlex order")


def check_lasso() -> None:
    ab = Alphabet.of(["a"])
    z, o = ab.letters()
    try:
        Lasso((z,), EMPTY)  # empty loop rejected
        raise AssertionError("empty loop should be rejected")
    except ValueError:
        pass
    lo = Lasso((z,), (o,))
    r = lo.raised_to(3)
    # (u, v) -> (u.v^3, v^3): same denoted word, loop at power 3.
    assert r.stem == (z, o, o, o) and r.loop == (o, o, o), (r.stem, r.loop)
    print("OK lasso validation + raised_to")


def main() -> int:
    check_canonical_order()
    check_letter_roundtrip()
    check_canonical_letter_order()
    check_shortlex()
    check_lasso()
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
