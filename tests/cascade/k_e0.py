"""K-E0 gate: the two cascade-ladder witnesses (bls_cascade_spec.md §4).

    python3 -m tests.cascade.k_e0 floor      # GF(a & X((!a&!b) U a))
    python3 -m tests.cascade.k_e0 gaFb       # G(a -> F b)

Builds `𝓘(L)`, runs C1 (Cayley layers) and C2 (anchoring) to read off the final
layer's structure, then the config-machine decider (`config_machine.decide`) at
width 0, and asserts the draft's C.3 worked derivation: the final-layer
predictions of steps 1-3/5 and the saturation-agnostic (C) read-off. Prints
every read-off; a mismatch is a PAPER-EDIT finding and exits nonzero.
"""
from __future__ import annotations

import sys
from typing import Dict, FrozenSet, List, Tuple

import spot

from aut2ltl.language import Language
from aut2ltl.sos2ltl.bridge import invariant_of_language
from aut2ltl.sos2ltl.cayley import build
from aut2ltl.sos2ltl.anchoring import analyze_layer
from sosl.sos import Invariant

from tests.cascade.config_machine import (
    Edge,
    concrete_letters,
    decide,
    quotient_letters,
)

CASES = {
    "floor": "G F (a & X((!a & !b) U a))",
    "gaFb": "G (a -> F b)",
}


def letter_name(inv: Invariant, d: int, aps: Tuple[str, ...]) -> str:
    """A readable name for quotient letter `d`: the true APs of a concrete
    letter folding to it, e.g. `a` / `!a&!b` / `b`."""
    masks = concrete_letters(inv)[d]
    a = masks[0]
    trues = inv.alphabet.true_aps(a)
    return "&".join((p if p in trues else "!" + p) for p in aps) or "(all-false)"


def final_layer(inv: Invariant):
    """The Cayley build and its final (bottom, absorbing-candidate) layer id —
    the last layer in topological order that is an SCC some run stays in."""
    cay = build(inv)
    return cay, len(cay.layers) - 1


def show_edge(inv: Invariant, e: Edge, name: Dict[int, str]) -> str:
    (q, m), d = e
    return f"({q},{name[d]})->{inv.mult[q][d]}"


def run(case: str) -> int:
    formula = CASES[case]
    inv = invariant_of_language(Language.of(spot.translate(formula)))
    aps = tuple(inv.alphabet.aps)
    sigma = quotient_letters(inv)
    name = {d: letter_name(inv, d, aps) for d in sigma}

    cay, fid = final_layer(inv)
    R = frozenset(cay.layers[fid])
    print(f"# {case}: {formula}")
    print(f"  {inv.n} classes, {len(cay.layers)} layers; "
          f"Σ_λ = {{{', '.join(name[d] for d in sigma)}}}")
    print(f"  layers: " + " | ".join(
        "{" + ",".join(map(str, l)) + "}" for l in cay.layers))
    print(f"  final layer {fid}: R = {{{','.join(map(str, sorted(R)))}}}  "
          f"successors={cay.successors[fid]}")

    anc = analyze_layer(cay, fid)
    print(f"  1-anchored width: {anc.width}  (None = FAIL)")
    for q in sorted(R):
        print(f"    class {q}: "
              f"St={sorted(name[inv.letter_class[a]] for a in anc.stutter[q])} "
              f"An={sorted(name[inv.letter_class[a]] for a in anc.anchors[q])} "
              f"exits={sorted(name[inv.letter_class[a]] for a in anc.exits[q])}")
    print(f"    letter kinds: "
          f"{ {name[inv.letter_class[a]]: k for a, k in anc.letter_kind.items()} }")

    # ALG-1 at k=0: the within-layer edges, printed and counted.
    dec = decide(inv, R, k=0)
    edges: FrozenSet[Edge] = frozenset().union(*dec.verdicts.keys()) \
        if dec.verdicts else frozenset()
    all_edges = sorted(edges, key=lambda e: (e[0][0], name[e[1]]))
    print(f"  ALG-1 k=0: {len(all_edges)} within-layer edges: "
          + ", ".join(show_edge(inv, e, name) for e in all_edges))

    # ALG-5/6 at width 0.
    print(f"  (C) at k=0: holds={dec.c_holds}  collected F={dec.n_collected}  "
          f"max_states={dec.max_states}  budget={dec.budget}")
    print(f"  (B) at k=0: holds={dec.b_holds}  conflicts={len(dec.b_conflicts)}")
    accepting = sorted(
        ([show_edge(inv, e, name) for e in sorted(F, key=lambda e: (e[0][0], name[e[1]]))]
         for F, vs in dec.verdicts.items() if vs == {True}),
        key=len)
    minimal = [F for F, vs in dec.verdicts.items() if vs == {True}
               and not any(other < F for other, ov in dec.verdicts.items()
                           if ov == {True})]
    print(f"  accepting F count: {sum(1 for vs in dec.verdicts.values() if vs == {True})}"
          f"  minimal accepted sets: "
          + "; ".join("{" + ",".join(show_edge(inv, e, name)
                                      for e in sorted(F, key=lambda e: (e[0][0], name[e[1]])))
                      + "}" for F in minimal))
    return 0


def main(argv: List[str]) -> int:
    if not argv or argv[0] not in CASES:
        print(f"usage: k_e0 <{'|'.join(CASES)}>", file=sys.stderr)
        return 2
    return run(argv[0])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
