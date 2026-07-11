"""E11 loop half, worked instance: the floor witness's pendency machine.

    python3 -m tests.sos2ltl.e11_pendency

The residual witness `GF(a ∧ X(s U a))`, `s = !a∧!b` (paper §5.1/§6): its
loop content sits on a frozen singleton terminal layer where (C) fails at
every width. The delegate restricts the deterministic acceptor to the
layer's tails (the two-state pendency machine — "last non-`s` letter was
an `a`", Büchi on the completion transition), KR-decomposes it, and reads
the label off `Fin(C)`. Expected: an emission equivalent to the language
itself (the layer is terminal and prefix-independent, so `T_z = L`),
checked with `spot.are_equivalent` — the bounded oracle, per the K-E4
gate pattern. DAG-only; sizes reported, never the formula string.
"""
from __future__ import annotations

import sys

import spot

from aut2ltl.language import Language
from aut2ltl.ltl.builders import _simp_f
from aut2ltl.ltl.metrics import dag_node_count, tree_node_count
from aut2ltl.ltl.printers import format_gated
from aut2ltl.sos2ltl.bridge import invariant_of_language
from aut2ltl.sos2ltl.cascade import loop_acceptance
from aut2ltl.sos2ltl.cayley import build

PHI = "G F (a & X ((!a & !b) U a))"


def main() -> int:
    lang = Language.of(spot.translate(PHI))
    inv = invariant_of_language(lang)
    cay = build(inv)
    fid = len(cay.layers) - 1
    print(f"  classes={inv.n} layers={len(cay.layers)} "
          f"final layer {fid} = {cay.layers[fid]}")

    em = loop_acceptance(cay, fid, lang.det_parity_sbacc(), timeout=10)
    print(f"  seam: {em.record.line()}  member={em.technique}", flush=True)

    f = em.formula
    print(f"  label size: dag={dag_node_count(f)} "
          f"flat={tree_node_count(f, limit=10**6)}", flush=True)
    f_s = _simp_f(f)
    print(f"  simplified: dag={dag_node_count(f_s)} "
          f"flat={tree_node_count(f_s, limit=10**6)}", flush=True)
    print(f"  label: {format_gated(f_s, limit=200)}", flush=True)
    eq = spot.are_equivalent(f_s, spot.formula(PHI))
    print(f"  label ≡ {PHI}: {eq}")
    print("OK" if eq else "FAIL")
    return 0 if eq else 1


if __name__ == "__main__":
    sys.exit(main())
