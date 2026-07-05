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
is the acceptance-correct M2 learner.
"""
from __future__ import annotations

from typing import Dict, Optional

from sosl.contract import Counterexample, Equivalent, Teacher
from sosl.learn.chains import process_counterexample
from sosl.learn.columns import LinCol, OmCol
from sosl.learn.export import export
from sosl.learn.partition import Partition
from sosl.learn.table import Table
from sosl.objects.alphabet import Alphabet
from sosl.objects.cayley import Hypothesis
from sosl.objects.invariant import Invariant
from sosl.trace import TRACE_ON, trace


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
            if TRACE_ON:
                trace("stab", f"close: +{len(unclosed)} rows "
                      f"(rows={len(table.rows)} cols={len(table.columns)} classes={p.n})")
            for w in unclosed:
                table.add_row(w)
            continue
        if _make_consistent(table, p):
            if TRACE_ON:
                trace("stab", f"consist: mint col -> {len(table.columns)} "
                      f"(rows={len(table.rows)} classes={p.n})")
            continue
        if TRACE_ON:
            trace("stab", f"stable: rows={len(table.rows)} "
                  f"cols={len(table.columns)} classes={p.n}")
        return p


def learn(
    teacher: Teacher, alphabet: Alphabet, stats: Optional[Dict[str, int]] = None
) -> Invariant:
    """Learn the canonical invariant of the teacher's language over ``alphabet``.

    If ``stats`` is given it is populated with basic run counters (learned class
    count, membership queries, equivalence queries, counterexamples)."""
    table = Table(alphabet, teacher.member)
    n_equiv = 0
    n_cex = 0
    while True:
        p = _stabilize(table)
        n_equiv += 1
        if TRACE_ON:
            trace("learn", f"round {n_equiv}: classes={p.n} "
                  f"rows={len(table.rows)} cols={len(table.columns)} cex_so_far={n_cex}")
        result = teacher.equiv(_build_hypothesis(table, p))
        if isinstance(result, Equivalent):
            if TRACE_ON:
                trace("learn", f"EQUIVALENT ({result.strategy}) classes={p.n}")
            inv = export(p, teacher.member)
            if stats is not None:
                stats.update(
                    learned_classes=inv.n,
                    n_member=table.n_member,
                    n_equiv=n_equiv,
                    n_cex=n_cex,
                )
            return inv
        assert isinstance(result, Counterexample)
        n_cex += 1
        if TRACE_ON:
            trace("learn", f"counterexample stem={result.lasso.stem} "
                  f"loop={result.lasso.loop}")
        process_counterexample(table, p, result.lasso)
