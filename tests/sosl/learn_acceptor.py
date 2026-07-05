"""Acceptance-correctness probe for the M2 learner (sosl.learn).

Single formula per run (respects the per-example cap). Run from the repo root:

    python3 -m tests.sosl.learn_acceptor "GF a & GF b"
    python3 -m tests.sosl.learn_acceptor "F a"        [n_random]

Learns the invariant of the LTL formula's language from the white-box teacher
and checks that its membership read-off agrees with the teacher on many seeded
random lassos (the acceptor check). Prints the run stats (classes, queries,
equivalence rounds, counterexamples) and OK / a witness of disagreement.
"""
from __future__ import annotations

import random
import sys

from sosl.learn import learn
from sosl.objects import Lasso
from sosl.teacher import HoaTeacher


def run(formula: str, n_random: int) -> int:
    t = HoaTeacher.of_ltl(formula)
    stats: dict = {}
    learned = learn(t, t.alphabet, stats)
    print(f"formula: {formula!r}")
    print(f"stats:   {stats}")

    letters = t.alphabet.letters()
    rng = random.Random(0xC0FFEE)
    for _ in range(n_random):
        stem = tuple(rng.choice(letters) for _ in range(rng.randint(0, 4)))
        loop = tuple(rng.choice(letters) for _ in range(rng.randint(1, 4)))
        lasso = Lasso(stem, loop)
        if learned.member(lasso) != t.member(lasso):
            print(f"MISMATCH stem={stem} loop={loop}: "
                  f"learned={learned.member(lasso)} teacher={t.member(lasso)}")
            return 1
    print(f"OK acceptor agrees on {n_random} random lassos")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: learn_acceptor <ltl-formula> [n_random]", file=sys.stderr)
        return 2
    formula = sys.argv[1]
    n_random = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    return run(formula, n_random)


if __name__ == "__main__":
    raise SystemExit(main())
