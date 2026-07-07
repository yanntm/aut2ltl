"""Checks for the white-box teacher membership (sosl.teacher.whitebox).

Self-contained (uses spot to build the target automata). Run from the `sosl/` subtree root:

    python3 -m tests.sosl.teacher_member

Verifies simulation on GF a (infinitely often), FG a (eventually always) and
G a (safety) against hand-known lasso answers, then cross-checks the GF a
teacher against the GF a invariant read-off on seeded random lassos (a preview
of the two-oracle harness). Prints OK lines, or raises on the first failure.
"""
from __future__ import annotations

import random

from sosl.sos import EMPTY, Alphabet, Invariant, Lasso
from sosl.teacher import HoaTeacher


def gfa_invariant() -> Invariant:
    ab = Alphabet.of(["a"])
    return Invariant(
        alphabet=ab,
        keys=(EMPTY, (0,), (1,)),
        letter_class=(1, 2),
        mult=((0, 1, 2), (1, 1, 2), (2, 2, 2)),
        accept=frozenset({(2, 2)}),
        identity=0,
    )


# letters over AP={a}: {} = mask 0, {a} = mask 1
NOA, A = (0,), (1,)


def check_gf_a() -> None:
    t = HoaTeacher.of_ltl("GF a")
    assert t.member(Lasso(EMPTY, A)) is True
    assert t.member(Lasso(EMPTY, NOA)) is False
    assert t.member(Lasso(A, NOA)) is False           # finitely many a
    assert t.member(Lasso(EMPTY, NOA + A)) is True     # loop has an a
    print("OK GF a membership")


def check_fg_a() -> None:
    t = HoaTeacher.of_ltl("FG a")
    assert t.member(Lasso(EMPTY, A)) is True
    assert t.member(Lasso(EMPTY, NOA)) is False
    assert t.member(Lasso(EMPTY, A + NOA)) is False    # loop has a non-a
    assert t.member(Lasso(NOA + NOA, A)) is True       # stem irrelevant
    print("OK FG a membership")


def check_g_a() -> None:
    t = HoaTeacher.of_ltl("G a")
    assert t.member(Lasso(EMPTY, A)) is True
    assert t.member(Lasso(A, A)) is True
    assert t.member(Lasso(NOA, A)) is False            # stem violates safety
    assert t.member(Lasso(EMPTY, A + NOA)) is False    # loop violates safety
    print("OK G a membership")


def check_cross_with_invariant() -> None:
    t = HoaTeacher.of_ltl("GF a")
    inv = gfa_invariant()
    letters = t.alphabet.letters()
    rng = random.Random(20260705)
    for _ in range(2000):
        stem = tuple(rng.choice(letters) for _ in range(rng.randint(0, 3)))
        loop = tuple(rng.choice(letters) for _ in range(rng.randint(1, 3)))
        lasso = Lasso(stem, loop)
        assert t.member(lasso) == inv.member(lasso), (stem, loop)
    print("OK teacher vs GF a invariant on 2000 random lassos")


def main() -> int:
    check_gf_a()
    check_fg_a()
    check_g_a()
    check_cross_with_invariant()
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
