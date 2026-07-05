"""The main learning loop: drive the teacher until the hypothesis is certified,
then export the canonical invariant.

    fill; close; consist   -- to a closed, consistent fixpoint
    equiv                  -- ask the teacher
      Equivalent    -> export and stop
      Counterexample -> process (chains) and restart

Consistency is fixed by *minting* the migrated column: a separating column of
the successors ``p.a`` / ``q.a`` moves the letter ``a`` into the column's prefix
(``(x, a.y, t)`` linear, ``(x, a.y)`` omega), which splits the offending class.

Saturation (the two-sided-congruence phase) is not part of this loop yet; this
is the acceptance-correct M2 learner. Counterexample processing is likewise a
stub until the chains land — a returned counterexample raises rather than
silently looping.
"""
from __future__ import annotations

from sosl.contract import Counterexample, Equivalent, Teacher
from sosl.learn.columns import LinCol, OmCol
from sosl.learn.export import export
from sosl.learn.partition import Partition
from sosl.learn.table import Table
from sosl.objects.alphabet import Alphabet
from sosl.objects.cayley import Hypothesis
from sosl.objects.invariant import Invariant
from sosl.objects.lasso import Lasso


def _build_hypothesis(table: Table, p: Partition) -> Hypothesis:
    """The Cayley-form hypothesis for a closed partition (empty accept cache —
    the teacher resolves misses via the representative lasso)."""
    ab = table.alphabet
    keys = tuple(p.rep[c] for c in range(p.n))
    step = tuple(tuple(p.step(c, a) for a in ab.letters()) for c in range(p.n))
    return Hypothesis(alphabet=ab, keys=keys, step=step, accept={}, start=p.start)


def _make_consistent(table: Table, p: Partition) -> bool:
    """If inconsistent, mint the migrated column and return True; else False."""
    inc = p.inconsistency()
    if inc is None:
        return False
    _p, _q, a, col_i = inc
    src = table.columns[col_i]
    if isinstance(src, LinCol):
        table.add_column(LinCol(src.x, (a,) + src.y, src.t))
    else:
        table.add_column(OmCol(src.x, (a,) + src.y))
    return True


def _stabilize(table: Table) -> Partition:
    """Run fill / close / consist until closed and consistent."""
    while True:
        table.fill()
        p = Partition(table)
        unclosed = p.unclosed()
        if unclosed:
            for w in unclosed:
                table.add_row(w)
            continue
        if _make_consistent(table, p):
            continue
        return p


def learn(teacher: Teacher, alphabet: Alphabet) -> Invariant:
    """Learn the canonical invariant of the teacher's language over ``alphabet``."""
    table = Table(alphabet, teacher.member)
    while True:
        p = _stabilize(table)
        result = teacher.equiv(_build_hypothesis(table, p))
        if isinstance(result, Equivalent):
            return export(p, teacher.member)
        assert isinstance(result, Counterexample)
        raise NotImplementedError(
            "counterexample chains land in the next increment; "
            f"got {result.lasso}"
        )
