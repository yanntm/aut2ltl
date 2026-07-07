"""DG synthesis probe on one `.sos` invariant (E0 sanity / E4b baseline).

    python3 -m tests.sos2ltl.e0_dg <file.sos> [--expect <ltl-formula>]

On an aperiodic invariant: synthesize (dg local-divisor induction), print
the formula with its DAG/tree sizes and recursion node count, and — when
``--expect`` is given — check Spot-equivalence against the expected
formula (bounded formula-level check). On a group-bearing invariant the
probe asserts the synthesis is refused upstream (no group ever reaches
`synthesize`).
"""
from __future__ import annotations

import sys
from typing import List

from aut2ltl.sos2ltl.dg import synthesize
from sosl.sos import load_invariant
from sosl.sos.classify.aperiodic import first_group


def main(argv: List[str]) -> int:
    path = argv[0]
    expect = argv[2] if len(argv) > 2 and argv[1] == "--expect" else None
    with open(path) as f:
        inv = load_invariant(f.read())

    if first_group(inv) is not None:
        print(f"{path}: group-bearing — dg refused (certificate side owns it)")
        assert expect is None, "cannot expect a formula on a group"
        print("OK")
        return 0

    ast, phi, n_nodes = synthesize(inv)
    ab = inv.alphabet
    cubes = ["&".join(p if p in ab.true_aps(a) else "!" + p for p in ab.aps)
             for a in ab.letters()]
    rendered = ast.to_spot(phi, cubes)
    print(f"{path}: {n_nodes} nodes, arena {len(ast)}, "
          f"tree {ast.tree_size(phi)}")
    print(f"  formula: {rendered if len(rendered) < 400 else rendered[:400] + '...'}")

    if expect is not None:
        import spot
        eq = spot.are_equivalent(spot.formula(rendered), spot.formula(expect))
        print(f"  equivalent to {expect}: {eq}")
        assert eq, "synthesized formula is not equivalent to the expectation"
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
