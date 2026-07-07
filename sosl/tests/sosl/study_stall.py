"""Anatomy of one automaton's SoS learner stall.

    python3 -m tests.sosl.study_stall <hoa>

For a single input this prints, in order: the canonical deterministic /complete/
transition-based/generic form ``D`` the sos layer imports; the reference
invariant ``I(L)`` (``.sos``); the learner's pre-equivalence **stall** partition
and its **learned** fixpoint, each as classes of member words; the P1 (hypothesis
acceptor) and F2 (exported-invariant acceptor) verdicts; and, when the export is
non-canonical, the shortest lasso on which the exported invariant disagrees with
the teacher — the concrete witness of the two-sided split saturation must add.

A prototype study tool for the surviving-stall specimens the census surfaces.
"""
from __future__ import annotations

import itertools
import sys
from typing import List, Optional, Tuple

from sosl.contract import Counterexample
from sosl.learn.export import export
from sosl.learn.learner import _build_hypothesis, _stabilize, process_counterexample
from sosl.learn.partition import Partition
from sosl.learn.table import Table
from sosl.sos import Lasso, dump_invariant
from sosl.sos.build import import_hoa, reference_of_hoa
from sosl.sos.io.serialize import render_word
from sosl.teacher import HoaTeacher


def _drive(teacher: HoaTeacher) -> Tuple[Partition, Partition, object]:
    """Learn to the equivalence fixpoint; return ``(stall, final, invariant)``
    where ``stall`` is the first closed/consistent partition (before any
    equivalence query) and ``final`` the fixpoint the teacher certifies."""
    table = Table(teacher.alphabet, teacher.member)
    stall: Optional[Partition] = None
    while True:
        p = _stabilize(table)
        if stall is None:
            stall = p
        res = teacher.equiv(_build_hypothesis(table, p))
        if not isinstance(res, Counterexample):
            break
        process_counterexample(table, p, res.lasso)
    assert stall is not None
    return stall, p, export(p, teacher.member)


def _dump_partition(title: str, teacher: HoaTeacher, p: Partition) -> None:
    ab = teacher.alphabet
    print(f"{title} ({p.n} classes):")
    for c in range(p.n):
        words = sorted(p.members[c], key=lambda w: (len(w), w))
        rendered = ", ".join(render_word(ab, w) for w in words)
        print(f"  {render_word(ab, p.members[c][0]) if p.members[c] else '?'}"
              f" = {{{rendered}}}")


def _first_export_divergence(inv: object, teacher: HoaTeacher,
                             stem_max: int = 3, loop_max: int = 3
                             ) -> Optional[Tuple[Lasso, bool, bool]]:
    """The shortlex-least lasso where ``inv.member`` disagrees with the teacher,
    or ``None`` if they agree to the bound."""
    letters = teacher.alphabet.letters()
    for slen in range(stem_max + 1):
        for stem in itertools.product(letters, repeat=slen):
            for llen in range(1, loop_max + 1):
                for loop in itertools.product(letters, repeat=llen):
                    la = Lasso(tuple(stem), tuple(loop))
                    iv, te = inv.member(la), teacher.member(la)
                    if iv != te:
                        return la, iv, te
    return None


def run(path: str) -> int:
    ref = reference_of_hoa(path)
    teacher = HoaTeacher.of_hoa(path)
    stall, final, inv = _drive(teacher)

    print(f"=== {path} ===\n")
    print("Canonical form D (deterministic, complete, transition-based, generic):")
    print(import_hoa(path).to_str("hoa"))
    print(f"Reference invariant I(L)  ({ref.n} classes):")
    print(dump_invariant(ref))
    _dump_partition("\nStall partition (pre-equivalence fixpoint)", teacher, stall)
    _dump_partition("\nLearned fixpoint", teacher, final)
    print(f"\nlearned classes: {final.n}   reference classes: {ref.n}   "
          f"byte-equal: {dump_invariant(ref) == dump_invariant(inv)}")
    print("\nLearned (exported) invariant — the non-canonical .sos:")
    print(dump_invariant(inv))

    div = _first_export_divergence(inv, teacher)
    if div is None:
        print("export acceptor (F2): agrees with the teacher to the bound")
    else:
        la, iv, te = div
        print(f"export acceptor (F2): first divergence at {la}  "
              f"exported={iv} teacher={te}")
    return 0


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: study_stall <hoa>", file=sys.stderr)
        return 2
    return run(sys.argv[1])


if __name__ == "__main__":
    raise SystemExit(main())
