"""``sos2cayley`` — one `.sos` invariant to one paper-ready Cayley figure.

    python3 -m tests.sos.sos2cayley <in.sos> --name <basename>
        --out-dir <dir>          # the .tex / _gen.tex / _gen.dot / .pdf land here
        [--img-dir <dir>]        # the .png lands here (default: --out-dir)
        [--rename 'a=a,!a=b']    # display letters, in display order
        [--layout dot|layered]   # node placement (default: dot)
        [--rankdir LR|TB]        # which way the BFS layers run (default: LR)
        [--keep-identity]        # draw [eps] too (default: elided)
        [--no-pairs]             # ablate the P caption (draw the bare algebra)
        [--reseed]               # redraw the hand-owned tex from the machine, at
                                 # its own coordinates (propagate a restyle)

The drawing itself is `sosl.sos.viz`, the engine's generic `.sos` -> picture
service: the full multiplication table of the algebra, `[eps]` elided unless
`--keep-identity` is passed. This tool is the *paper* wrapper around it, and adds
the one thing a figure of record needs: **the two-file convention.**

``<name>_gen.tex`` and ``<name>_gen.dot`` are rewritten on every run — the machine
artefacts, a deterministic function of the input, never hand-touched. ``<name>.tex``
is seeded as a copy the first time and is **hand-owned** from then on: it is what
the paper's figure is compiled from, so a nudged coordinate survives a re-run.
Traceability is the point, not full machine generation — ``diff <name>_gen.tex
<name>.tex`` is exactly the hand-tuning, and the committed pdf/png are always
built from the committed hand-owned tex.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from typing import Dict, List, Tuple

from sosl.sos import load_invariant
from sosl.sos.viz import dot_of, figure_of, place, tikz_of
from sosl.sos.viz.layout import Placement
from sosl.sos.viz.dot import pairs_label
from sosl.sos.viz.model import Figure, Naming
from sosl.sos.viz.render import compile_pdf, pdf_to_png


NODE_AT = re.compile(r"\\node\[[^\]]*\]\s*\((\w+)\)\s*at\s*\(([-\d.]+),\s*([-\d.]+)\)")
LOOP_AT = re.compile(r"\\draw\[[^\]]*\]\s*\((\w+)\)\s*to\[(loop \w+)\]")


def harvest(tex_path: str, fig: Figure) -> Tuple[Placement, Dict[int, str]]:
    """The placement of an existing hand-owned `.tex`: one (x, y) per class and the
    direction of each self-loop, read off its ``\\node`` and ``\\draw`` lines.

    Placement is the *only* thing taken — coordinates and loop directions, nothing
    else — which is what lets a restyle rewrite the whole figure from the machine
    while keeping the arrangement a human chose. Raises if the file does not place
    every class (a node was renamed or dropped: re-seed from scratch rather than
    half-transplant)."""
    by_ident = {nd.ident: nd.cls for nd in fig.nodes}
    with open(tex_path) as fh:
        text = fh.read()
    pos = {by_ident[m.group(1)]: (float(m.group(2)), float(m.group(3)))
           for m in NODE_AT.finditer(text) if m.group(1) in by_ident}
    loops = {by_ident[m.group(1)]: m.group(2)
             for m in LOOP_AT.finditer(text) if m.group(1) in by_ident}
    missing = [nd.ident for nd in fig.nodes if nd.cls not in pos]
    if missing:
        raise RuntimeError(f"{tex_path} places no coordinate for {missing}")
    return pos, loops


def emit(fig: Figure, out_dir: str, img_dir: str, name: str, layout: str,
         provenance: str, pairs: bool = True, rankdir: str = "LR",
         reseed: bool = False) -> str:
    """Write the machine artefacts and the hand-owned tex under ``out_dir``,
    compile *the hand-owned one* to pdf, and rasterize it into ``img_dir``.
    Returns the hand-owned tex path.

    ``reseed`` regenerates the hand-owned tex from the machine *at its current
    coordinates* — the way to propagate a change of style or of drawn content into
    figures that have been placed by hand, without either losing the placement or
    hand-patching the graph."""
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)
    gen_dot = os.path.join(out_dir, f"{name}_gen.dot")
    gen_tex = os.path.join(out_dir, f"{name}_gen.tex")
    tex = os.path.join(out_dir, f"{name}.tex")

    with open(gen_dot, "w") as fh:
        fh.write(f"// {provenance}\n"
                 + dot_of(fig, name.replace("-", "_"), pairs, rankdir))
    with open(gen_tex, "w") as fh:
        fh.write(tikz_of(fig, place(fig, layout, rankdir), provenance, pairs))
    if reseed and os.path.exists(tex):
        pos, loops = harvest(tex, fig)    # read BEFORE the truncating open below
        with open(tex, "w") as fh:
            fh.write(tikz_of(fig, pos, provenance, pairs, loops))
        print(f"reseeded {tex} from the machine, at its own coordinates")
    elif os.path.exists(tex):
        print(f"kept hand-owned {tex} (machine form refreshed in {gen_tex})")
    else:
        shutil.copyfile(gen_tex, tex)
        print(f"seeded hand-owned {tex} from {gen_tex}")

    pdf = compile_pdf(tex)
    png = pdf_to_png(pdf)
    if os.path.abspath(img_dir) != os.path.abspath(out_dir):
        shutil.move(png, os.path.join(img_dir, os.path.basename(png)))
        png = os.path.join(img_dir, os.path.basename(png))
    print(f"wrote {gen_dot}, {gen_tex}, {pdf}, {png}")
    return tex


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="sos2cayley")
    ap.add_argument("sos")
    ap.add_argument("--name", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--img-dir")
    ap.add_argument("--rename")
    ap.add_argument("--layout", default="dot", choices=("dot", "layered"))
    ap.add_argument("--rankdir", default="LR", choices=("LR", "TB"))
    ap.add_argument("--keep-identity", action="store_true",
                    help="draw [eps] as a node and a column (default: elided — its "
                         "row and column are fixed by the identity axiom)")
    ap.add_argument("--no-pairs", action="store_true",
                    help="ablate the P caption; draw the bare algebra A")
    ap.add_argument("--reseed", action="store_true",
                    help="rewrite the hand-owned tex from the machine, keeping its "
                         "coordinates (propagates a restyle without losing placement)")
    args = ap.parse_args(argv[1:])

    with open(args.sos) as fh:
        inv = load_invariant(fh.read())
    naming = (Naming.renamed(inv.alphabet, args.rename) if args.rename
              else Naming.machine(inv.alphabet))
    # asserts freshness: no LETTER edge enters [eps] (the identity is adjoined)
    fig = figure_of(inv, naming, elide_identity=not args.keep_identity)

    rename = f" --rename {args.rename}" if args.rename else ""
    keep = " --keep-identity" if args.keep_identity else ""
    emit(fig, args.out_dir, args.img_dir or args.out_dir, args.name, args.layout,
         f"sos2cayley {os.path.basename(args.sos)}{rename}{keep}", not args.no_pairs,
         args.rankdir, args.reseed)
    print(pairs_label(fig))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
