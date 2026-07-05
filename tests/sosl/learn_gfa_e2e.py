"""End-to-end learn of GF a (sosl.learn, M2 path: no counterexample needed).

Self-contained (white-box teacher). Run from the repo root:

    python3 -m tests.sosl.learn_gfa_e2e

Learns the invariant of GF a straight from the teacher (the seed omega column
already yields the right congruence, so equivalence is certified with no
counterexample), then checks the exported invariant against the hand-built one
by byte-equal `.sos`, and re-checks membership on random lassos against the
teacher. Prints the learned `.sos`, or raises on the first failure.
"""
from __future__ import annotations

import random

from sosl.learn import learn
from sosl.objects import EMPTY, Alphabet, Invariant, Lasso, dump_invariant
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


def check_learn_gfa() -> None:
    t = HoaTeacher.of_ltl("GF a")
    learned = learn(t, t.alphabet)
    expected = gfa_invariant()
    assert dump_invariant(learned) == dump_invariant(expected), (
        "learned invariant is not byte-equal to the reference:\n"
        + dump_invariant(learned)
    )
    print("--- learned .sos ---")
    print(dump_invariant(learned), end="")
    print("OK GF a learned == reference (byte-equal)")


def check_membership_agrees() -> None:
    t = HoaTeacher.of_ltl("GF a")
    learned = learn(t, t.alphabet)
    letters = t.alphabet.letters()
    rng = random.Random(4242)
    for _ in range(2000):
        stem = tuple(rng.choice(letters) for _ in range(rng.randint(0, 3)))
        loop = tuple(rng.choice(letters) for _ in range(rng.randint(1, 3)))
        lasso = Lasso(stem, loop)
        assert learned.member(lasso) == t.member(lasso), (stem, loop)
    print("OK learned invariant agrees with teacher on 2000 random lassos")


def main() -> int:
    check_learn_gfa()
    check_membership_agrees()
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
