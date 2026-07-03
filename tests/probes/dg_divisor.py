"""Dump the local divisors of the quotient algebra of ONE HOA file — the
display client of `aut2ltl/bls/definability/dg/divisor.py`: for every visible
letter (class ≠ identity), the divisor at its image `m` — carrier (as base
class ids with their canonical keys), unit position, and the `∘` table — with
the v0 pivot (least visible letter, `dg/algorithm.md` layer 8) marked.

Usage:  python3 tests/probes/dg_divisor.py <file.hoa>

On a group-bearing quotient the strict-decrease assert of `local_divisor` can
fire (identity inside `mT ∩ Tm`); the probe reports the firing per letter and
exits 2 if any fired — demonstrating the backstop, not a verdict.
"""
from __future__ import annotations

import sys

from aut2ltl.bls.definability.dg.divisor import Divisor, local_divisor
from dg_common import DgData, print_d_line, quotient_of_hoa


def main(path: str) -> int:
    data = quotient_of_hoa(path)
    if data is None:
        print("closure  : blew the cap")
        return 2
    print_d_line(data)
    alg = data.alg
    print(f"quotient : {len(alg)} classes"
          + ("  (group-bearing -- dg proper would refuse)" if data.group else ""))

    visible = [li for li in range(len(alg.letters)) if alg.letter_cls[li] != 0]
    if not visible:
        print("pivot    : none (every letter invisible -- base case)")
        return 0
    pivot: int = visible[0]

    fired = False
    for li in visible:
        m: int = alg.letter_cls[li]
        tag = "  <- v0 pivot" if li == pivot else ""
        print(f"letter {alg.letters[li]!r} -> m = {m} [{alg.key(m)}]{tag}")
        try:
            div: Divisor = local_divisor(alg.mult, m)
        except AssertionError as e:
            print(f"  ASSERT FIRED: {e}")
            fired = True
            continue
        print(f"  carrier : {{{', '.join(str(c) for c in div.carrier)}}}"
              f"  ({len(alg)} -> {len(div)}), unit at position {div.unit}")
        print("  mult    :  (positions; base ids in carrier order)")
        for row in div.mult:
            print("    " + " ".join(str(x) for x in row))
    return 2 if fired else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
