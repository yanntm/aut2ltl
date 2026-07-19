"""The main learning loop: drive the teacher until the belief is certified.

    fill; close; consist   -- to a closed, consistent fixpoint
    saturate               -- the two-sided-congruence sweep (restart on a split)
    export                 -- the belief: the table's invariant, canonicalized
    equiv                  -- ask the teacher, on the belief
      Equivalent     -> the belief is I(L); stop
      Counterexample -> process (chains) and restart

The hypothesis shipped to every equivalence query is an `Invariant` — a
well-formed algebraic object, never a bare classifier. Exporting it is legal
exactly because the saturation sweep just ran clean: the partition is a
two-sided congruence, so the class-substituting multiplication is well
defined (`export` is called with ``check=False`` on that certificate). Its
accepting pairs are filled by membership queries through the table's counted
path, so the P phase is visible in ``n_member``.

Consistency is fixed by *minting* the migrated column: a separating column of
the successors ``p.a`` / ``q.a`` moves the letter ``a`` into the column's prefix
(``(x, a.y, t)`` linear, ``(x, a.y)`` omega), which splits the offending class.

Saturation (`sosl.learn.saturate`) turns the right congruence into the syntactic
two-sided one.
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
from sosl.sos.invariant import Invariant
from sosl.trace import TRACE_ON, trace


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
) -> Invariant:
    """Learn the canonical invariant of the teacher's language over ``alphabet``.

    If ``stats`` is given it is populated with basic run counters (learned class
    count, membership queries, equivalence queries, counterexamples, saturation
    escalations)."""
    table = Table(alphabet, teacher.member)
    n_equiv = 0
    n_cex = 0
    n_sat = 0
    while True:
        p = _stabilize(table)
        if saturate(table, p):
            n_sat += 1
            assert n_sat <= 1000, "saturation not converging (non-splitting mint?)"
            if TRACE_ON:
                trace("LEARN", f"saturation escalation {n_sat}: "
                      f"cols={len(table.columns)} classes(pre-split)={p.n}")
            continue
        # The sweep just certified a two-sided congruence: the belief exists.
        belief = export(p, table.query_lasso, check=False)
        n_equiv += 1
        if TRACE_ON:
            trace("LEARN", f"round {n_equiv}: classes={p.n} "
                  f"rows={len(table.rows)} cols={len(table.columns)} cex_so_far={n_cex}")
        result = teacher.equiv(belief)
        if isinstance(result, Equivalent):
            if TRACE_ON:
                trace("LEARN", f"EQUIVALENT ({result.strategy}) classes={p.n}")
            if stats is not None:
                stats.update(
                    learned_classes=belief.n,
                    n_member=table.n_member,
                    n_equiv=n_equiv,
                    n_cex=n_cex,
                    n_saturation=n_sat,
                )
            return belief
        assert isinstance(result, Counterexample)
        n_cex += 1
        if TRACE_ON:
            trace("LEARN", f"counterexample stem={result.lasso.stem} "
                  f"loop={result.lasso.loop}")
        process_counterexample(table, p, result.lasso)
