"""The ``sos_classify`` tool: classify one `.sos` invariant.

    python3 -m sosl.sos.classify <file.sos>
        [--hoa <file.hoa>]       # reserved for the derivative recursion (C section 8)
        [--cat <out.cat>]        # also write the `.cat` sidecar
        [--certificates]         # (reserved) replay witnesses against --hoa
        [--expect <fixture.cat>] # assert the emitted `.cat` equals a fixture

Exit codes (spec section 2): 0 record emitted; 2 record emitted with gamma
PARTIAL (derivative needed, no resolution — not an error); 3 malformed input;
4 internal invariant violation (a soundness assertion fired — always a bug).
A ``--expect`` mismatch exits 1.
"""
from __future__ import annotations

import argparse
import sys
from typing import List

from .. import load_invariant
from . import classify, render_text
from .io import cat_text


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="sos_classify")
    ap.add_argument("sos")
    ap.add_argument("--hoa")
    ap.add_argument("--cat")
    ap.add_argument("--certificates", action="store_true")
    ap.add_argument("--expect")
    args = ap.parse_args(argv)

    try:
        with open(args.sos) as f:
            inv = load_invariant(f.read())
        inv.validate()
    except (OSError, ValueError, AssertionError, KeyError, IndexError) as exc:
        print(f"malformed input: {exc}", file=sys.stderr)
        return 3

    try:
        rec = classify(inv)
    except AssertionError as exc:
        print(f"internal invariant violation: {exc}", file=sys.stderr)
        return 4

    cat = cat_text(rec)
    print(render_text(rec))
    if args.cat:
        with open(args.cat, "w") as f:
            f.write(cat)

    if args.expect:
        with open(args.expect) as f:
            want = f.read()
        if cat != want:
            print("EXPECT MISMATCH", file=sys.stderr)
            return 1

    return 2 if rec.gamma_partial else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
