"""``sos2cayley`` — one `.sos` invariant to one paper-ready Cayley figure.

    python3 -m tests.sos.sos2cayley <in.sos> --name <basename> --out-dir <dir>
        [--rename 'a=a,!a=b']    # display letters, in display order
        [--layout dot|layered]   # node placement (default: dot)
        [--no-pairs]             # ablate the P caption (draw the bare algebra)

The drawing itself is `sosl.sos.viz`, the engine's generic `.sos` -> picture
service. This tool is the *paper* wrapper around it, and adds the one thing a
figure of record needs: **the two-file convention.**

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
import shutil
import sys
from typing import List

from sosl.sos import load_invariant
from sosl.sos.viz import dot_of, figure_of, place, tikz_of
from sosl.sos.viz.dot import pairs_label
from sosl.sos.viz.model import Figure, Naming
from sosl.sos.viz.render import compile_pdf, pdf_to_png


def emit(fig: Figure, out_dir: str, name: str, layout: str, provenance: str,
         pairs: bool = True) -> str:
    """Write the machine artefacts, seed the hand-owned ``<name>.tex`` if absent,
    and compile *that* one to pdf + png. Returns the hand-owned tex path."""
    os.makedirs(out_dir, exist_ok=True)
    gen_dot = os.path.join(out_dir, f"{name}_gen.dot")
    gen_tex = os.path.join(out_dir, f"{name}_gen.tex")
    tex = os.path.join(out_dir, f"{name}.tex")

    with open(gen_dot, "w") as fh:
        fh.write(f"// {provenance}\n" + dot_of(fig, name.replace("-", "_"), pairs))
    with open(gen_tex, "w") as fh:
        fh.write(tikz_of(fig, place(fig, layout), provenance, pairs))
    if os.path.exists(tex):
        print(f"kept hand-owned {tex} (machine form refreshed in {gen_tex})")
    else:
        shutil.copyfile(gen_tex, tex)
        print(f"seeded hand-owned {tex} from {gen_tex}")

    pdf = compile_pdf(tex)
    print(f"wrote {gen_dot}, {gen_tex}, {pdf}, {pdf_to_png(pdf)}")
    return tex


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="sos2cayley")
    ap.add_argument("sos")
    ap.add_argument("--name", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--rename")
    ap.add_argument("--layout", default="dot", choices=("dot", "layered"))
    ap.add_argument("--no-pairs", action="store_true",
                    help="ablate the P caption; draw the bare algebra A")
    args = ap.parse_args(argv[1:])

    with open(args.sos) as fh:
        inv = load_invariant(fh.read())
    naming = (Naming.renamed(inv.alphabet, args.rename) if args.rename
              else Naming.machine(inv.alphabet))
    fig = figure_of(inv, naming)   # asserts freshness: no edge enters [eps]

    rename = f" --rename {args.rename}" if args.rename else ""
    emit(fig, args.out_dir, args.name, args.layout,
         f"sos2cayley {os.path.basename(args.sos)}{rename}", not args.no_pairs)
    print(pairs_label(fig))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
