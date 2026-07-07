"""The ``sos_classify`` tool: classify one `.sos` invariant.

    python3 -m sosl.sos.classify <file.sos>
        [--hoa <file.hoa>]        # reserved for the derivative recursion (C section 8)
        [--json <out.json>]       # also write the flat record as JSON
        [--certificates]          # (reserved) replay witnesses against --hoa
        [--expect <fixture.json>] # assert the emitted record equals a fixture

Exit codes (spec section 2): 0 record emitted; 2 record emitted with gamma
PARTIAL (derivative needed, no resolution — not an error); 3 malformed input;
4 internal invariant violation (a soundness assertion fired — always a bug).
A ``--expect`` mismatch exits 1.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from .. import load_invariant
from . import classify, record_to_dict, render_text


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(prog="sos_classify")
    ap.add_argument("sos")
    ap.add_argument("--hoa")
    ap.add_argument("--json")
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

    doc = record_to_dict(rec)
    print(render_text(rec))
    if args.json:
        with open(args.json, "w") as f:
            json.dump(doc, f, indent=2, sort_keys=True)

    if args.expect:
        with open(args.expect) as f:
            want = json.load(f)
        if doc != want:
            print("EXPECT MISMATCH", file=sys.stderr)
            return 1

    return 2 if rec.gamma_partial else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
