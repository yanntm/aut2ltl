"""Publish a validated campaign drop to the committed reference tree (spec §8
item 9, the reproducibility floor). `tests/**/logs/` is build-machine scratch and
is never cited by the report; this step **copies** a validated drop's
load-bearing outputs into the curated, committed `tests/sosl/reference/<campaign>/`
tree so every reported figure traces to a git-committed, machine-generated file.

    # after the sweep + analyzers + gates are green:
    python3 -m tests.sosl.flatcanon_gates > tests/sosl/logs/census/gates.txt
    python3 -m tests.sosl.publish_reference [campaign]      # default: flat_canon

Copies the analyzer summaries and the gate report verbatim, and **gzips** the raw
sweep CSVs (they compress ~10x and MB-scale raw data does not belong in git; the
per-language ROLL `targets/` scratch is never copied). It does not compute
anything — run the analyzers/gates first; a missing source is a warning.
Idempotent: re-running overwrites the destination, so a drop is immutable only by
convention (commit it, then leave it).
"""
from __future__ import annotations

import gzip
import shutil
import sys
from pathlib import Path
from typing import List, Tuple

REFERENCE = Path("tests/sosl/reference")
LOGS = Path("tests/sosl/logs")

# (source under logs/, destination under reference/<campaign>/). The load-bearing
# outputs behind the report's flat_canon tables.
# (source under logs/, destination under reference/<campaign>/). A `.csv` source
# is gzipped to `<dest>.gz`; everything else is copied verbatim.
FLAT_CANON: List[Tuple[str, str]] = [
    ("census/results.csv", "census_results.csv.gz"),   # raw sweep, both legs (E1+E2)
    ("census_e1/summary.md", "e1_summary.md"),          # E1 cost + SoS ventilation
    ("census_e2/flat_canon.md", "e2_exhibits.md"),      # E2 permanent family + buckets
    ("census_e3/results.csv", "e3_results.csv.gz"),     # E3 ROLL raw
    ("census_e3/summary.md", "e3_summary.md"),           # E3 medians + wash + LTL cut
    ("census/gates.txt", "gates.txt"),                   # (d′) + dual-symmetry report
]

DROPS = {"flat_canon": FLAT_CANON}


def main(argv: List[str]) -> int:
    campaign = argv[0] if argv else "flat_canon"
    drop = DROPS.get(campaign)
    if drop is None:
        print(f"unknown campaign {campaign}; known: {sorted(DROPS)}",
              file=sys.stderr)
        return 2

    dest_dir = REFERENCE / campaign
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = missing = 0
    for src_rel, dst_name in drop:
        src = LOGS / src_rel
        if not src.exists():
            print(f"  MISSING {src} — not produced yet (run its analyzer/gate)",
                  file=sys.stderr)
            missing += 1
            continue
        dst = dest_dir / dst_name
        if dst_name.endswith(".gz"):
            with open(src, "rb") as fi, gzip.open(dst, "wb") as fo:
                shutil.copyfileobj(fi, fo)
        else:
            shutil.copy2(src, dst)
        print(f"  {src}  ->  {dst}  ({dst.stat().st_size} B)")
        copied += 1

    print(f"published {copied} file(s) to {dest_dir}"
          + (f"; {missing} missing" if missing else ""))
    print("commit the reference/ tree; cite these paths in the report.")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
