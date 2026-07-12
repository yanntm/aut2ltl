"""The ``sos_viz`` tool: draw the Cayley graph of one `.sos` invariant.

    python3 -m sosl.sos.viz <file.sos>
        [-o <out.dot|.tex|.pdf|.png>]  # format from the extension; default: dot to stdout
        [--rename 'a=a,!a=b']          # display letters, in display order
        [--layout dot|layered]         # node placement (default: dot)
        [--no-pairs]                   # ablate the P caption (bare algebra A)

The object is `<A, P>`: the drawing is the algebra `A`, and `P` rides under it as
a *caption* — an accepting pair is a pair of classes, not a transition, so it is
typeset, never drawn as edges. `--no-pairs` ablates it. P is always echoed on
stdout. A `.png` is rendered by GraphViz.

Exit codes: 0 written; 1 bad usage or a failing external tool; 4 the invariant
violates a structural law (freshness, reachability — always a bug upstream).
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import List

from .. import load_invariant
from . import dot_of, figure_of, place, tikz_of
from .dot import pairs_label
from .model import Naming
from .render import compile_pdf, dot_to_png, pdf_to_png


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="sos_viz")
    ap.add_argument("sos")
    ap.add_argument("-o", "--out")
    ap.add_argument("--rename")
    ap.add_argument("--layout", default="dot", choices=("dot", "layered"))
    ap.add_argument("--no-pairs", action="store_true",
                    help="ablate the P caption; draw the bare algebra A")
    args = ap.parse_args(argv[1:])
    pairs = not args.no_pairs

    with open(args.sos) as fh:
        inv = load_invariant(fh.read())
    naming = (Naming.renamed(inv.alphabet, args.rename) if args.rename
              else Naming.machine(inv.alphabet))
    try:
        fig = figure_of(inv, naming)
    except AssertionError as exc:
        print(f"sos_viz: {args.sos} is not a valid invariant: {exc}", file=sys.stderr)
        return 4

    rename = f" --rename {args.rename}" if args.rename else ""
    provenance = f"sos_viz {os.path.basename(args.sos)}{rename}"
    ext = os.path.splitext(args.out)[1].lower() if args.out else ".dot"
    try:
        if ext == ".dot" or args.out is None:
            text = dot_of(fig, pairs=pairs)
            if args.out is None:
                sys.stdout.write(text)
            else:
                _write(args.out, text)
        elif ext == ".tex":
            _write(args.out, tikz_of(fig, place(fig, args.layout), provenance, pairs))
        elif ext == ".pdf":
            tex = os.path.splitext(args.out)[0] + ".tex"
            _write(tex, tikz_of(fig, place(fig, args.layout), provenance, pairs))
            print(f"wrote {compile_pdf(tex)}")
        elif ext == ".png":
            dot_to_png(dot_of(fig, pairs=pairs), args.out)
            print(f"wrote {args.out}")
        else:
            print(f"sos_viz: unknown output format {ext!r}", file=sys.stderr)
            return 1
    except RuntimeError as exc:
        print(f"sos_viz: {exc}", file=sys.stderr)
        return 1

    print(pairs_label(fig))
    return 0


def _write(path: str, text: str) -> None:
    """Write ``text`` to ``path`` and say so."""
    with open(path, "w") as fh:
        fh.write(text)
    print(f"wrote {path}")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
