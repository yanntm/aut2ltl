"""FIG-1 — the layered Cayley graph of `GF(aa)` (paper §5.2).

    python3 -m tests.sos2ltl.figs.fig1 <file.sos> [out.tex]

Prints the Cayley edge list, the layers and the R-order, and the per-layer
(A)/(B) read-offs; with an output path, writes the TikZ source of the layered
drawing. The structure is read off `cayley`/`anchoring`/`windows`; only the
node coordinates below are the figure's own.

The layout is the six-class algebra's: the transient root on top, the two
mirrored moving layers side by side, the frozen absorbing class at the
bottom — the diamond of the paper's ASCII.
"""
from __future__ import annotations

import sys
from typing import List

from aut2ltl.sos2ltl.cayley import build
from tests.sos2ltl.figs import machine
from tests.sos2ltl.figs.machine import Layout
from sosl.sos import load_invariant

GF_AA = Layout(
    pos={0: (0.0, 0.0),
         1: (-5.0, -3.8), 3: (-2.2, -3.8),
         2: (2.2, -3.8), 4: (5.0, -3.8),
         5: (0.0, -7.6)},
    tag_at={0: "east", 1: "west", 2: "east", 3: "east"},
    tag_shift={0: 6.0, 1: 14.0, 2: 14.0, 3: 8.0},
    bend={(1, 3): 24, (3, 1): 24, (2, 4): -24, (4, 2): -24},
    loop_at={1: "left", 4: "right", 5: "below"},
    entry_at={1: 225, 2: 315},
    scale=1.0,
)


def main(argv: List[str]) -> int:
    path = argv[0]
    with open(path) as f:
        inv = load_invariant(f.read())
    cay = build(inv)

    print(f"{path}: {inv.n} classes, {len(cay.layers)} layers")
    for c in range(inv.n):
        steps = "  ".join(
            f"{machine.letter_txt(inv, a)} -> {cay.step(c, a)}"
            for a in range(inv.alphabet.size))
        print(f"  class {c} [{machine.class_tex(inv, c)}]: {steps}")
    for i, layer in enumerate(cay.layers):
        succ = ", ".join(str(j) for j in cay.successors[i]) or "-"
        print(f"  layer {i} {{{' '.join(map(str, layer))}}} -> {succ}")

    if len(argv) > 1:
        with open(argv[1], "w") as out:
            out.write(machine.render(inv, cay, GF_AA))
        print(f"  wrote {argv[1]}")
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
