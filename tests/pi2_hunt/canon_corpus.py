"""Canonicalise a folder of ω-automata to minimal deterministic forms for the hunt.

The genaut census stores arbitrary (often nondeterministic, transition-based)
automata, so an as-is state count is not comparable to a minimal one. This reads
every `.hoa` under a folder, maps each to its SAT-min-backed minimal deterministic
form (Language.det_generic_minimal), keeps only genuine recurrences (acceptance
mentions Inf), dedups by AP-normalised minimal HOA, and writes the survivors out.
Every emitted automaton is therefore minimal by construction, so a downstream
predicate sweep tests P1 ∧ P3 on the true minimal witness (P2 holds trivially).

Usage:  python3 tests/pi2_hunt/canon_corpus.py <in_dir> --out <out_dir>
                 [--max-states N]

Prints a read/kept summary to stderr.
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import List

import spot

from aut2ltl.ltl.twa import dump_hoa

from aut2ltl.language import Language
from survey.normalize import normalize_hoa


def _find_hoa(folder: str) -> List[str]:
    out: List[str] = []
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in ("logs", "__pycache__") and not d.startswith(".")]
        for f in sorted(files):
            if f.endswith(".hoa"):
                out.append(os.path.join(root, f))
    return sorted(out)


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("in_dir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-states", type=int, default=8)
    args = ap.parse_args(argv)

    os.makedirs(args.out, exist_ok=True)
    files = _find_hoa(args.in_dir)
    seen: set = set()
    kept = 0
    read = 0
    skipped = 0
    for path in files:
        read += 1
        try:
            aut = spot.automaton(path)
            det = Language.of(aut).det_generic_minimal()
        except Exception:
            skipped += 1
            continue
        n = det.num_states()
        if n < 2 or n > args.max_states or "Inf" not in str(det.get_acceptance()):
            continue
        key = normalize_hoa(det.to_str("hoa"))
        if key in seen:
            continue
        seen.add(key)
        det.set_name(f"canon of {os.path.basename(path)}")
        with open(os.path.join(args.out, f"canon_{kept:04d}_s{n}.hoa"), "w") as fh:
            fh.write(dump_hoa(det))
        kept += 1

    print(f"read={read} skipped={skipped} kept(distinct minimal recurrence)={kept} "
          f"-> {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
