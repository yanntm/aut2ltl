"""Saturation: promote a right-congruence table to the full two-sided congruence.

A table closed under fill / close / consist is only a *right* congruence — its
rows agree on the columns seen so far, but two rows in one class may still be
told apart when placed as a *left* factor. Saturation hunts those left-context
splits by a zero-query fold comparison and escalates to targeted queries only
where a mismatch shows up.

`saturate` does at most one escalation per call (mint one column, return True);
the caller re-stabilizes and calls again until it returns False — the certificate
that the partition is a two-sided congruence, so the exported invariant's
class-substituting multiplication is sound.

The scan itself is exposed as `find_left_divergence` — the sweep's *check phase*,
a pure fold computation with zero queries. On a certified fixpoint it decides
congruence outright (paper Lemma 5.2): clean scan ⟺ ``ker psi`` is a two-sided
congruence — so it doubles as the export-refusal classifier of spec §3.2 step 6.
The letter-level test (``mult[c][class(a)]`` vs ``step(c, a)``) is NOT a valid
substitute: ``rep(class(a))`` is always a letter, so it is vacuous whenever no
two letters share a class.

Scan order (normative, so transcripts are byte-reproducible): subject words in
shortlex order, classes ``d`` in class-id order; escalate on the FIRST divergence.

For a subject ``p`` whose class representative ``r0`` is not ``p``, and a class
``d`` with representative ``r``, compare ``fold(d, p)`` (class ``c_a``) against
``fold(d, r0)`` (class ``c_b``). On a mismatch, with ``kappa`` the first column
(creation order) separating ``rep(c_a)`` from ``rep(c_b)``:

  - **branch 1** — the bits of ``r.p`` and ``r.r0`` under ``kappa`` differ: mint
    ``kappa`` with ``r`` absorbed into its prefix (``(x.r, y, t)`` / ``(x.r, y)``);
  - **branch 2** — those bits agree: then exactly one of ``r.p`` / ``r.r0``
    disagrees with the representative of its own fold class under ``kappa`` (the
    two rep bits differ and the shared bit matches one of them); run the
    frozen-prefix chain on that word inside ``kappa``'s context.

Either branch mints one column that splits a class on the next stabilization.
"""
from __future__ import annotations

from typing import Optional, Tuple

from sosl.learn.chains import _find_flip
from sosl.learn.columns import Column, LinCol, OmCol
from sosl.learn.partition import Partition
from sosl.learn.table import Table
from sosl.sos.alphabet import Word, shortlex_key
from sosl.sos.lasso import Lasso
from sosl.trace import TRACE_ON, trace


def _bit(table: Table, kappa: Column, w: Word) -> bool:
    """The membership bit of word ``w`` under column ``kappa`` — a counted query
    of the lasso ``kappa`` shapes around ``w``."""
    return table.query_lasso(kappa.lasso(w))


def _frozen_prefix_chain(table: Table, p: Partition, g: Word, kappa: Column) -> None:
    """Mint the one column the frozen-prefix chain isolates: the stem-chain
    replacement scheme run on ``g`` inside ``kappa``'s context, with ``kappa``'s
    own prefix ``x0`` frozen in place. The endpoints (``j = 0`` folds nothing;
    ``j = |g|`` replaces all of ``g`` by ``rep(fold(g))``) differ by construction;
    a binary search finds an adjacent flip ``j``, and the minted column keeps the
    prefix ``x0`` ALONE — the unconsumed segment ``g[j+1:]`` migrates into the
    middle component (spec §3.2 step 5, paper Lemma 4.5)."""
    def repfold(w: Word) -> Word:
        return p.rep[p.fold(w)]

    length = len(g)
    if isinstance(kappa, LinCol):
        x0, y0, t0 = kappa.x, kappa.y, kappa.t

        def bit(j: int) -> bool:
            return table.query_lasso(Lasso(x0 + repfold(g[:j]) + g[j:] + y0, t0))

        j = _find_flip(bit, 0, length)
        if TRACE_ON:
            trace("SAT", f"frozen chain (lin) flip j={j} -> "
                  f"LinCol(x0={x0}, y={g[j + 1:] + y0}, t={t0})")
        table.add_column(LinCol(x0, g[j + 1:] + y0, t0))
    else:
        x0, y0 = kappa.x, kappa.y

        def bit(j: int) -> bool:
            return table.query_lasso(Lasso(x0, repfold(g[:j]) + g[j:] + y0))

        j = _find_flip(bit, 0, length)
        if TRACE_ON:
            trace("SAT", f"frozen chain (om) flip j={j} -> "
                  f"OmCol(x0={x0}, y={g[j + 1:] + y0})")
        table.add_column(OmCol(x0, g[j + 1:] + y0))


def _escalate(table: Table, p: Partition, subj: Word, r0: Word,
              d: int, c_a: int, c_b: int) -> str:
    """Mint the one column the mismatch ``fold(d, subj) = c_a != c_b = fold(d, r0)``
    demands, and return which branch fired (``"branch1"`` or ``"frozen"``)."""
    ra, rb = p.rep[c_a], p.rep[c_b]
    kappa_i = p.separating_column(ra, rb)
    assert kappa_i is not None, "fold classes claimed distinct but no column separates them"
    kappa = table.columns[kappa_i]
    r = p.rep[d]

    b_p = _bit(table, kappa, r + subj)
    b_r0 = _bit(table, kappa, r + r0)
    if TRACE_ON:
        trace("SAT", f"escalate subj={subj} r0={r0} d={d} r={r} "
              f"c_a={c_a} c_b={c_b} kappa=#{kappa_i} b_p={b_p} b_r0={b_r0}")

    if b_p != b_r0:
        # Reproduce "r.w under kappa" as a column on the bare candidate w. For a
        # linear column the candidate sits in the finite prefix, so r prepends
        # there: LinCol(x.r, y, t).bit(w) = member(x.r.w.y, t) = kappa.bit(r.w).
        # For an omega column the candidate rides in the period; peeling one r off
        # the repeating block, x.(r.w.y)^omega = x.r.(w.y.r)^omega, so r seeds BOTH
        # the prefix and the period suffix: OmCol(x.r, y.r).bit(w) = kappa.bit(r.w).
        # (OmCol(x.r, y) alone keeps the period w.y and fails to split on a
        # prefix-independent language such as GF(aa).)
        if isinstance(kappa, LinCol):
            table.add_column(LinCol(kappa.x + r, kappa.y, kappa.t))
        else:
            table.add_column(OmCol(kappa.x + r, kappa.y + r))
        if TRACE_ON:
            trace("SAT", f"branch1: absorb r into context of #{kappa_i}")
        return "branch1"

    # branch 2: shared bit B; exactly one word disagrees with its fold-class rep.
    shared = b_p
    bit_ra = _bit(table, kappa, ra)
    bit_rb = _bit(table, kappa, rb)
    assert bit_ra != bit_rb, "kappa does not separate c_a from c_b"
    disagree_a = shared != bit_ra
    disagree_b = shared != bit_rb
    assert disagree_a != disagree_b, "branch 2 expects exactly one disagreement"
    g = (r + subj) if disagree_a else (r + r0)
    if TRACE_ON:
        trace("SAT", f"branch2: chain on {'r.subj' if disagree_a else 'r.r0'} g={g}")
    _frozen_prefix_chain(table, p, g, kappa)
    return "frozen"


def find_left_divergence(
    table: Table, p: Partition,
) -> Optional[Tuple[Word, Word, int, int, int]]:
    """The sweep's check phase: the first left-context fold divergence
    ``(subj, r0, d, c_a, c_b)`` in normative scan order (subjects shortlex,
    classes ``d`` in id order), or ``None`` if the scan is clean.

    Zero queries — a pure fold computation on the table's own classes. On a
    closed, consistent table ``None`` certifies that ``ker psi`` is a two-sided
    congruence (paper Lemma 5.2), which is the exact premise the exported
    multiplication needs to be well-defined."""
    for subj in sorted(table.domain(), key=shortlex_key):
        c_subj = p.class_of[subj]
        r0 = p.rep[c_subj]
        if r0 is None or r0 == subj:
            continue
        for d in range(p.n):
            c_a = p.fold_from(d, subj)
            c_b = p.fold_from(d, r0)
            if c_a != c_b:
                return subj, r0, d, c_a, c_b
    return None


def saturate(table: Table, p: Partition) -> Optional[str]:
    """One saturation escalation, or ``None`` if the partition is already
    two-sided.

    Runs `find_left_divergence`; on a divergence it mints one column (via
    `_escalate`) and returns the branch that fired (``"branch1"`` / ``"frozen"``)
    — the caller must re-stabilize before calling again. ``None`` is the
    certificate that the table is a full two-sided congruence."""
    div = find_left_divergence(table, p)
    if div is None:
        return None
    subj, r0, d, c_a, c_b = div
    return _escalate(table, p, subj, r0, d, c_a, c_b)
