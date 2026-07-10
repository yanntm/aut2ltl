"""K-E7 positive controls (K-E0 step 3): both mechanisms must be detected.

    python3 -m tests.cascade.k_e7_controls floor|evenblocks [k]

The scan must dump the floor witness's aperiodic *absorption* failure
`e·z·e = z <_J e` on its frozen final layer, and `EvenBlocks`' *group* failure
`f·z·f = z <_J f` on its frozen layer at k=2..3. A stratum showing no failure
means the scan is not testing anything (K-E7 decision rule).
"""
from __future__ import annotations

import sys
from typing import List

import spot

from aut2ltl.language import Language
from aut2ltl.sos2ltl.bridge import invariant_of_language
from aut2ltl.sos2ltl.cayley import build
from sosl.sos import Invariant, load_invariant
from sosl.sos.classify.aperiodic import is_aperiodic

from tests.cascade.sandwich import scan_layer
from tests.cascade.k_e0 import CASES

EVENBLOCKS = "samples/fixtures/hoa/sos/evenblocks.sos"


def load(case: str) -> Invariant:
    if case == "evenblocks":
        with open(EVENBLOCKS) as f:
            return load_invariant(f.read())
    return invariant_of_language(Language.of(spot.translate(CASES[case])))


def main(argv: List[str]) -> int:
    case = argv[0]
    k = int(argv[1]) if len(argv) > 1 else (2 if case == "evenblocks" else 0)
    inv = load(case)
    ap = is_aperiodic(inv)
    cay = build(inv)
    R = frozenset(cay.layers[-1])
    print(f"# {case}: aperiodic={ap}  final layer {{{','.join(map(str,sorted(R)))}}} at k={k}")

    fails, passes = scan_layer(inv, R, k, ap, budget=200000)
    by_mech: dict = {}
    for fl in fails:
        by_mech.setdefault(fl.mechanism, []).append(fl)
    print(f"  PASS pairs={passes}  FAIL pairs={len(fails)}  "
          f"mechanisms={ {m: len(v) for m, v in by_mech.items()} }")
    for m, v in sorted(by_mech.items()):
        fl = v[0]
        print(f"  [{m}] e={fl.e} e'={fl.ep} -> e·e'·e={fl.s}, e'·e·e'={fl.sp}"
              f"  (base {fl.base}, |F|={len(fl.F)})   (+{len(v)-1} more)")

    want = "absorption" if case != "evenblocks" else "group"
    detected = want in by_mech
    print(f"  expected mechanism '{want}' detected: {detected}")
    print("OK" if detected else "FAIL")
    return 0 if detected else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
