"""The measure shadow: the theta = 1 stem-region read-off on the invariant's
own table (paper Prop 4.1).

With ``D`` the union of the theta = 1 bottom SCCs of the right-Cayley graph,
the shadow's pair set keeps exactly the linked pairs whose stem class lies
in ``D``; the result is reduced to the canonical invariant of that language.
It is at distance 0 from the input under every full-support ``p``, the
operation is idempotent, and it never reads ``p`` — no ``p`` parameter
exists (see `algorithm.md` §8). Shadow byte-equality is sufficient for
``d_p = 0``, not necessary.
"""
from __future__ import annotations

from ..sos.invariant import Invariant
from ..sos.calculus import Table, reduce
from .chain import bottom_sccs
from .theta import theta_profile


def shadow(inv: Invariant) -> Invariant:
    """The reduced invariant of ``inv``'s shadow language: lassos whose
    stem class lies in a theta = 1 bottom SCC of ``inv``'s table."""
    profile = theta_profile(inv)
    region = frozenset(
        c
        for scc, (_, bit) in zip(bottom_sccs(inv), profile.entries)
        if bit
        for c in scc
    )
    table = Table.of(inv)
    pairs = frozenset((s, e) for (s, e) in table.linked if s in region)
    return reduce(table, pairs)
