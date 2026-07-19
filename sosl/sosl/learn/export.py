"""Build the canonical invariant from a closed, consistent partition.

The read-off is only well-defined on a **two-sided congruence**: the letter map
``lambda(a) = step(start, a)``, the multiplication ``M[c][d] = fold(c, rep(d))``
(a *representative* of ``d`` substituted mid-product), and the accepting linked
pairs P (one membership query on ``rep(s).rep(e)^omega`` per linked pair, the
identity excluded as it is never a loop). By default `export` therefore runs the
congruence test first — the saturation sweep's check phase, zero queries (paper
Lemma 5.2) — and raises `NotCongruent` on a dirty check: there is no algebra to
export (spec §3.2 step 6). ``check=False`` skips the test, either because the
caller has already run it (a saturated run's final sweep, or a pre-computed
classification) or to *display* the raw read-off a non-congruent fixpoint would
produce (the ``--unchecked`` diagnostic of rows P7/F8); an unchecked export is
never a deliverable.

The clean read-off is handed to the shared `canonicalize` normal form
(`sosl.sos.core.canonical`), which re-keys and renumbers. Using that shared
normal form is what makes an exported invariant byte-comparable with a
reference-built one; its reachability assertion stays as a backstop on its own
contract.
"""
from __future__ import annotations

from typing import List

from sosl.learn.columns import Member
from sosl.learn.partition import Partition
from sosl.learn.saturate import find_left_divergence
from sosl.sos.alphabet import Word
from sosl.sos.core.canonical import canonicalize
from sosl.sos.invariant import Invariant
from sosl.sos.lasso import Lasso


class NotCongruent(Exception):
    """`export` refused: the partition's kernel is not a two-sided congruence,
    so the class-substituting multiplication is not well-defined and there is
    no algebra to export. Carries the first divergence of the check scan:
    ``fold(d, subj) != fold(d, r0)`` with ``r0 = rep(class(subj))``."""

    def __init__(self, subj: Word, r0: Word, d: int) -> None:
        self.subj = subj
        self.r0 = r0
        self.d = d
        super().__init__(
            f"not a congruence: fold(d={d}, subj={subj}) != fold(d={d}, rep={r0})")


def export(p: Partition, member: Member, check: bool = True) -> Invariant:
    """The canonical `Invariant` for a closed, consistent partition ``p``.

    With ``check`` (the default) the Lemma 5.2 congruence test runs first and a
    dirty check raises `NotCongruent`; ``check=False`` trusts the caller (see
    the module docstring)."""
    if check:
        div = find_left_divergence(p.table, p)
        if div is not None:
            subj, r0, d, _c_a, _c_b = div
            raise NotCongruent(subj, r0, d)

    ab = p.table.alphabet
    n = p.n

    letter_class = [p.step(p.start, a) for a in ab.letters()]
    mult = [[p.fold_from(c, p.rep[d]) for d in range(n)] for c in range(n)]

    accept = set()
    for e in range(n):
        # The identity is never a loop (its key is the empty word).
        if e == p.start or mult[e][e] != e:
            continue
        for s in range(n):
            # The keyed lasso rep(s).rep(e)^omega — the same bit the pair
            # legality scan cached, so this fill replays evidence.
            if mult[s][e] == s and member(Lasso(p.rep[s], p.rep[e])):
                accept.add((s, e))

    return canonicalize(ab, p.start, letter_class, mult, accept)
