"""K-E0 step 6: saturation / raw-exploration agreement + closure assertion.

    python3 -m tests.cascade.k_e0_sat floor|gaFb [k]

For every entry cone / full-memory base of the final layer, checks that raw
ALG-5 `CL(x)` is closed under `(F₁,d₁),(F₂,d₂) ↦ (F₁∪F₂, M(d₁,d₂))` and that
saturating its prime seeds reproduces it exactly. A mismatch is a closure bug.
"""
from __future__ import annotations

import sys
from typing import List

import spot

from aut2ltl.language import Language
from aut2ltl.sos2ltl.bridge import invariant_of_language
from aut2ltl.sos2ltl.cayley import build

from tests.cascade.config_machine import (
    build_cone, closure_at, first_returns, is_closed, quotient_letters, saturate,
)
from tests.cascade.k_e0 import CASES


def main(argv: List[str]) -> int:
    case = argv[0]
    k = int(argv[1]) if len(argv) > 1 else 0
    budget = 200000
    inv = invariant_of_language(Language.of(spot.translate(CASES[case])))
    cay = build(inv)
    R = frozenset(cay.layers[-1])
    sigma = quotient_letters(inv)
    print(f"# {case}: final layer {{{','.join(map(str,sorted(R)))}}} at k={k}")

    ok = True
    for c in sorted(R):
        cone = build_cone(inv, R, c, k, sigma)
        for x in cone.fm_nodes:
            cl = closure_at(inv, cone, x, budget)
            prims = first_returns(inv, cone, x, budget)
            if cl is None or prims is None:
                print(f"  entry {c} base {x}: BUDGET")
                ok = False
                continue
            bad = is_closed(inv, cl)
            sat = saturate(inv, prims)
            agree = sat == cl
            ok = ok and bad is None and agree
            print(f"  entry {c} base {x}: |CL|={len(cl)} closed={bad is None} "
                  f"|first-returns|={len(prims)} saturate==raw={agree}"
                  + ("" if bad is None else f"  MISSING {bad[2]}")
                  + ("" if agree else f"  raw-sat={len(cl - sat)}"))
    print("OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
