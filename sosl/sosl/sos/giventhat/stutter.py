"""Stutter invariance as one instance of the quotient engine.

Collapsing every letter's square onto the letter (`M(la,la) ~ la`) is the
congruence whose recognizable languages are the stutter-invariant ones (paper
Prop 5.6). So `sc` is `hull` under that congruence, and the interval-membership
question "is there a stutter-invariant `B`?" is one `admits` — but the verdict
is **YES / UNKNOWN, never NO** (paper Thm 5.7: the least stutter-invariant
superset can escape the table, and then the interval may still hold a member the
hull cannot exhibit; trap #11).

Paper §5.4's AP shedding is the same engine under `lambda(l) ~ lambda(l')`
seeds — not commissioned, but the API does not foreclose it.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from ..calculus.table import PairSet, Table
from .interval import Interval
from .quotient import admits, congruence, hull, least_member

Verdict = str  # "YES" | "UNKNOWN"


def stutter_seeds(table: Table) -> List[Tuple[int, int]]:
    """The seeds `M(la, la) ~ la` over the distinct letter classes — identify
    each letter with its own square, the generators of the stutter congruence."""
    mult = table.mult
    return [(mult[la][la], la) for la in sorted(set(table.letter_class))]


def sc(table: Table, q: PairSet) -> PairSet:
    """The stutter closure of `q` (paper Prop 5.6's `SC`, on the table): the
    least stutter-recognizable superset, as `hull` under the stutter
    congruence."""
    return hull(congruence(table, stutter_seeds(table)), q)


def exists_stutter_invariant(iv: Interval) -> Tuple[Verdict, Optional[PairSet]]:
    """Does the interval contain a stutter-invariant `B`? YES with the least
    member `hull(P_min)` when the stutter hull stays under `P_max`; otherwise
    **UNKNOWN** — never NO (paper Thm 5.7)."""
    quot = congruence(iv.table, stutter_seeds(iv.table))
    if admits(quot, iv):
        return "YES", least_member(quot, iv)
    return "UNKNOWN", None
