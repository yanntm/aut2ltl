"""K-E4 conformance: emit Ω for G(a→F b)'s final layer, gate against L.

    python3 -m tests.cascade.k_e4_gaFb

Assembles the config normal form Ω(R*, ·) for `𝓘(G(a→F b))` (DAG-only), checks
it is Spot-equivalent to `G(a→F b)` (the layer is terminal and the language
carries no safety, so L = the tail recurrence), and reports DAG size / modal
depth. No stringification of Ω.
"""
from __future__ import annotations

import sys

import spot

from aut2ltl.language import Language
from aut2ltl.sos2ltl.bridge import invariant_of_language
from aut2ltl.sos2ltl.cayley import build
from aut2ltl.sos2ltl.anchoring import analyze_layer

from aut2ltl.ltl.builders import _simp_f
from aut2ltl.ltl.metrics import dag_node_count, tree_node_count

from tests.cascade.config_machine import decide
from tests.cascade.emit import omega, source_classes


def main() -> int:
    inv = invariant_of_language(Language.of(spot.translate("G (a -> F b)")))
    cay = build(inv)
    fid = len(cay.layers) - 1
    R = frozenset(cay.layers[fid])
    anc = analyze_layer(cay, fid)

    dec = decide(inv, R, 0, assert_sc=False)
    assert dec.c_holds, "final layer not (C)-decided at k=0"
    multi = [F for F in dec.verdicts
             if len(source_classes(F)) >= 2 and dec.verdicts[F] == {True}]
    minimal = [F for F in multi
               if not any(o < F for o in multi)]
    Om, mixed = omega(inv, anc, R, 0, multi, minimal)

    Om_s = _simp_f(Om)
    eq = spot.are_equivalent(Om, spot.formula("G (a -> F b)"))
    print(f"  minimal accepted ≥2-class F: {len(minimal)}  parks-mixed: {mixed}")
    print(f"  Ω size: dag={dag_node_count(Om)} flat={tree_node_count(Om, limit=10**6)}"
          f"  | simplified: dag={dag_node_count(Om_s)} "
          f"flat={tree_node_count(Om_s, limit=10**6)}")
    print(f"  Ω ≡ G(a→F b): {eq}   (simplified ≡: "
          f"{spot.are_equivalent(Om_s, spot.formula('G (a -> F b)'))})")
    print("OK" if eq and not mixed else "FAIL")
    return 0 if eq and not mixed else 1


if __name__ == "__main__":
    sys.exit(main())
