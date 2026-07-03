"""Dump the canonical quotient algebra `S(L)+^1` of ONE HOA file — the display
client of `aut2ltl/bls/definability/dg/morphism.py`: the frozen `Alg` value
(classes keyed by shortlex-least representative, the letter map, the class
multiplication table, the idempotents, the accepting-pair table `P` on the
linked pairs) printed table by table.

Usage:  python3 tests/probes/dg_dump.py <file.hoa>

A reading aid for the dg worked examples (`dg/algorithm.md` layers 12-13) —
the input is expected to be LTL-definable (aperiodic quotient); a group-bearing
quotient is reported and exits 2. No verdict logic of its own.
"""
from __future__ import annotations

import sys
from typing import List

import spot

from aut2ltl.language import Language
from aut2ltl.bls.extract import extract_generators
from aut2ltl.bls.definability.witness.enriched import letter_elems
from aut2ltl.bls.definability.witness.support import valuation_to_letter
from aut2ltl.bls.definability.oracle.closure import close, Monoid
from aut2ltl.bls.definability.oracle.profile import Profile, profile
from aut2ltl.bls.definability.oracle.quotient import find_group
from aut2ltl.bls.definability.oracle.refine import refine
from aut2ltl.bls.definability.oracle.residuals import state_classes
from aut2ltl.bls.definability.dg.morphism import Alg, build


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
    prof: List[Profile] = [profile(acc, el) for el in mon.elems]
    cls: List[int] = refine(mon, list(zip(lin, prof)))
    print(f"quotient : |EM1| = {len(mon)} elements -> {max(cls) + 1} classes")
    if find_group(mon, cls) is not None:
        print("verdict  : NOT aperiodic -- not a dg input")
        return 2

    alg: Alg = build(mon, cls, prof, names, init)
    k: int = len(alg)
    print("classes  :")
    for i in range(k):
        tag = "  idempotent" if alg.idem[i] else ""
        print(f"  {i}: [{alg.key(i)}]{tag}")
    print("letters  : " + ", ".join(
        f"{names[li]} -> {alg.letter_cls[li]}" for li in range(len(names))))

    print("mult     :  (row i, col j) = i.j")
    for i in range(k):
        print("  " + " ".join(str(alg.mult[i][j]) for j in range(k)))

    print("P(s,e)   :  rows s, cols e;  1/0 at linked pairs, '.' elsewhere")
    for s in range(k):
        print(f"  {s}: " + " ".join(
            "." if alg.P[s][e] is None else "1" if alg.P[s][e] else "0"
            for e in range(k)))
    print("accepting: " + (" ".join(
        f"({s},{e})" for (s, e) in alg.accepting_pairs()) or "none"))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
