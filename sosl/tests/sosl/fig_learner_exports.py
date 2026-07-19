"""Figure artifacts for the sos_learning paper — machine-dumped `.sos` files of
the learner's intermediate objects, drawn core-style by
`research_notes/sos_core_figs` (the `sosl_`-prefixed figures; `make sosl` there).

    python3 -m tests.sosl.fig_learner_exports [out_dir]

Three artifacts, each a machine product of the learner itself (no hand-written
data), written under ``out_dir`` (default: the core figs `sources/`):

  sosl_even_day1.sos, sosl_evenblocks_day1.sos
      The hypothesis each run passes to its FIRST equivalence query, exported
      as the invariant it provably is (paper Lemma 5.2): fill / close /
      consist / sweep to the pre-EQ fixpoint — the head of
      `sosl.learn.learner.learn` — then the checked export, whose pair set is
      filled by teacher queries over all linked pairs. Asserted well-formed
      (conjugacy-closed): the day-one belief denotes a language of its own.

  sosl_a_implies_xa_stall.sos
      The ablated (no-saturation, exact-oracle) run's certified stalled
      fixpoint on `a_implies_xa` — the raw unchecked read-off of paper §4.2.
      NOT an algebra (its table is not associative); a display artifact,
      never a deliverable.
"""
from __future__ import annotations

import sys
from pathlib import Path

from sosl.experiment.manifest import case_by_id
from sosl.experiment.run import _reference
from sosl.learn.export import export
from sosl.learn.learner import _stabilize, learn
from sosl.learn.saturate import saturate
from sosl.learn.table import Table
from sosl.sos import dump_invariant
from sosl.sos.calculus.surgery import is_saturated
from sosl.sos.calculus.table import Table as CalcTable
from sosl.sos.invariant import Invariant
from sosl.teacher.whitebox import HoaTeacher

OUT_DEFAULT = "../research_notes/sos_core_figs/sources"


def day1_invariant(hoa_path: str) -> Invariant:
    """The invariant carried by the learner's first equivalence query on the
    language of ``hoa_path``: stabilize and sweep to the pre-EQ fixpoint, then
    the checked export (`NotCongruent` would mean the sweep did not run clean —
    impossible here, and asserted by ``check=True``)."""
    teacher = HoaTeacher.of_hoa(hoa_path)
    table = Table(teacher.alphabet, teacher.member)
    while True:
        p = _stabilize(table)
        if not saturate(table, p):
            break
    return export(p, teacher.member, check=True)


def stall_invariant(case_id: str) -> Invariant:
    """The ablation leg's certified stalled fixpoint on ``case_id``, through
    the learner's own display path: no saturation, exact oracle, and the
    ``unchecked_export`` raw read-off (a proper export would refuse —
    Theorem 5.3; this artifact exists to be *drawn*, never consumed)."""
    case = case_by_id(case_id)
    assert case is not None, case_id
    _dump, ref = _reference(case.hoa, case.sos)
    teacher = HoaTeacher.of_hoa(case.hoa, eq_mode="exact", reference=ref)
    return learn(teacher, teacher.alphabet, saturation=False,
                 unchecked_export=True)


def _write(out: Path, name: str, inv: Invariant) -> None:
    path = out / f"{name}.sos"
    path.write_text(dump_invariant(inv), encoding="utf-8")
    print(f"wrote {path} ({inv.n} classes, {len(inv.accept)} accepting pairs)")


def main(argv: list) -> int:
    out = Path(argv[1] if len(argv) > 1 else OUT_DEFAULT)
    out.mkdir(parents=True, exist_ok=True)

    for case_id, expect_n in (("even", 3), ("evenblocks", 3)):
        case = case_by_id(case_id)
        assert case is not None, case_id
        inv = day1_invariant(case.hoa)
        assert inv.n == expect_n, f"{case_id} day-one: {inv.n} classes, expected {expect_n}"
        assert is_saturated(CalcTable.of(inv), frozenset(inv.accept)), \
            f"{case_id} day-one pair set is not conjugacy-closed"
        _write(out, f"sosl_{case_id}_day1", inv)

    stall = stall_invariant("a_implies_xa")
    assert stall.n == 4, f"a_implies_xa stall: {stall.n} classes, expected 4"
    _write(out, "sosl_a_implies_xa_stall", stall)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
