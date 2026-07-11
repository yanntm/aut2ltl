"""The export-refusal gate — spec §8 item 13(c), the local checks before the drop.

    python3 -m tests.sosl.congruence_gate

Four exact-ablation (`--no-saturation --eq-mode exact`) runs, each a named case
the 2026-07-11 ruling pins:

  - `a_implies_xa` and `a_once` (the proven-permanent specimens): the run must
    certify the stall and REFUSE the export — verdict `ACCEPTOR_ONLY`,
    `fixpoint_congruent = false`, no invariant produced;
  - the ex-crasher `2state2ap2acc_parity_16186325768790242365` and its
    complement (the loudest of the 17 export-assert crashes): after the fix
    they classify like the rest — `ACCEPTOR_ONLY`, never `CRASH`.

Exits non-zero listing every violated expectation.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from sosl.experiment.manifest import NOSAT_EXACT, flat_canon_cases
from sosl.experiment.run import Config, RunResult, run_case

SPECIMENS: List[Tuple[str, Optional[str]]] = [
    ("a_implies_xa", "samples/a_implies_xa.hoa"),
    ("a_once", "samples/a_once.hoa"),
]
EX_CRASHERS = [
    "2state2ap2acc_parity_16186325768790242365",
    "2state2ap2acc_parity_16186325768790242365_c",
]


def _check(res: RunResult, problems: List[str]) -> None:
    s = res.stats
    tag = f"{s.case_id}/{s.config_id}"
    if s.verdict != "ACCEPTOR_ONLY":
        problems.append(f"{tag}: verdict {s.verdict} (want ACCEPTOR_ONLY; "
                        f"detail: {s.detail})")
    if s.fixpoint_congruent != "false":
        problems.append(f"{tag}: fixpoint_congruent {s.fixpoint_congruent} "
                        f"(want false)")
    if res.invariant is not None:
        problems.append(f"{tag}: an invariant was produced (export must refuse)")
    if s.export_associative != "n/a":
        problems.append(f"{tag}: export_associative {s.export_associative} "
                        f"(want n/a on a refusal)")


def main() -> int:
    cfg = Config(**{**NOSAT_EXACT.__dict__, "budget_seconds": 30})
    problems: List[str] = []

    for case_id, hoa in SPECIMENS:
        res = run_case(case_id, hoa, cfg)
        _check(res, problems)
        print(f"  {case_id}: {res.stats.verdict} "
              f"congruent={res.stats.fixpoint_congruent}")

    by_id = {c.case_id: c for c in flat_canon_cases()
             if c.case_id in EX_CRASHERS}
    for case_id in EX_CRASHERS:
        case = by_id.get(case_id)
        if case is None:
            problems.append(f"{case_id}: not in the flat_canon catalogue")
            continue
        res = run_case(case.case_id, case.hoa, cfg, reference_sos=case.sos)
        _check(res, problems)
        print(f"  {case_id}: {res.stats.verdict} "
              f"congruent={res.stats.fixpoint_congruent}")

    if problems:
        print("FAILURES:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("OK — specimens + ex-crashers all refuse: ACCEPTOR_ONLY, "
          "fixpoint_congruent=false, no CRASH")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
