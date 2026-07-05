"""Render ONE automaton to an image the way Spot draws it in Jupyter.

Input is an HOA file or an LTL/PSL formula; the drawing is Spot's own styled
SVG (`spot.twa._repr_svg_`, the exact picture a notebook shows). `spot.setup()`
is called first so the picture carries the fancy display defaults — rounded
pale-yellow states in the Lato font, UTF-8 colour bullets for the acceptance
sets, vee arrowheads — the same styling the notebook and the online Spot app
use, driven by the `SPOT_DOTDEFAULT` / `SPOT_DOTEXTRA` environment variables
`setup()` exports. The output format follows the OUT extension: `.svg` writes
that SVG verbatim; `.png` rasterizes it with `rsvg-convert` (librsvg — the
layout stays Spot's, only the pixels are ours) to a fixed display WIDTH in
pixels, height scaled to keep the aspect ratio (never stretched). The default
width is a reasonable on-screen automaton size, well under a page; pass a
smaller/larger width to taste.

Usage (module run from repo root):
  python3 -m tests.sosg.render_svg <file.hoa | 'LTL/PSL formula'> OUT[.svg|.png] [width_px]
"""
from __future__ import annotations

import os
import subprocess
import sys

import spot

# Spot's fancy display defaults (colour bullets, filled states, Lato font),
# exported as SPOT_DOTDEFAULT/SPOT_DOTEXTRA and read by print_dot at render
# time. Must run before any automaton is drawn.
spot.setup()


def load(arg: str) -> "spot.twa_graph":
    """The automaton for `arg`: the file if it exists, else the deterministic
    translation of the formula it denotes."""
    if os.path.isfile(arg):
        return spot.automaton(arg)
    return spot.translate(spot.formula(arg),
                         "deterministic", "generic", "complete")


def main(argv: list) -> int:
    if len(argv) not in (3, 4):
        print(__doc__)
        return 1
    out = argv[2]
    width = argv[3] if len(argv) == 4 else "360"
    svg = load(argv[1])._repr_svg_()
    if out.lower().endswith(".png"):
        # -w alone fixes the width and scales height to keep the aspect ratio.
        subprocess.run(["rsvg-convert", "-w", width, "-f", "png", "-o", out],
                       input=svg.encode(), check=True)
        print(f"wrote {out}  (png, width {width}px)")
    else:
        with open(out, "w") as fh:
            fh.write(svg)
        print(f"wrote {out}  ({len(svg)} bytes svg)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
