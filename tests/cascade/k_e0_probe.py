"""K-E0 investigation: full layer dump + width sweep for one witness.

    python3 -m tests.cascade.k_e0_probe floor|gaFb

Dumps every layer's C2 anchoring, prefix-independence, the acceptance at the
final class(es), and sweeps (C)/(B) at widths 0..3 on the final layer. Grounds
the PAPER-EDIT attribution against the draft's C.3 derivation.
"""
from __future__ import annotations

import sys
from typing import Dict, List, Tuple

import spot

from aut2ltl.language import Language
from aut2ltl.sos2ltl.bridge import invariant_of_language
from aut2ltl.sos2ltl.cayley import build
from aut2ltl.sos2ltl.anchoring import analyze_layer
from aut2ltl.sos2ltl.readoffs import is_prefix_independent
from sosl.sos import Invariant

from tests.cascade.config_machine import concrete_letters, decide, quotient_letters
from tests.cascade.k_e0 import CASES, letter_name


def main(argv: List[str]) -> int:
    case = argv[0]
    inv = invariant_of_language(Language.of(spot.translate(CASES[case])))
    aps = tuple(inv.alphabet.aps)
    sigma = quotient_letters(inv)
    name = {d: letter_name(inv, d, aps) for d in sigma}
    cay = build(inv)

    print(f"# {case}: {CASES[case]}")
    print(f"  {inv.n} classes; Σ_λ={{{', '.join(name[d] for d in sigma)}}}; "
          f"prefix-independent={is_prefix_independent(inv)}")
    print(f"  identity class={inv.identity}; accept P={sorted(inv.accept)}")
    print(f"  layers: " + " | ".join(
        f"{i}:{{{','.join(map(str,l))}}}->{cay.successors[i]}"
        for i, l in enumerate(cay.layers)))

    for i, layer in enumerate(cay.layers):
        anc = analyze_layer(cay, i)
        frozen = all(k == "neutral" for k in anc.letter_kind.values())
        print(f"  layer {i} {{{','.join(map(str,layer))}}} "
              f"width={anc.width} frozen={frozen} "
              f"kinds={ {name[inv.letter_class[a]]: k for a,k in anc.letter_kind.items()} }")
        for q in sorted(layer):
            print(f"      {q}: St={sorted(name[inv.letter_class[a]] for a in anc.stutter[q])}"
                  f" An={sorted(name[inv.letter_class[a]] for a in anc.anchors[q])}"
                  f" move={sorted(name[inv.letter_class[a]] for a in anc.move[q])}"
                  f" exits={sorted(name[inv.letter_class[a]] for a in anc.exits[q])}")

    fid = len(cay.layers) - 1
    R = frozenset(cay.layers[fid])
    print(f"  --- width sweep on final layer {fid} R={{{','.join(map(str,sorted(R)))}}} "
          f"(budget=40000/base, assert_sc off) ---")
    for k in range(3):
        dec = decide(inv, R, k=k, budget=40000, assert_sc=False)
        print(f"    k={k}: (C) holds={dec.c_holds} conflicts={len(dec.c_conflicts)}"
              f" | (B) holds={dec.b_holds} conflicts={len(dec.b_conflicts)}"
              f" | collectedF={dec.n_collected} maxstates={dec.max_states} budget={dec.budget}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
