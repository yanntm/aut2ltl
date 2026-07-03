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

from dg_common import print_d_line, quotient_of_hoa


def main(path: str) -> int:
    data = quotient_of_hoa(path)
    if data is None:
        print("closure  : blew the cap")
        return 2
    print_d_line(data)
    alg = data.alg
    k: int = len(alg)
    print(f"quotient : |EM1| = {len(data.mon)} elements -> {k} classes")
    if data.group is not None:
        print("verdict  : NOT aperiodic -- not a dg input")
        return 2

    print("classes  :")
    for i in range(k):
        tag = "  idempotent" if alg.idem[i] else ""
        print(f"  {i}: [{alg.key(i)}]{tag}")
    print("letters  : " + ", ".join(
        f"{alg.letters[li]} -> {alg.letter_cls[li]}" for li in range(len(alg.letters))))

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
