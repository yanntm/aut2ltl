"""Reference vs learner: byte-equality of the canonical .sos (sosl.reference).

Single formula per run. From the repo root:

    python3 -m tests.sosl.reference_vs_learner "GF a"
    python3 -m tests.sosl.reference_vs_learner "F(a & X a)"

Builds the reference invariant (definability pipeline) and the learned invariant
(query learner) for the same language and compares their canonical `.sos`. Prints
MATCH, or DIFFER with both dumps (the expected outcome where the M2 learner,
without saturation, reaches an acceptance-correct but non-canonical fixpoint).
"""
from __future__ import annotations

import itertools
import random
import sys
from typing import Iterator

from sosl.learn import learn
from sosl.objects import Invariant, Lasso, dump_invariant
from sosl.teacher import HoaTeacher
from sosl.reference import reference_of_ltl

# Cap on lassos checked, so the acceptor check never becomes a 10^8 loop on a
# large alphabet (the count is ~2^(AP*(stem_max+loop_max)) if enumerated whole).
BUDGET = 20_000


def _exhaustive_count(n_letters: int, stem_max: int, loop_max: int) -> int:
    stems = sum(n_letters ** s for s in range(stem_max + 1))
    loops = sum(n_letters ** l for l in range(1, loop_max + 1))
    return stems * loops


def _all_lassos(letters: list[int], stem_max: int, loop_max: int) -> Iterator[Lasso]:
    """Every lasso with |stem| in [0, stem_max] and |loop| in [1, loop_max]."""
    for slen in range(stem_max + 1):
        for stem in itertools.product(letters, repeat=slen):
            for llen in range(1, loop_max + 1):
                for loop in itertools.product(letters, repeat=llen):
                    yield Lasso(tuple(stem), tuple(loop))


def _sampled_lassos(
    letters: list[int], stem_max: int, loop_max: int, count: int, seed: int = 4242
) -> Iterator[Lasso]:
    """`count` random lassos within the same bounds (deterministic seed)."""
    rng = random.Random(seed)
    for _ in range(count):
        stem = tuple(rng.choice(letters) for _ in range(rng.randint(0, stem_max)))
        loop = tuple(rng.choice(letters) for _ in range(rng.randint(1, loop_max)))
        yield Lasso(stem, loop)


def acceptor_check(
    learned: Invariant, teacher: HoaTeacher, stem_max: int = 3, loop_max: int = 3
) -> tuple[bool, int, str]:
    """Acceptance-correctness: learned read-off vs teacher on lassos up to the
    bound. Exhaustive (a certificate) when the space fits in BUDGET, else a
    deterministic random sample of BUDGET lassos. Returns (ok, n_checked, mode)."""
    letters = teacher.alphabet.letters()
    total = _exhaustive_count(len(letters), stem_max, loop_max)
    if total <= BUDGET:
        lassos, mode = _all_lassos(letters, stem_max, loop_max), "exhaustive"
    else:
        lassos = _sampled_lassos(letters, stem_max, loop_max, BUDGET)
        mode = f"sampled {BUDGET}/{total}"
    n = 0
    for lasso in lassos:
        n += 1
        if learned.member(lasso) != teacher.member(lasso):
            print(f"  ACCEPTOR MISMATCH at {lasso}: "
                  f"learned={learned.member(lasso)} teacher={teacher.member(lasso)}")
            return False, n, mode
    return True, n, mode


def run(formula: str) -> int:
    ref = reference_of_ltl(formula)
    teacher = HoaTeacher.of_ltl(formula)
    stats: dict = {}
    learned = learn(teacher, teacher.alphabet, stats)

    ref_sos = dump_invariant(ref)
    learned_sos = dump_invariant(learned)
    print(f"formula: {formula!r}")
    print(f"reference classes: {ref.n}   learned: {stats}")

    ok, n_checked, mode = acceptor_check(learned, teacher)
    verdict = "acceptance-correct" if ok else "ACCEPTANCE-WRONG"
    print(f"acceptor check: {verdict} ({mode}, {n_checked} lassos, "
          f"|stem|<=3,|loop|<=3)")

    if ref_sos == learned_sos:
        print("MATCH (byte-equal canonical .sos)")
        print(ref_sos, end="")
        return 0 if ok else 1
    print("DIFFER (M2 non-canonical fixpoint; canonicity awaits saturation/M3)")
    print("--- reference .sos ---")
    print(ref_sos, end="")
    print("--- learned .sos ---")
    print(learned_sos, end="")
    return 0 if ok else 1


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: reference_vs_learner <ltl-formula>", file=sys.stderr)
        return 2
    return run(sys.argv[1])


if __name__ == "__main__":
    raise SystemExit(main())
