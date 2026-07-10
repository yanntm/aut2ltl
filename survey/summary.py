"""survey.summary — rebuild a run's SUMMARY from its CSV.

The summary is a fold over the rows and nothing else, so a complete CSV is a
sufficient record of a run: `survey.report.summarize` reads only `result`,
`validation`, `dag`, `temporals` and `build_s`, all of them columns. A run whose
summary was never captured, or was captured in pieces — a sharded cluster run,
whose every command summarized only its own slice — is summarized after the fact,
once the run is fully reaped, from the merged CSV.

Every row is one run, so they fold together into one summary. The `--use` label a
live run prints is not in the CSV (which records the technique that answered, not
the one that was asked for); name it with `--label` when it matters.

Exits 1 when a verified non-equivalence (`validation == FAIL`) is present, as the
live run does, so this is usable as a gate.

    python3 -m survey.summary logs/cluster/$RUN/results.csv > SUMMARY.txt
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional

from survey.report import summarize


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="survey.summary",
        description="Rebuild a run's summary from the CSV it produced.")
    p.add_argument("csv", type=Path, metavar="FILE", help="a survey CSV")
    p.add_argument("--label", default="default", metavar="TECH",
                   help="the technique the run was asked for; the CSV records "
                        "only the one that answered")
    args = p.parse_args(argv)

    with args.csv.open(newline="") as fh:
        rows: List[Dict[str, object]] = list(csv.DictReader(fh))
    if not rows:
        print(f"survey.summary: no rows in {args.csv}", file=sys.stderr)
        return 2

    for line in summarize(rows, args.label):
        print(line)

    return 1 if any(r.get("validation") == "FAIL" for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
