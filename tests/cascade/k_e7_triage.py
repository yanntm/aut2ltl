"""K-E7 triage: dump sandwich failures of a given mechanism on one layer.

    python3 -m tests.cascade.k_e7_triage <id> <layer> <k> [mech]

Loads a corpus `.sos` by id, runs the (C)-decider + sandwich scan at width k,
and dumps every failure of `mech` (default 'other') in full: e, e′, s=e·e′·e,
sp=e′·e·e′, whether the sink coincides with an idempotent of the pair, its
𝒥-data, and whether the two loop classes actually split the verdict over
EntrySt (the identity is stronger than (C), so they usually do not).
"""
from __future__ import annotations

import sys
from typing import List

from aut2ltl.sos2ltl.cayley import build
from sosl.sos import load_invariant
from sosl.sos.classify.aperiodic import is_aperiodic

from tests.cascade.config_machine import (
    build_cone, decide, entry_stems, quotient_letters,
)
from tests.cascade.sandwich import scan, two_sided_ideals, j_equiv, j_minimal

CORPUS = "genaut/corpus/flat_canon/sos"


def entryst_of(inv, R, k, x):
    """EntrySt(x) unioned over every entry cone (the stem classes at base x)."""
    sigma = quotient_letters(inv)
    out = set()
    for c in sorted(R):
        cone = build_cone(inv, R, c, k, sigma)
        out |= set(entry_stems(inv, cone, sigma).get(x, frozenset()))
    return out


def main(argv: List[str]) -> int:
    lang_id, layer_id, k = argv[0], int(argv[1]), int(argv[2])
    want = argv[3] if len(argv) > 3 else "other"
    with open(f"{CORPUS}/{lang_id}.sos") as f:
        inv = load_invariant(f.read())
    ap = is_aperiodic(inv)
    cay = build(inv)
    R = frozenset(cay.layers[layer_id])
    ideals = two_sided_ideals(inv)
    zeros = [c for c in range(inv.n) if j_minimal(c, ideals)]
    print(f"# {lang_id} layer {layer_id} R={{{','.join(map(str,sorted(R)))}}} "
          f"k={k} aperiodic={ap} nC={inv.n}")
    print(f"  𝒥-minimal (zero) classes: {zeros}   accept P={sorted(inv.accept)}")

    dec = decide(inv, R, k, budget=150000, assert_sc=False)
    fails, passes = scan(inv, dec.closures, ap)
    sel = [fl for fl in fails if fl.mechanism == want]
    print(f"  (C) holds={dec.c_holds}; sandwich PASS={passes} FAIL={len(fails)}; "
          f"'{want}'={len(sel)}")

    for fl in sel[:6]:
        est = entryst_of(inv, R, k, fl.base)
        eid = {inv.idempotent_power(fl.e): None}  # e,e' already idempotent
        vale = {(inv.mult[s][fl.e], fl.e) in inv.accept for s in est}
        valep = {(inv.mult[s][fl.ep], fl.ep) in inv.accept for s in est}
        print(f"  --- e={fl.e} e'={fl.ep}  s=e·e'·e={fl.s}  sp=e'·e·e'={fl.sp}")
        print(f"      sink s: ==e'? {fl.s==fl.ep}  ==e? {fl.s==fl.e}  "
              f"J-equiv e'? {j_equiv(fl.s, fl.ep, ideals)}  "
              f"J-min? {j_minimal(fl.s, ideals)}  |ideal(s)|={len(ideals[fl.s])}")
        print(f"      |ideal(e)|={len(ideals[fl.e])} |ideal(e')|={len(ideals[fl.ep])}"
              f"   verdicts over EntrySt: Val(·,e)={vale} Val(·,e')={valep}"
              f"  {'SPLIT' if (vale|valep)=={True,False} else 'uniform'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
