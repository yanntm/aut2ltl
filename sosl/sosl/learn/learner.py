"""The main learning loop: drive the teacher until the belief is certified.

    probe                  -- bootstrap: each letter's omega-power into the
                              evidence, shortlex order
    fill; close; consist   -- to a closed, consistent fixpoint; fill collapses
                              the frontier by letter classes (proxy bits,
                              `Table` module doc), and a closedness witness is
                              `verify`-grounded before it may become a row
    saturate               -- stamp legality: the two-sided-congruence sweep
                              (restart on a split)
    pairs                  -- pair legality: P saturated under conjugacy
                              (a violation is refereed and chained; restart)
    export                 -- the belief: the table's invariant, canonicalized
    replay                 -- the belief against the evidence, query-free;
                              a contradiction is a discordant lasso with the
                              teacher's bit already in hand -> chain, restart
    equiv                  -- ask the teacher, on the belief
      Equivalent     -> the belief is I(L); stop
      Counterexample -> process (chains) and restart

The equivalence query is posed only at quiescence — the normal form: closed
and consistent, a genuine morphism, a saturated pair layer, and coherent with
every bit of evidence (every lasso ever queried, under any presentation, is
predicted with the teacher's own answer).

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
from sosl.learn.pairs import saturation_violation
from sosl.learn.partition import Partition
from sosl.learn.saturate import saturate
from sosl.learn.table import Table
from sosl.sos.alphabet import EMPTY, Alphabet
from sosl.sos.invariant import Invariant
from sosl.sos.lasso import Lasso
from sosl.trace import TRACE_ON, trace


def _evidence_discordance(table: Table, belief: Invariant) -> Optional[Lasso]:
    """The first witnessed bit ``belief`` contradicts — a discordant lasso
    whose teacher bit is already in hand — or ``None`` when the belief is
    evidence-coherent. Query-free: a replay of `Invariant.member` over the
    ledger, in first-query order."""
    for lasso, bit in table.evidence.items():
        if belief.member(lasso) != bit:
            return lasso
    return None


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
            # A speculative signature never promotes: ground each witness's
            # proxied bits first; if any bit moves, regroup before deciding.
            changed = False
            for w in unclosed:
                if table.verify(w):
                    changed = True
            if changed:
                if TRACE_ON:
                    trace("STAB", "verify: closedness witness corrected, regroup")
                continue
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
    # Bootstrap probe sweep (the last a-priori experimentation): each letter's
    # omega-power into the evidence, shortlex order; the coherence replay
    # below converts any discordance among these opening bits into a split.
    for a in alphabet.letters():
        table.query_lasso(Lasso(EMPTY, (a,)))
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
        # Pair legality: P saturated under conjugacy; a violation is a
        # refereed discordance, chained like any other.
        viol = saturation_violation(table, p)
        if viol is not None:
            n_sat += 1
            if TRACE_ON:
                trace("LEARN", f"pair escalation: stem={viol.stem} "
                      f"loop={viol.loop}")
            process_counterexample(table, p, viol)
            continue
        # Both legality checks clean: the belief exists.
        belief = export(p, table.query_lasso, check=False)
        dis = _evidence_discordance(table, belief)
        if dis is not None:
            if TRACE_ON:
                trace("LEARN", f"evidence discordance stem={dis.stem} "
                      f"loop={dis.loop} (replay, zero queries)")
            process_counterexample(table, p, dis)
            continue
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
