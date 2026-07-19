"""Figure artifacts for the sos_learning paper — machine-dumped `.sos` files of
the learner's day-one beliefs, drawn core-style by
`research_notes/sos_core_figs` (the `sosl_`-prefixed figures; `make sosl` there).

    python3 -m tests.sosl.fig_learner_exports [out_dir]

One artifact per case, each a machine product of the learner itself (no
hand-written data), written under ``out_dir`` (default: the core figs
`sources/`):

  sosl_even_day1.sos, sosl_evenblocks_day1.sos,
  sosl_a_implies_xa_day1.sos, sosl_a_once_day1.sos
      The hypothesis each run passes to its FIRST equivalence query — the
      learner's day-one belief (paper §3, Figure 3), a well-formed language of
      its own. Captured by running the learner against a recorder that answers
      the first query with `Equivalent`; the belief the query carried is the
      export. Asserted well-formed (conjugacy-closed): the day-one belief
      denotes a language of its own.

The frozen `sosl_a_implies_xa_stall.sos` (the §4.2 ablation read-off) is *not*
produced here — its ablation path was removed from the learner; the committed
`.sos` stands as a display artifact and is drawn by the Makefile's `sosl:`
target from that committed file.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

from sosl.contract import Equivalent, EquivResult, Teacher
from sosl.experiment.manifest import case_by_id
from sosl.learn.learner import learn
from sosl.sos import dump_invariant
from sosl.sos.calculus.surgery import is_saturated
from sosl.sos.calculus.table import Table as CalcTable
from sosl.sos.invariant import Invariant
from sosl.sos.lasso import Lasso
from sosl.teacher.whitebox import HoaTeacher

OUT_DEFAULT = "../research_notes/sos_core_figs/sources"


class _FirstEqTeacher:
    """A teacher decorator that defers membership to ``inner`` and stops the
    learner at its first equivalence query — answering `Equivalent` — so the
    query's hypothesis (recorded in ``first``) is the learner's day-one belief.
    The learner is a pure query algorithm, so no learner change is needed to
    read the belief it presents."""

    def __init__(self, inner: Teacher) -> None:
        self._inner = inner
        self.first: Optional[Invariant] = None

    def member(self, lasso: Lasso) -> bool:
        return self._inner.member(lasso)

    def equiv(self, hypothesis: Invariant) -> EquivResult:
        if self.first is None:
            self.first = hypothesis
        return Equivalent("stop-at-first-eq")


def day1_invariant(hoa_path: str) -> Invariant:
    """The invariant the learner presents at its FIRST equivalence query on the
    language of ``hoa_path`` — its day-one belief.

    Captured, not recomputed: the learner runs to its first query and the
    hypothesis that query carries is returned. This is the *actual* pre-EQ
    fixpoint — closed, consistent, a morphism AND pair-legal — not the
    stabilize/saturate head alone, which predates pair legality and undercounts
    (`even`/`evenblocks` split once more under conjugacy before the first
    query)."""
    teacher = HoaTeacher.of_hoa(hoa_path)
    rec = _FirstEqTeacher(teacher)
    belief = learn(rec, teacher.alphabet)
    assert rec.first is belief, "learner returned a belief it never presented"
    return belief


def _write(out: Path, name: str, inv: Invariant) -> None:
    path = out / f"{name}.sos"
    path.write_text(dump_invariant(inv), encoding="utf-8")
    print(f"wrote {path} ({inv.n} classes, {len(inv.accept)} accepting pairs)")


def main(argv: List[str]) -> int:
    out = Path(argv[1] if len(argv) > 1 else OUT_DEFAULT)
    out.mkdir(parents=True, exist_ok=True)

    for case_id, expect_n in (("even", 3), ("evenblocks", 3),
                              ("a_implies_xa", 2), ("a_once", 2)):
        case = case_by_id(case_id)
        assert case is not None, case_id
        inv = day1_invariant(case.hoa)
        assert inv.n == expect_n, f"{case_id} day-one: {inv.n} classes, expected {expect_n}"
        assert is_saturated(CalcTable.of(inv), frozenset(inv.accept)), \
            f"{case_id} day-one pair set is not conjugacy-closed"
        _write(out, f"sosl_{case_id}_day1", inv)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
