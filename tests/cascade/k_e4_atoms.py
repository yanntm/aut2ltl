"""K-E4 (atoms): verify the config atoms on G(a→F b) against the C.3 prediction.

    python3 -m tests.cascade.k_e4_atoms

Builds A_{(2,a)} and A_{(4,b)} on the final layer of 𝓘(G(a→F b)) and checks
they are Spot-equivalent to the draft's `b∧X((b∨s)U a)` and `a∧X((a∨s)U b)`
(bounded Spot equivalence — the atoms are tiny; no stringification of assembled
output).
"""
from __future__ import annotations

import sys

import spot

from aut2ltl.language import Language
from aut2ltl.sos2ltl.bridge import invariant_of_language
from aut2ltl.sos2ltl.cayley import build
from aut2ltl.sos2ltl.anchoring import analyze_layer

from tests.cascade.config_machine import quotient_letters
from tests.cascade.emit import atom


def main() -> int:
    inv = invariant_of_language(Language.of(spot.translate("G (a -> F b)")))
    cay = build(inv)
    fid = len(cay.layers) - 1
    anc = analyze_layer(cay, fid)
    sigma = quotient_letters(inv)
    # quotient letters: find the class ids for a (a&!b), b (!a&b), s (!a&!b)
    def qid(cube_pos):
        for d in sigma:
            a0 = next(a for a in inv.alphabet.letters() if inv.letter_class[a] == d)
            if set(inv.alphabet.true_aps(a0)) == cube_pos:
                return d
        raise KeyError(cube_pos)
    qa, qb = qid({"a"}), qid({"b"})

    # edges (2,a) and (4,b) at k=0
    e_2a = ((2, ()), qa)
    e_4b = ((4, ()), qb)
    A_2a = atom(inv, anc, e_2a, 0)
    A_4b = atom(inv, anc, e_4b, 0)

    # Real quotient letters: a-class = a&!b (a&b folds into the b-class, since
    # a&b discharges the obligation like b); b-class = b; s-class = !a&!b. So the
    # draft's b∨s = b|!a, a∨s = !b, target a = a&!b, target b = b.
    exp_2a = spot.formula("b & X((b | !a) U (a & !b))")
    exp_4b = spot.formula("(a & !b) & X((!b) U b)")
    ok1 = spot.are_equivalent(A_2a, exp_2a)
    ok2 = spot.are_equivalent(A_4b, exp_4b)
    print(f"  A_(2,a) equiv b∧X((b∨s)U a) [concrete cubes]: {ok1}")
    print(f"  A_(4,b) equiv a∧X((a∨s)U b) [concrete cubes]: {ok2}")
    print("OK" if ok1 and ok2 else "FAIL")
    return 0 if ok1 and ok2 else 1


if __name__ == "__main__":
    sys.exit(main())
