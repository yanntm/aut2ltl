"""Build the canonical invariant from a closed, consistent partition.

At a fixpoint the partition is a finite congruence; this reads its *raw algebra*
off the partition's own class numbering — the letter map ``lambda(a) =
step(start, a)``, the multiplication ``M[c][d] = fold(c, rep(d))``, and the
accepting linked pairs P (one membership query on ``rep(s).rep(e)^omega`` per
linked pair, the identity excluded as it is never a loop) — and hands it to the
shared `canonicalize` normal form (`sosl.sos.build.canonical`), which re-keys and
renumbers. Using that shared normal form is what makes an exported invariant
byte-comparable with a reference-built one.
"""
from __future__ import annotations

from typing import List, Optional

from sosl.learn.columns import Member
from sosl.learn.partition import Partition
from sosl.sos.alphabet import Word, shortlex_key
from sosl.sos.build.canonical import canonicalize
from sosl.sos.invariant import Invariant
from sosl.sos.lasso import Lasso


def _loop_rep(p: Partition, c: int) -> Optional[Word]:
    """The shortlex-least non-empty word of class ``c`` (a loop must be
    non-empty), or ``None`` if the class is strictly the empty word."""
    cands = [w for w in p.members[c] if w]
    return min(cands, key=shortlex_key) if cands else None


def export(p: Partition, member: Member) -> Invariant:
    """The canonical `Invariant` for a closed, consistent partition ``p``."""
    ab = p.table.alphabet
    n = p.n

    letter_class = [p.step(p.start, a) for a in ab.letters()]
    mult = [[p.fold_from(c, p.rep[d]) for d in range(n)] for c in range(n)]

    accept = set()
    for e in range(n):
        if mult[e][e] != e:
            continue
        loop = _loop_rep(p, e)
        if loop is None:  # a strictly-empty class cannot be a loop
            continue
        for s in range(n):
            if mult[s][e] == s and member(Lasso(p.rep[s], loop)):
                accept.add((s, e))

    return canonicalize(ab, p.start, letter_class, mult, accept)
