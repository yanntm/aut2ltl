"""One learner run, in its own process, printing its `RunStats` as a CSV row.

    python3 -m sosl.experiment.run_one CASE_ID HOA [--sos REF] [--budget S]
                                       [--config default|bounded]

The child half of the bounded runner (`run.run_case_bounded`). It exists so a run
can be bounded from *outside* the interpreter: `run_case`'s own budget is a
`signal.alarm`, and Python defers a signal handler to a bytecode boundary, so a
run sitting inside a native call (Spot / BuDDy) cannot be interrupted by it. Only
the OS can stop that run, and only if it owns the process.

Prints exactly one line — `csv_row(stats)`, in `CSV_FIELDS` order — on stdout, so
the parent reconstructs the record with `stats.parse_row`. Everything else goes
to stderr. A run that faults still prints its row (`run_case` records CRASH); a
run the parent kills prints nothing, and the parent synthesizes the BUDGET row.
"""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Optional

from sosl.experiment.manifest import BOUNDED, DEFAULT
from sosl.experiment.run import Config, run_case
from sosl.experiment.stats import csv_row

CONFIGS = {c.config_id: c for c in (DEFAULT, BOUNDED)}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("case_id")
    ap.add_argument("hoa")
    ap.add_argument("--sos", default=None, metavar="REF",
                    help="precomputed reference .sos (the census fast path)")
    ap.add_argument("--config", default="default", choices=sorted(CONFIGS))
    ap.add_argument("--budget", type=int, default=None, metavar="S",
                    help="the run's own (cooperative) budget; the parent's kill "
                         "is the hard one")
    args = ap.parse_args(argv)

    base = CONFIGS[args.config]
    cfg = base if args.budget is None else Config(
        **{**base.__dict__, "budget_seconds": args.budget})
    res = run_case(args.case_id, args.hoa, cfg, reference_sos=args.sos)
    csv.writer(sys.stdout).writerow(csv_row(res.stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
