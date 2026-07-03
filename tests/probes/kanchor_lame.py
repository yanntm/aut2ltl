"""Dump the L/A/M/E split kanchor reads off ONE input.

Usage: python3 tests/probes/kanchor_lame.py <file.hoa | LTL formula>

Builds the exact form the brick reads (`sbacc(tgba(L))` of the initial SCC),
prints the component's edges, per state the k = 1 form of the L/A/M/E split
with the promoted guard `P` (the self-loop part reclassified into `δ↑`), and
the k = 1 / k = 2 precondition verdicts (`None` = the level passes).
Diagnostic printer only — no verdict logic of its own.
"""

import os
import sys
from typing import Dict, Set

import spot
import buddy

from aut2ltl.language import Language
from aut2ltl.kanchor.shape import init_scc_states, lame_data
from aut2ltl.kanchor.windows import k1_violation, k2_violation


def fmt(aut: "spot.twa_graph", b: "buddy.bdd") -> str:
    return spot.bdd_format_formula(aut.get_dict(), b)


def main(arg: str) -> int:
    src = spot.automaton(arg) if os.path.exists(arg) else spot.translate(arg)
    lang = Language.of(src)
    aut: "spot.twa_graph" = spot.postprocess(lang.tgba(), "sbacc")
    q0 = int(aut.get_init_state_number())
    C: Set[int] = init_scc_states(aut, q0)
    print(f"q0={q0}  C={sorted(C)}  states={aut.num_states()} "
          f"acc={aut.get_acceptance()}")
    for s in sorted(C):
        marks = aut.state_acc_sets(s)
        print(f"state {s}{'  ' + str(marks) if marks.count() else ''}:")
        for e in aut.out(s):
            kind = ("loop" if e.dst == s else
                    "move" if e.dst in C else "EXIT")
            print(f"    [{fmt(aut, e.cond)}] -> {e.dst}  ({kind})")
    Lr, Ar, Mr, exits, P = lame_data(aut, C)
    L: Dict[int, "buddy.bdd"] = {s: Lr[s] - P[s] for s in C}
    A: Dict[int, "buddy.bdd"] = {s: Ar[s] | P[s] for s in C}
    M: Dict[int, "buddy.bdd"] = {s: Mr[s] | P[s] for s in C}
    print("-- L/A/M/E (k = 1 form; P = promoted guard, in A and M) --")
    for s in sorted(C):
        print(f"state {s}: L={fmt(aut, L[s])}  A={fmt(aut, A[s])}  "
              f"M={fmt(aut, M[s])}  E={[(fmt(aut, g), d) for g, d in exits[s]]}"
              + (f"  P={fmt(aut, P[s])}"
                 if P[s] != buddy.bddfalse else ""))
    print(f"k=1 violation: {k1_violation(L, A)}")
    print(f"k=2 violation: {k2_violation(aut, C, q0, L, A, P)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
