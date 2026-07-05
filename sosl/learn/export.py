"""Build the canonical invariant from a closed, consistent partition.

At a fixpoint the partition is a finite congruence; this reads its *raw algebra*
off the partition's own class numbering — the letter map ``lambda(a) =
step(start, a)``, the multiplication ``M[c][d] = fold(c, rep(d))``, and the
accepting linked pairs P (one membership query on ``rep(s).rep(e)^omega`` per
linked pair, the identity excluded as it is never a loop) — and hands it to the
shared `canonicalize` normal form (`sosl.objects.canonical`), which re-keys and
renumbers. Using that shared normal form is what makes an exported invariant
byte-comparable with a reference-built one.
"""
from __future__ import annotations

from typing import List

from sosl.learn.columns import Member
from sosl.learn.partition import Partition
from sosl.objects.alphabet import EMPTY
from sosl.objects.canonical import canonicalize
from sosl.objects.invariant import Invariant
from sosl.objects.lasso import Lasso


def export(p: Partition, member: Member) -> Invariant:
    """The canonical `Invariant` for a closed, consistent partition ``p``."""
    ab = p.table.alphabet
    n = p.n

    letter_class = [p.step(p.start, a) for a in ab.letters()]
    mult = [[p.fold_from(c, p.rep[d]) for d in range(n)] for c in range(n)]

    accept = set()
    for e in range(n):
        if p.rep[e] == EMPTY or mult[e][e] != e:  # identity is never a loop
            continue
        for s in range(n):
            if mult[s][e] == s and member(Lasso(p.rep[s], p.rep[e])):
                accept.add((s, e))

    return canonicalize(ab, p.start, letter_class, mult, accept)
