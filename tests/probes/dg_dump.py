"""Dump the quotient algebra `S(L)+^1` of ONE HOA file, in the canonical form
the Diekert-Gastin synthesis consumes (`aut2ltl/bls/definability/dg/algorithm.md`):
the classes re-keyed by shortlex-least representative, the letter map, the
class multiplication table, the idempotents, and the accepting-pair table
`P(s, e)`, with the linked pairs (`s.e = s`, `e.e = e`) marked.

Usage:  python3 tests/probes/dg_dump.py <file.hoa>

A reading aid for the dg worked examples (its open point O4) — the input is
expected to be LTL-definable (aperiodic quotient); a group-bearing quotient is
reported and exits 2. No verdict logic of its own.
"""
from __future__ import annotations

import sys
from typing import Dict, List, Tuple

import spot

from aut2ltl.language import Language
from aut2ltl.bls.extract import extract_generators
from aut2ltl.bls.definability.witness.enriched import letter_elems
from aut2ltl.bls.definability.witness.support import valuation_to_letter
from aut2ltl.bls.definability.oracle.closure import close, Monoid
from aut2ltl.bls.definability.oracle.profile import profile
from aut2ltl.bls.definability.oracle.quotient import find_group
from aut2ltl.bls.definability.oracle.refine import refine
from aut2ltl.bls.definability.oracle.residuals import state_classes


def word_str(rep: List[int], names: List[str]) -> str:
    """A representative word as `letter;letter;...`, the empty word as `eps`."""
    return ";".join(names[li] for li in rep) if rep else "eps"


def main(path: str) -> int:
    lang = Language.of(spot.automaton(path))
    det = lang.det_generic_minimal()
    aut = spot.postprocess(det, "deterministic", "generic", "complete")
    gens, _masks, valuations = extract_generators(aut)
    names: List[str] = [valuation_to_letter(v) for v in valuations]
    init: int = aut.get_init_state_number()
    print(f"D        : {aut.num_states()} states, letters {names}, "
          f"init {init}, acc {aut.get_acceptance()}")

    letters = letter_elems(aut, valuations)
    mon: Monoid = close(letters, aut.num_states(), 20000)
    if mon is None:
        print("closure  : blew the cap")
        return 2

    st_cls = state_classes(aut)
    lin = [tuple(st_cls[st] for (st, _m) in el) for el in mon.elems]
    acc = aut.acc()
    prof = [profile(acc, el) for el in mon.elems]
    cls: List[int] = refine(mon, list(zip(lin, prof)))
    k: int = max(cls) + 1
    print(f"quotient : |EM1| = {len(mon)} elements -> {k} classes")
    if find_group(mon, cls) is not None:
        print("verdict  : NOT aperiodic -- not a dg input")
        return 2

    # Canonical re-keying (dg/algorithm.md layer 8): each class is keyed by its
    # shortlex-least representative word. Closure BFS order enumerates words
    # shortlex-first, so the first element met in each class carries that word.
    first_elem: Dict[int, int] = {}
    for ei in range(len(mon)):
        first_elem.setdefault(cls[ei], ei)
    order: List[int] = sorted(
        range(k), key=lambda c: (len(mon.rep[first_elem[c]]), mon.rep[first_elem[c]]))
    canon: Dict[int, int] = {c: i for i, c in enumerate(order)}
    key: List[str] = [word_str(mon.rep[first_elem[c]], names) for c in order]

    def cmul(i: int, j: int) -> int:
        """Class product via representatives (well-defined by the congruence)."""
        return canon[cls[mon.mult(first_elem[order[i]], first_elem[order[j]])]]

    idem: List[bool] = [cmul(i, i) == i for i in range(k)]
    print("classes  :")
    for i in range(k):
        members = sum(1 for c in cls if canon[c] == i)
        tag = "  idempotent" if idem[i] else ""
        print(f"  {i}: [{key[i]}]  ({members} elems){tag}")
    print("letters  : " + ", ".join(
        f"{names[li]} -> {canon[cls[mon.right[0][li]]]}" for li in range(len(names))))

    print("mult     :  (row i, col j) = i.j")
    for i in range(k):
        print("  " + " ".join(str(cmul(i, j)) for j in range(k)))

    # P(s, e): acceptance of u.z^w with [u] = s, [z] = e, from init -- the
    # profile of e's representative read at the state s's representative
    # reaches from init. Linked pairs (s.e = s, e.e = e) are the meaningful
    # entries; others are printed for completeness ('.' = not a linked pair).
    print("P(s,e)   :  rows s, cols e;  1/0 at linked pairs, '.' elsewhere")
    for s in range(k):
        row: List[str] = []
        st_s: int = mon.elems[first_elem[order[s]]][init][0]
        for e in range(k):
            if cmul(s, e) == s and idem[e]:
                row.append("1" if prof[first_elem[order[e]]][st_s] else "0")
            else:
                row.append(".")
        print(f"  {s}: " + " ".join(row))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
