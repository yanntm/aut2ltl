"""The main learning loop: drive the teacher until the hypothesis is certified,
then export the canonical invariant.

    fill; close; consist   -- to a closed, consistent fixpoint
    saturate               -- the two-sided-congruence sweep (restart on a split)
    equiv                  -- ask the teacher
      Equivalent    -> export and stop
      Counterexample -> process (chains) and restart

Consistency is fixed by *minting* the migrated column: a separating column of
the successors ``p.a`` / ``q.a`` moves the letter ``a`` into the column's prefix
(``(x, a.y, t)`` linear, ``(x, a.y)`` omega), which splits the offending class.

Saturation (`sosl.learn.saturate`) turns the right congruence into the syntactic
two-sided one; it is skipped under ``saturation=False`` (the M2 ablation), which
still converges but only to an acceptance-correct fixpoint — the certified
Cayley acceptor. Export then refuses (`NotCongruent`) unless that fixpoint
happens to be a congruence, in which case it is canonical (paper Theorem 5.3);
``unchecked_export`` bypasses the refusal to *display* the raw read-off
(diagnostic fixtures only, never a deliverable).
"""
from __future__ import annotations

from typing import Dict, Optional

from sosl.contract import Counterexample, Equivalent, Teacher
from sosl.learn.chains import process_counterexample
from sosl.learn.columns import LinCol, OmCol
from sosl.learn.export import export
from sosl.learn.partition import Partition
from sosl.learn.saturate import saturate
from sosl.learn.table import Table
from sosl.sos.alphabet import Alphabet
from sosl.sos.hypothesis import Hypothesis
from sosl.sos.invariant import Invariant
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
                trace("STAB", f"close: +{len(unclosed)} rows "
                      f"(rows={len(table.rows)} cols={len(table.columns)} classes={p.n})")
            for w in unclosed:
                table.add_row(w)
            continue
        if _make_consistent(table, p):
            if TRACE_ON:
                trace("STAB", f"consist: mint col -> {len(table.columns)} "
                      f"(rows={len(table.rows)} classes={p.n})")
            continue
        if TRACE_ON:
            trace("STAB", f"stable: rows={len(table.rows)} "
                  f"cols={len(table.columns)} classes={p.n}")
        return p


def learn(
    teacher: Teacher, alphabet: Alphabet, stats: Optional[Dict[str, int]] = None,
    saturation: bool = True, unchecked_export: bool = False,
) -> Invariant:
    """Learn the canonical invariant of the teacher's language over ``alphabet``.

    With ``saturation`` (the default), the two-sided-congruence sweep runs to a
    fixpoint before every equivalence query, so the exported invariant is sound;
    with it off (the M2 ablation, experiment E2) the learner still converges to
    an acceptance-correct fixpoint, and export refuses (`NotCongruent`) when
    that fixpoint is not a congruence — unless ``unchecked_export`` asks for the
    raw read-off (diagnostic display only).

    If ``stats`` is given it is populated with basic run counters (learned class
    count, membership queries, equivalence queries, counterexamples, saturation
    escalations)."""
    table = Table(alphabet, teacher.member)
    n_equiv = 0
    n_cex = 0
    n_sat = 0
    while True:
        p = _stabilize(table)
        if saturation and saturate(table, p):
            n_sat += 1
            assert n_sat <= 1000, "saturation not converging (non-splitting mint?)"
            if TRACE_ON:
                trace("LEARN", f"saturation escalation {n_sat}: "
                      f"cols={len(table.columns)} classes(pre-split)={p.n}")
            continue
        n_equiv += 1
        if TRACE_ON:
            trace("LEARN", f"round {n_equiv}: classes={p.n} "
                  f"rows={len(table.rows)} cols={len(table.columns)} cex_so_far={n_cex}")
        result = teacher.equiv(_build_hypothesis(table, p))
        if isinstance(result, Equivalent):
            if TRACE_ON:
                trace("LEARN", f"EQUIVALENT ({result.strategy}) classes={p.n}")
            # A saturated run's final sweep just ran clean, so the congruence
            # check is already done; only the ablation needs it (or skips it,
            # for the unchecked display).
            inv = export(p, teacher.member,
                         check=not saturation and not unchecked_export)
            if stats is not None:
                stats.update(
                    learned_classes=inv.n,
                    n_member=table.n_member,
                    n_equiv=n_equiv,
                    n_cex=n_cex,
                    n_saturation=n_sat,
                )
            return inv
        assert isinstance(result, Counterexample)
        n_cex += 1
        if TRACE_ON:
            trace("LEARN", f"counterexample stem={result.lasso.stem} "
                  f"loop={result.lasso.loop}")
        process_counterexample(table, p, result.lasso)
