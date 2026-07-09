"""FIG-4 — the `F a` micro-machine (paper §5.2, example 1).

    python3 -m tests.sos2ltl.figs.fig4 <file.sos> [out.tex]

The pure peel: three singleton layers in a chain, so condition (A) is
vacuous. The committed sink (`T_c = Σ^ω`, the co-safety base case) is drawn
double-circled; the middle layer is all-rejecting as a final layer, which is
what kills its `STAY^∞`. Same conventions as FIG-1.

Committedness is the engine's own read-off, not a second implementation.
"""
from __future__ import annotations

import sys
from typing import List

from aut2ltl.sos2ltl.cayley import build
from aut2ltl.sos2ltl.engine import _committed
from tests.sos2ltl.figs import machine
from tests.sos2ltl.figs.machine import Layout
from sosl.sos import load_invariant

F_A = Layout(
    pos={0: (0.0, 0.0), 1: (0.0, -3.2), 2: (0.0, -6.4)},
    tag_at={0: "east", 1: "east", 2: "east"},
    tag_shift={0: 6.0, 1: 26.0, 2: 6.0},
    bend={(0, 2): 62},
    loop_at={1: "left", 2: "below"},
    scale=1.0,
)


def main(argv: List[str]) -> int:
    path = argv[0]
    with open(path) as f:
        inv = load_invariant(f.read())
    cay = build(inv)
    committed = [c for c in range(inv.n) if _committed(cay, c)]

    print(f"{path}: {inv.n} classes, {len(cay.layers)} layers")
    print(f"  accepting linked pairs: {sorted(inv.accept)}")
    print(f"  committed classes (T_c = Sigma^w): {committed}")
    for i, layer in enumerate(cay.layers):
        succ = ", ".join(str(j) for j in cay.successors[i]) or "-"
        print(f"  layer {i} {{{' '.join(map(str, layer))}}} -> {succ}")

    if len(argv) > 1:
        with open(argv[1], "w") as out:
            out.write(machine.render(inv, cay, F_A, committed=committed))
        print(f"  wrote {argv[1]}")
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
