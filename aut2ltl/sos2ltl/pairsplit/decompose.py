"""pairsplit/decompose.py — the invariant-plane split (algorithm.md).

Pure `sosl.sos` level: choose the side of P / P̄ with the fewest saturation
atoms (complement is a free set flip), partition it into atoms, and return
one canonical, alphabet-minimal `Invariant` per piece. No aut2ltl imports —
the translator assembly consumes the plan through `split_plan` alone.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from sosl.sos import Invariant
from sosl.sos.calculus.table import Table, PairSet
from sosl.sos.calculus.surgery import complement, conjugacy_classes
from sosl.sos.calculus.reduce import reduce
from sosl.sos.minimize import remove_free_aps


@dataclass(frozen=True)
class SplitPlan:
    """One decomposition: translate every invariant in `pieces`, OR the
    labels, negate the disjunction iff `negate` (the complement side was
    taken)."""
    negate: bool
    pieces: Tuple[Invariant, ...]


def atoms_of(table: Table, pairs: PairSet) -> List[PairSet]:
    """The saturation atoms (conjugacy classes) contained in `pairs`. A
    saturated set is exactly the union of the classes it intersects."""
    return [k for k in conjugacy_classes(table) if k & pairs]


def piece_invariant(table: Table, group: PairSet) -> Invariant:
    """One piece: the group's language over the shared table, re-quotiented to
    its canonical invariant (`reduce`) and projected onto its minimal alphabet
    (`remove_free_aps` — restricting P can free an AP; algorithm.md
    "Fusion criteria")."""
    return remove_free_aps(reduce(table, group))


def split_plan(inv: Invariant) -> Optional[SplitPlan]:
    """The least-pairs decomposition of `inv`, or None where it cannot help.

    Side rule (algorithm.md "The general form"): a side is a CANDIDATE only
    if it has >= 2 atoms — a single-atom side offers no decomposition (it is
    the undecomposable hard block; picking it by raw count is exactly
    backwards on the conjunctive-recurrence stratum, where P is one atom and
    P̄ many trivial ones). Among candidates, least atoms; ties to P (no outer
    negation). No candidate → None (pass-through)."""
    table = Table.of(inv)
    p_atoms = atoms_of(table, inv.accept)
    n_atoms = atoms_of(table, complement(table, inv.accept))
    candidates = [(len(side), negate, side)
                  for negate, side in ((False, p_atoms), (True, n_atoms))
                  if len(side) >= 2]
    if not candidates:
        return None
    _, negate, chosen = min(candidates, key=lambda t: (t[0], t[1]))
    return SplitPlan(
        negate=negate,
        pieces=tuple(piece_invariant(table, g) for g in chosen))


__all__ = ["SplitPlan", "atoms_of", "piece_invariant", "split_plan"]
