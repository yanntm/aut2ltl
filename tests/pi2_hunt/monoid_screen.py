"""Fast cascade-free screen: which minimal forms in a corpus carry a group?

For every `.hoa` under a folder, close the transition monoid in-process (no
cascade, no GAP, no oracle -- pure algebra, ~instant) and tally aperiodic vs
group-bearing. A group-bearing minimal star-free form is a Π₂-hunt hit candidate
(the group forces a non-star-free Inf(C)); this is the cheap pre-screen the
expensive predicate then confirms. Lists the group-bearing files with the period
and witness word.

Usage:  python3 tests/pi2_hunt/monoid_screen.py <folder> [--out <file.md>]
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from typing import List

import spot

from monoid_check import analyze


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
    ap.add_argument("folder")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    files = _find_hoa(args.folder)
    hist: "Counter[str]" = Counter()
    groups: List[str] = []
    for path in files:
        try:
            n, size, period, witness, image = analyze(spot.automaton(path))
        except Exception as e:
            hist["error"] += 1
            continue
        if period > 1:
            hist["group"] += 1
            groups.append(f"{os.path.basename(path)}\tstates={n} period={period} "
                          f"word={witness} image={image}")
        else:
            hist["aperiodic"] += 1

    lines = [f"# transition-monoid screen — `{args.folder}`\n",
             f"- files: **{len(files)}**",
             f"- aperiodic (no group): **{hist['aperiodic']}**",
             f"- **group-bearing (hit candidates): {hist['group']}**",
             f"- errors: {hist['error']}\n",
             "## group-bearing minimal forms\n"]
    lines += [f"- `{g}`" for g in groups]
    report = "\n".join(lines) + "\n"
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(report)
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
