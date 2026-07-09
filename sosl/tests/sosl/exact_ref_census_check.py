"""Exact-by-reference reproduces the committed ablation-leg classifications.

    python3 -m tests.sosl.exact_ref_census_check [COUNT] [SEED]

The E2 frequency counts are read off the `no-sat-exact` leg, whose oracle this
change replaces. The two oracles decide the same question, so every decided row
of the committed drop (`tests/sosl/reference/flat_canon/census_results.csv.gz`)
must come back with the same verdict, the same `stall_class` and the same
learned class count — a permanent stall stays permanent, a transient one is
still broken by a counterexample.

Sampled, seeded, one row per case; `OVERSIZE` and `BUDGET` rows are excluded
(they were never decided, and `exact_ref_oversize` covers the five deferred
ones). A disagreement here invalidates the published E2 table and is
build-stopping.
"""
from __future__ import annotations

import csv
import gzip
import random
import sys
from pathlib import Path
from typing import Dict, List

from sosl.experiment.manifest import NOSAT_EXACT, flat_canon_cases
from sosl.experiment.run import Config, run_case

DROP = Path("tests/sosl/reference/flat_canon/census_results.csv.gz")
DEFAULT_COUNT = 25
DECIDED = ("SOUND", "ACCEPTOR_ONLY")


def ablation_rows() -> List[Dict[str, str]]:
    """The decided `no-sat-exact` rows of the committed drop."""
    with gzip.open(DROP, "rt", encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh)
                if r["config_id"] == "no-sat-exact" and r["verdict"] in DECIDED]


def main(argv: List[str]) -> int:
    count = int(argv[1]) if len(argv) > 1 else DEFAULT_COUNT
    seed = int(argv[2]) if len(argv) > 2 else 0
    rows = ablation_rows()
    random.Random(seed).shuffle(rows)
    sample = rows[:count]
    cases = {c.case_id: c for c in flat_canon_cases()}
    config = Config(NOSAT_EXACT.config_id, saturation=False, eq_mode="exact",
                    budget_seconds=30)

    print(f"{len(rows)} decided ablation rows; replaying {len(sample)} (seed {seed})")
    for row in sample:
        case = cases[row["case_id"]]
        stats = run_case(case.case_id, case.hoa, config, reference_sos=case.sos).stats
        for field in ("verdict", "stall_class", "learned_classes"):
            assert str(getattr(stats, field)) == row[field], (
                f"{case.case_id}: {field} was {row[field]!r} in the committed drop, "
                f"now {getattr(stats, field)!r} — the E2 table is invalidated"
            )
        print(f"  OK {case.case_id}: {stats.verdict} / {stats.stall_class} "
              f"({stats.learned_classes} of {stats.ref_classes} classes)")
    print("SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
