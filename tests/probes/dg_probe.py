"""Synthesize the Diekert-Gastin formula of ONE HOA file and verify it —
the end-to-end client of `aut2ltl/bls/definability/dg/synth.py`: oracle
pipeline, canonical algebra, the induction, the phantom unwinding; then the
formula is translated by Spot and checked language-equivalent to the input's
deterministic form (both containment directions, with a witness word on a
mismatch).

Usage:  python3 tests/probes/dg_probe.py <file.hoa>

Exit 0: verified equivalent. Exit 2: not a dg input (group-bearing, cap) or
a decline. Exit 3: built but not verified (the flat tree is beyond Spot's
budget — a downstream limit, not a construction failure). Exit 1: VERIFY
FAILED — a construction bug, never to be shipped.
"""
from __future__ import annotations

import sys
import time

import spot

from aut2ltl.bls.definability.dg.synth import DgDecline, synthesize
from dg_common import ast_to_spot, print_d_line, quotient_of_hoa


def main(path: str) -> int:
    data = quotient_of_hoa(path)
    if data is None:
        print("closure  : blew the cap")
        return 2
    print_d_line(data)
    if data.group is not None:
        print("verdict  : NOT aperiodic -- not a dg input")
        return 2

    t0 = time.time()
    try:
        ast, root, n_nodes = synthesize(data.alg, max_nodes=MAX_NODES)
    except DgDecline as e:
        print(f"decline  : {e}  ({time.time() - t0:.3f}s)")
        return 2
    tree: int = ast.tree_size(root)
    print(f"synth    : {n_nodes} nodes, arena {len(ast)}, "
          f"tree {tree}, {time.time() - t0:.3f}s")

    # Spot's translator works on the flat semantics and is not interruptible
    # in-process: past this crude gate the formula is BUILT and the probe
    # skips verification -- a Spot-side limit, not a construction failure
    # (the survey wiring, with its bounded spotrun calls, is the real path).
    if tree > 3_000_000:
        print(f"VERIFY   : skipped (flat tree {tree} beyond Spot's budget; "
              "the DAG is built)")
        return 3
    f = ast_to_spot(ast, root, data.alg.letters)
    if tree <= 400:
        print(f"formula  : {f}")
    if tree <= 100000:
        s = str(spot.simplify(f))
        print(f"simplified: {s}" if len(s) <= 200
              else f"simplified: ({len(s)} chars, suppressed)")
    faut = spot.translate(f)
    inc_lr = spot.contains(data.aut, faut)   # L(formula) ⊆ L(input)
    inc_rl = spot.contains(faut, data.aut)   # L(input) ⊆ L(formula)
    if inc_lr and inc_rl:
        print("VERIFY   : equivalent")
        return 0
    print(f"VERIFY   : FAILED  formula⊆input={inc_lr}  input⊆formula={inc_rl}")
    for big, small, tag in ((data.aut, faut, "formula ∖ input"),
                            (faut, data.aut, "input ∖ formula")):
        w = spot.complement(big).intersecting_word(small)
        if w is not None:
            print(f"  witness ({tag}): {w}")
    return 1


MAX_NODES: int = 2000

if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        sys.exit(1)
    if len(sys.argv) == 3:
        MAX_NODES = int(sys.argv[2])
    sys.exit(main(sys.argv[1]))
