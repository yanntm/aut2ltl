"""Sweep a folder of HOA automata through the Π₂-hunt predicate and tally.

Recurses a folder for `.hoa` files and runs `predicate.py` on EACH as its own
subprocess (one input per invocation, a hard per-file timeout so a single stall
is a recorded finding, never a blocked sweep). Classifies every file by its
predicate verdict into a death histogram, lists any HIT and any P3-benign
near-miss (the interesting group-bearing cases), and writes a markdown report.

Usage:  python3 tests/pi2_hunt/sweep.py <folder> [--out <file.md>] [--timeout S]

The report is markdown on stdout, or to --out. Exit 0 if a HIT was found, 1 if
none, 2 if the folder held no readable HOA.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter
from typing import List, Tuple

from aut2ltl import bounded

_HERE = os.path.dirname(os.path.abspath(__file__))
_PREDICATE = os.path.join(_HERE, "predicate.py")

# a coarse bucket per line, most-informative-first
_BUCKETS: List[Tuple[str, str]] = [
    ("HIT", r": HIT "),
    ("P3-benign", r"P3-benign"),
    ("P2-fail", r"P2-fail"),
    ("P1-fail", r"P1-fail"),
    ("P3-blocked", r"P3-blocked"),
    ("P3-none", r"P3-none"),
    ("ERROR", r": ERROR "),
    ("TIMEOUT", r": TIMEOUT"),
]


def _classify(line: str) -> str:
    for name, pat in _BUCKETS:
        if re.search(pat, line):
            return name
    return "OTHER"


def _find_hoa(folder: str) -> List[str]:
    if os.path.isfile(folder):
        return [folder]
    out: List[str] = []
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in ("logs", "__pycache__") and not d.startswith(".")]
        for f in sorted(files):
            if f.endswith(".hoa"):
                out.append(os.path.join(root, f))
    return sorted(out)


def _run_one(path: str, timeout: int) -> str:
    """Run the predicate on one file under aut2ltl.bounded (which wraps
    `timeout --signal=INT`, so a stalled decomposition's GAP process group is
    reaped by the child's own handler rather than orphaned)."""
    res = bounded.run([sys.executable, _PREDICATE, path], timeout)
    if res.timed_out:
        return f"{path}: TIMEOUT (>{timeout}s)"
    line = (res.out or res.err or "").strip().splitlines()
    return line[0] if line else f"{path}: ERROR empty output"


def _render(folder: str, total: int, done: int, hist: "Counter[str]",
            hits: List[str], benign: List[str]) -> str:
    """Build the markdown report from the running tallies (progress-aware)."""
    denom = sum(hist[b] for b in ("HIT", "P3-benign", "P3-none", "P3-blocked"))
    md: List[str] = [f"# Π₂-hunt sweep — `{folder}`\n"]
    md.append(f"- progress: **{done}/{total}** files"
              + ("  _(in progress)_" if done < total else "  _(complete)_"))
    md.append(f"- passed P1∧P2 (the real denominator): **{denom}**")
    md.append(f"- **HITs: {len(hits)}**\n")
    md.append("## Death histogram\n")
    md.append("| bucket | count |")
    md.append("|---|---|")
    for name, _ in _BUCKETS + [("OTHER", "")]:
        if hist.get(name):
            md.append(f"| {name} | {hist[name]} |")
    if hits:
        md.append("\n## HITS (counterexamples — refute the conjecture)\n")
        md += [f"- `{h}`" for h in hits]
    if benign:
        md.append("\n## P3-benign near-misses (form group, star-free language)\n")
        md += [f"- `{b}`" for b in benign]
    return "\n".join(md) + "\n"


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out", default=None, help="markdown report path (default logs/<folder>.md)")
    ap.add_argument("--timeout", type=int, default=15)
    ap.add_argument("--limit", type=int, default=0, help="stop after N files (0 = all)")
    ap.add_argument("--refresh", type=int, default=10, help="rewrite the report every N files")
    args = ap.parse_args(argv)

    files = _find_hoa(args.folder)
    if args.limit:
        files = files[:args.limit]
    if not files:
        print(f"no .hoa under {args.folder}", file=sys.stderr)
        return 2

    out = args.out or os.path.join(_HERE, "logs", os.path.basename(args.folder.rstrip("/")) + ".md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    raw_path = os.path.splitext(out)[0] + ".lines.txt"

    hist: "Counter[str]" = Counter()
    hits: List[str] = []
    benign: List[str] = []

    # Raw per-file lines are appended and flushed as we go, so an interrupted run
    # loses nothing and the file can be tailed live; the markdown report is
    # rewritten every --refresh files (and at the end) from the running tallies.
    with open(raw_path, "w") as raw:
        for i, path in enumerate(files, 1):
            line = _run_one(path, args.timeout)
            bucket = _classify(line)
            hist[bucket] += 1
            raw.write(f"{bucket}\t{line}\n")
            raw.flush()
            if bucket == "HIT":
                hits.append(line)
            elif bucket == "P3-benign":
                benign.append(line)
            if i % args.refresh == 0 or i == len(files):
                with open(out, "w") as fh:
                    fh.write(_render(args.folder, len(files), i, hist, hits, benign))
            if bucket in ("HIT", "TIMEOUT", "ERROR") or i % args.refresh == 0:
                print(f"[{i}/{len(files)}] {bucket}", file=sys.stderr)

    print(f"done: {out} (+ {raw_path})", file=sys.stderr)
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
