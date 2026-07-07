"""Even paper-trace conformance gate (spec §8, M3).

    python3 -m tests.sosl.even_conformance

Drives the saturated learner on Even and asserts the run reproduces the paper's
§4.3 trace exactly:

  - the day-one sweep is clean (the initial 3-class table needs no saturation
    before the first equivalence query);
  - exactly ONE equivalence counterexample, the lasso ``(eps, a;a;!a)``, which
    splits ``a;a``;
  - the four-class sweep then fires (branch 2) and mints the LINEAR column
    ``(eps, a;!a, a;a;!a)`` — not the omega column ``(a, eps)`` (which would mean
    the sweep scan order is wrong).

The letters are masks over AP ``a``: ``!a = 0``, ``a = 1``.
"""
from __future__ import annotations

from typing import List, Tuple

from sosl.contract import Counterexample
from sosl.learn.chains import process_counterexample
from sosl.learn.columns import LinCol
from sosl.learn.learner import _build_hypothesis, _stabilize
from sosl.learn.saturate import saturate
from sosl.learn.table import Table
from sosl.sos.lasso import Lasso
from sosl.teacher import HoaTeacher

EVEN = "samples/even.hoa"

# expected trace artifacts (masks: !a=0, a=1)
CEX = Lasso((), (1, 1, 0))                      # (eps, a;a;!a)
SWEEP_COL = LinCol((), (1, 0), (1, 1, 0))       # (eps, a;!a, a;a;!a)
BAD_OMEGA = ("a", "eps")                        # the wrong mint, for the message


def drive(teacher: HoaTeacher) -> Tuple[List[Lasso], List[object], int]:
    """Learn Even with saturation, recording the counterexamples seen and the
    columns present at the end, plus the day-one sweep verdict. Returns
    ``(cexes, final_columns, day_one_saturations)``."""
    table = Table(teacher.alphabet, teacher.member)
    cexes: List[Lasso] = []
    day_one_sats = 0
    first_round = True
    while True:
        p = _stabilize(table)
        if saturate(table, p):
            if first_round:
                day_one_sats += 1
            continue
        first_round = False
        res = teacher.equiv(_build_hypothesis(table, p))
        if not isinstance(res, Counterexample):
            return cexes, list(table.columns), day_one_sats
        cexes.append(res.lasso)
        process_counterexample(table, p, res.lasso)


def main() -> int:
    t = HoaTeacher.of_hoa(EVEN)
    cexes, columns, day_one_sats = drive(t)

    assert day_one_sats == 0, f"day-one sweep not clean: {day_one_sats} escalation(s)"
    assert cexes == [CEX], f"counterexamples {cexes} != [{CEX}]"
    assert SWEEP_COL in columns, (
        f"sweep did not mint the linear column {SWEEP_COL}; columns={columns}. "
        f"If it minted the omega column {BAD_OMEGA} instead, the sweep scan order "
        "is not per spec §3.2 step 4."
    )
    print("OK Even conformance: clean day-one sweep; one cex (eps, a;a;!a); "
          "sweep mints linear (eps, a;!a, a;a;!a)")
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
