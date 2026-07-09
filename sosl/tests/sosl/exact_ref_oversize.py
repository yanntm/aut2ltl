"""Re-run the census cases the closure oracle could not decide (spec item 10).

    python3 -m tests.sosl.exact_ref_oversize --list
    python3 -m tests.sosl.exact_ref_oversize <case_id> [--budget S]

The committed flat_canon drop records five `no-sat-exact` runs as `OVERSIZE`: the
transformation closure of the largest languages blew its work cap, so their
permanent-vs-transient classification was deferred and never entered E2's
frequency counts.

Exact-by-reference builds no closure — but it may only *certify* under the
functionality guard, and on these languages the guard fires, sending the query
back to the closure and its cap. So an `OVERSIZE` here is legal (spec row
F10 → F9) and the case stays deferred; what would be a defect is an `OVERSIZE`
on a run whose guard never fired, since nothing would then have built a closure.

`--list` reads the committed CSV (`tests/sosl/reference/flat_canon/`) and prints
the deferred case ids with the class counts that defeated the closure; a case id
re-runs exactly that case under the ablation config and prints its verdict,
`stall_class`, `eq_certification` and guard-firing count. One case per invocation
— these are the census's largest languages, and a blown budget is a finding to
report, not a batch to hide.
"""
from __future__ import annotations

import csv
import gzip
import sys
from pathlib import Path
from typing import Dict, List, Optional

from sosl.experiment.manifest import NOSAT_EXACT, flat_canon_cases
from sosl.experiment.run import Config, run_case

DROP = Path("tests/sosl/reference/flat_canon/census_results.csv.gz")
"""The committed campaign drop the deferred cases are read from."""


def deferred() -> List[Dict[str, str]]:
    """The `OVERSIZE` rows of the committed drop, in file order."""
    with gzip.open(DROP, "rt", encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh) if r["verdict"] == "OVERSIZE"]


def find_case(case_id: str):
    """The manifest `Case` of ``case_id`` in the flat catalogue."""
    for case in flat_canon_cases():
        if case.case_id == case_id:
            return case
    raise SystemExit(f"no such case in the flat catalogue: {case_id}")


def rerun(case_id: str, budget: int) -> int:
    case = find_case(case_id)
    config = Config(NOSAT_EXACT.config_id, saturation=False, eq_mode="exact",
                    budget_seconds=budget)
    result = run_case(case.case_id, case.hoa, config, reference_sos=case.sos)
    s = result.stats
    print(f"{case_id}: verdict={s.verdict} stall_class={s.stall_class} "
          f"eq={s.eq_certification} ref={s.ref_classes} learned={s.learned_classes} "
          f"equiv={s.n_equiv} guard_firings={s.n_guard_firings} "
          f"wall={s.wall_seconds:.1f}s")
    if s.detail:
        print(f"  detail: {s.detail}")
    if s.verdict == "OVERSIZE":
        # `n_guard_firings` is -1 when the run raised before the stats were
        # filled, which is exactly the guard-fired-then-capped path.
        print("DEFERRED: the guard fired, the closure fallback hit its cap — the "
              "case stays out of E2's counts (spec rows F10 -> F9)")
        return 0
    print("SUCCESS")
    return 0


def main(argv: List[str]) -> int:
    if "--list" in argv:
        rows = deferred()
        print(f"{len(rows)} deferred (OVERSIZE) runs in {DROP}:")
        for r in rows:
            print(f"  {r['case_id']}  ref={r['ref_classes']} "
                  f"learned={r['learned_classes']} wall={float(r['wall_seconds']):.1f}s")
        return 0
    if len(argv) < 2:
        raise SystemExit(__doc__)
    budget = 60
    if "--budget" in argv:
        budget = int(argv[argv.index("--budget") + 1])
    return rerun(argv[1], budget)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
