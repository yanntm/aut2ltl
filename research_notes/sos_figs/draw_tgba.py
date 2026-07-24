#!/usr/bin/env python3
"""Draw one deterministic automaton, relabelled to the paper's two-letter
alphabet — the common renderer for every drawing in `img/`.

The construction's alphabet is `Σ = 2^{a}`, a single atomic proposition, so
Spot draws its two letters as the boolean labels `a` (the letter `{a}`) and
`!a` (the letter `{}`), and a both-letters edge as the constant `1` (true).
The paper writes that same two-letter alphabet as `{a, b}` — plain letters, no
boolean formulae. This script post-processes Spot's own styled drawing to that
convention:

    !a  ->  b            the `{}` letter is the paper's `b`
    1   ->  a,b          a both-letters (true) edge, comma-fused

`a` is left as is. The rewrite is deliberately narrow, not a generic
formula-to-letter simplifier: it only fires on Spot's `dot` *edge* lines (those
carrying `->`), so a state named `1` is never touched, only the true-label `1`
on an edge is. The picture is otherwise byte-for-byte Spot's `_repr_svg_`
layout — same styled `dot`, same `dot -Tsvg`, same `rsvg-convert` to a
fixed-width PNG — so these figures sit next to `render_svg.py`'s output
unchanged in everything but the letters.

Usage (run from the repository root or anywhere):
  python3 research_notes/sos_figs/draw_tgba.py [--verbatim] <file.hoa> OUT.png [width_px]

`--verbatim` draws an HOA exactly as written (hand-owned mark placement, e.g.
`aUGb`), skipping the sos import layer's re-canonicalization — same meaning as
in `render_svg.py`.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

# Reach the in-tree sosl package (import layer) and Spot regardless of cwd.
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "sosl"))

import spot  # noqa: E402

# Spot's fancy display defaults (colour bullets, filled states, Lato font):
# the same styling render_svg.py draws with. Must run before any drawing.
spot.setup()


def load(arg: str, verbatim: bool = False) -> "spot.twa_graph":
    """The automaton for `arg` — the file's canonical D through the sos import
    layer, or read verbatim, or the D of a formula. Mirrors render_svg.load."""
    from sosl.sos.build import import_hoa, import_ltl
    if os.path.isfile(arg):
        return spot.automaton(arg) if verbatim else import_hoa(arg)
    return import_ltl(arg)


def relabel(dot: str) -> str:
    """Rewrite Spot `dot` edge labels to the paper's `{a, b}` alphabet.

    Only lines carrying `->` (edges) are rewritten, so node labels — a state
    named `1` in particular — are left intact. On an edge line: `!a` becomes
    `b` (also inside a marked label like `!a<br/>⓿`), and a label whose formula
    is the constant `1` (true) becomes `a,b`. The true-label always sits right
    after `label=<`, so anchoring there distinguishes it from any incidental
    digit."""
    out = []
    for line in dot.splitlines():
        if "->" in line:
            line = line.replace("!a", "b")
            line = re.sub(r"label=<1(?=>|<br/>)", "label=<a,b", line)
        out.append(line)
    return "\n".join(out) + "\n"


def main(argv: list) -> int:
    verbatim = "--verbatim" in argv[1:]
    argv = [a for a in argv if a != "--verbatim"]
    if len(argv) not in (3, 4):
        print(__doc__)
        return 1
    src, out = argv[1], argv[2]
    width = argv[3] if len(argv) == 4 else "360"

    dot = relabel(load(src, verbatim).to_str("dot"))
    svg = subprocess.run(["dot", "-Tsvg"], input=dot.encode(),
                         capture_output=True, check=True).stdout
    subprocess.run(["rsvg-convert", "-w", width, "-f", "png", "-o", out],
                   input=svg, check=True)
    print(f"wrote {out}  (png, width {width}px)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
