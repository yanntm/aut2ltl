"""K-E0 sanity: confirm 𝓘(L) really is L, two independent ways.

    python3 -m tests.cascade.k_e0_verify floor|gaFb

(1) membership of hand-picked lassos against the invariant's `member`;
(2) DG round-trip: synthesize a formula from 𝓘 and Spot-check equivalence to the
input. Bounds the PAPER-EDIT claim — the divergence is the draft's, not a build
artifact.
"""
from __future__ import annotations

import sys
from typing import Dict, List, Tuple

import spot

from aut2ltl.language import Language
from aut2ltl.sos2ltl.bridge import invariant_of_language
from aut2ltl.sos2ltl.dg import synthesize
from sosl.sos import Invariant
from sosl.sos.lasso import Lasso

from tests.cascade.k_e0 import CASES

# hand-picked lassos per case: (name, stem-aps, loop-aps, expected membership).
# aps are cube strings over the alphabet; 's'=!a&!b, 'b'=!a&b, 'a'=a&!b.
LASSOS: Dict[str, List[Tuple[str, List[str], List[str], bool]]] = {
    "floor": [
        ("(a s)^w", [], ["a&!b", "!a&!b"], True),        # a,s,a,s,... good pairs
        ("(a b)^w", [], ["a&!b", "!a&b"], False),        # b breaks every pair
        ("s^w", [], ["!a&!b"], False),                   # never an a
        ("(a s s)^w", [], ["a&!b", "!a&!b", "!a&!b"], True),
        ("a (b)^w", ["a&!b"], ["!a&b"], False),          # only finitely many a
    ],
    "gaFb": [
        ("(a b)^w", [], ["a&!b", "!a&b"], True),         # every a eventually b
        ("(a)^w", [], ["a&!b"], False),                  # a with no following b
        ("(b)^w", [], ["!a&b"], True),                   # no a at all
    ],
}


def mask(inv: Invariant, cube: str) -> int:
    """The letter mask whose true-AP set matches the fully-specified cube
    `p&!q&...` (each AP appears once, positive or negated)."""
    toks = cube.split("&")
    pos = {t for t in toks if not t.startswith("!")}
    for a in inv.alphabet.letters():
        if set(inv.alphabet.true_aps(a)) == pos:
            return a
    raise KeyError(cube)


def main(argv: List[str]) -> int:
    case = argv[0]
    formula = CASES[case]
    inv = invariant_of_language(Language.of(spot.translate(formula)))

    print(f"# {case}: {formula}")
    ok = True
    for name, stem, loop, expect in LASSOS[case]:
        w = Lasso(tuple(mask(inv, c) for c in stem),
                  tuple(mask(inv, c) for c in loop))
        got = inv.member(w)
        flag = "ok" if got == expect else "MISMATCH"
        ok = ok and got == expect
        print(f"  {name:12s} expect={expect!s:5s} got={got!s:5s} {flag}")

    eq = None
    if len(argv) > 1 and argv[1] == "--dg":
        ast, phi, n = synthesize(inv)
        cubes = ["&".join(p if p in inv.alphabet.true_aps(a) else "!" + p
                          for p in inv.alphabet.aps)
                 for a in inv.alphabet.letters()]
        emitted = ast.to_spot(phi, cubes)
        eq = spot.are_equivalent(spot.formula(emitted), spot.formula(formula))
        print(f"  DG round-trip: {n} nodes; equivalent to input = {eq}")
    print("OK" if ok and eq is not False else "FAIL")
    return 0 if ok and eq is not False else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
