"""The paper's three running examples, learned from their source automata.

    python3 -m tests.sosl.paper_examples

For each of `GF(aa)`, `Even`, `EvenBlocks` (HOA under
``research_notes/sos_figs/sources/``) this builds the reference invariant from
the automaton, runs the M2 learner against the same automaton as teacher, and
reports: the canonical class count ``|S(L)+1|`` (against the paper's fingerprint
table), whether the learned invariant is acceptance-correct, and whether it is
byte-equal to the reference (canonical) or a coarser M2 stall.

It also dumps the learner's *stall* partition (the closed/consistent fixpoint
before the first equivalence query) so it can be lined up word-for-word against
the paper's hand-computed intermediate tables (§4.1/§4.3 of the write-up).
"""
from __future__ import annotations

import itertools
import os
from typing import List, Tuple

from sosl.learn import learn
from sosl.learn.learner import _stabilize
from sosl.learn.table import Table
from sosl.sos import Lasso, dump_invariant
from sosl.sos.io.serialize import render_word
from sosl.sos.build import reference_of_hoa
from sosl.teacher import HoaTeacher

_SRC = os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir,
    "research_notes", "sos_figs", "sources",
)

# (name, hoa file, canonical |S(L)+1| from the paper's fingerprint tables)
CASES: List[Tuple[str, str, int]] = [
    ("GF(aa)", "gf_aa_parity.hoa", 6),
    ("Even", "even.hoa", 5),
    ("EvenBlocks", "evenblocks.hoa", 7),
]


def _acceptor_ok(learned, teacher, stem_max: int = 3, loop_max: int = 3) -> Tuple[bool, int]:
    letters = teacher.alphabet.letters()
    n = 0
    for slen in range(stem_max + 1):
        for stem in itertools.product(letters, repeat=slen):
            for llen in range(1, loop_max + 1):
                for loop in itertools.product(letters, repeat=llen):
                    la = Lasso(tuple(stem), tuple(loop))
                    n += 1
                    if learned.member(la) != teacher.member(la):
                        return False, n
    return True, n


def _stall_partition(teacher: HoaTeacher):
    """The learner's first closed/consistent fixpoint (the M2 'stall' before any
    equivalence query), as a list of (class-key, [member words])."""
    table = Table(teacher.alphabet, teacher.member)
    p = _stabilize(table)
    ab = teacher.alphabet
    out = []
    for c in range(p.n):
        words = sorted(p.members[c], key=lambda w: (len(w), w))
        rendered = [render_word(ab, w) for w in words]
        out.append((rendered[0] if rendered else "?", rendered))
    return p, out


def run() -> int:
    ok_all = True
    for name, fname, canonical in CASES:
        path = os.path.join(_SRC, fname)
        print(f"================= {name}  ({fname}) =================")
        ref = reference_of_hoa(path)
        teacher = HoaTeacher.of_hoa(path)
        stats: dict = {}
        learned = learn(teacher, teacher.alphabet, stats)
        acc_ok, n_checked = _acceptor_ok(learned, teacher)
        byte_eq = dump_invariant(ref) == dump_invariant(learned)

        print(f"canonical |S(L)+1|: reference={ref.n}  paper={canonical}  "
              f"{'OK' if ref.n == canonical else 'MISMATCH'}")
        print(f"learned: classes={learned.n}  {stats}")
        print(f"acceptor: {'acceptance-correct' if acc_ok else 'ACCEPTANCE-WRONG'} "
              f"({n_checked} lassos)")
        print(f"vs reference: {'BYTE-EQUAL (canonical)' if byte_eq else 'DIFFER (M2 stall)'}")

        _p, stall = _stall_partition(teacher)
        print(f"M2 stall partition ({len(stall)} classes):")
        for key, words in stall:
            print(f"  [{key}] = {{{', '.join(words)}}}")

        if ref.n != canonical or not acc_ok:
            ok_all = False
        print()

    print("ALL OK" if ok_all else "SOME CHECKS FAILED")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(run())
