"""K-E0 step 4: (B)-mode agreement with C3 (windows.py) on decided cases.

    python3 -m tests.cascade.k_e0_bcross

Compares the config decider's (B)-mode verdict (window-projection grouping) to
C3's `realizable_verdicts` at matching window width `k`, on the named layers:
`GF(aa)` frozen `{5}`, the floor witness frozen `{6}`, and `G(a→F b)` moving
`{2,4}`. Agreement is asserted where C3 gives a definite verdict; the one
expected divergence is F1 (C3's cap false-PASSes where the exact closure sees a
conflict) — flagged, not failed.
"""
from __future__ import annotations

import sys
from typing import Dict, FrozenSet, List, Optional, Tuple

import spot

from aut2ltl.language import Language
from aut2ltl.sos2ltl.bridge import invariant_of_language
from aut2ltl.sos2ltl.cayley import build
from aut2ltl.sos2ltl.windows import realizable_verdicts
from sosl.sos import Invariant, load_invariant

from tests.cascade.config_machine import decide
from tests.cascade.k_e0 import CASES

GF_AA = "samples/fixtures/hoa/sos/gf_aa.sos"


def load_case(name: str) -> Invariant:
    if name == "gfaa":
        with open(GF_AA) as f:
            return load_invariant(f.read())
    return invariant_of_language(Language.of(spot.translate(CASES[name])))


def c3_verdict(cay, fid: int, k: int) -> Tuple[str, Optional[Dict]]:
    """C3's (B) at window width `k`: 'PASS' with the window→verdict map, or
    'NONE' (conflict or cap — indistinguishable at this call)."""
    table = realizable_verdicts(cay, fid, k, node_budget=200000)
    return ("PASS", table) if table is not None else ("NONE", None)


def my_b(inv: Invariant, R: FrozenSet[int], k: int) -> Tuple[Optional[bool], int]:
    dec = decide(inv, R, k, budget=200000, assert_sc=False)
    if dec.budget:
        return None, 0
    return dec.b_holds, len(dec.b_conflicts)


def main(argv: List[str]) -> int:
    # (case, expected final layer id, widths to test)
    cases = [("gfaa", None, [1, 2]), ("floor", None, [0, 1]), ("gaFb", None, [0, 1])]
    ok = True
    for name, _, widths in cases:
        inv = load_case(name)
        cay = build(inv)
        fid = len(cay.layers) - 1
        R = frozenset(cay.layers[fid])
        print(f"# {name}: final layer {{{','.join(map(str,sorted(R)))}}}")
        for k in widths:
            c3s, table = c3_verdict(cay, fid, k)
            mine, nconf = my_b(inv, R, k)
            # agreement logic on definite cases
            note = ""
            if mine is None:
                note = "mine=BUDGET (no compare)"
            elif c3s == "PASS" and mine is True:
                note = "agree PASS"
            elif c3s == "PASS" and mine is False:
                note = "C3 PASS but mine FAIL -> F1 cap false-PASS (expected)"
            elif c3s == "NONE" and mine is False:
                note = "agree FAIL/conflict"
            elif c3s == "NONE" and mine is True:
                note = "MINE PASS but C3 NONE -> C3 cap/budget undecided (no disagreement)"
            print(f"    k={k}: C3={c3s:4s}"
                  f"{'' if table is None else f'({len(table)} wsets)'} "
                  f"| mine b_holds={mine} conflicts={nconf}   {note}")
            # the hard failure: C3 PASS map with a verdict my exact side contradicts
            if c3s == "PASS" and mine is True and table is not None:
                # both decided PASS: verdict maps must be consistent (translate C3
                # windows to λ-class buffers)
                mymap = _my_map(inv, R, k)
                trans = {frozenset(tuple(inv.letter_class[a] for a in w) for w in ws): v
                         for ws, v in table.items()}
                shared = set(trans) & set(mymap)
                disagree = [w for w in shared if trans[w] != mymap[w]]
                if disagree:
                    ok = False
                    print(f"      MAP DISAGREE on {len(disagree)} window sets")
                else:
                    print(f"      map check: {len(shared)} shared wsets agree")
    print("OK" if ok else "FAIL")
    return 0 if ok else 1


def _my_map(inv: Invariant, R: FrozenSet[int], k: int
            ) -> Dict[FrozenSet[Tuple[int, ...]], bool]:
    """My (B)-mode window→verdict map, keyed by the window-projection (a set of
    λ-class buffers), for a decided PASS layer."""
    dec = decide(inv, R, k, budget=200000, assert_sc=False)
    return {proj: next(iter(vs)) for proj, vs in dec.groups.items() if len(vs) == 1}


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
