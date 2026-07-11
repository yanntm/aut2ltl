"""The distance ``d_p(L1, L2) = mu_p(L1 xor L2)``, exact, on the aligned product.

Both languages are moved onto one table (the calculus ``align`` +
``materialize``); there the symmetric difference of the two pair sets
presents ``L1 xor L2`` outright — membership of a cell is a single pair
lookup on the shared table, so the xor of the lookups is the lookup in the
xor of the sets. The distance is `measure` of that (non-reduced) invariant.

The xor's θ-profile is returned with the value: all-zero iff the distance
is 0 under *every* full-support ``p`` — the null-disagreement read-off,
decided with no second measure run (see `algorithm.md` §7).
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, Optional

from ..sos.alphabet import Letter
from ..sos.invariant import Invariant
from ..sos.calculus import Table, align, materialize
from .measure import measure
from .theta import ThetaProfile


@dataclass(frozen=True)
class DistanceResult:
    """The distance of two languages under one Bernoulli ``p``, with the
    θ-profile of their symmetric difference on the aligned table."""

    value: Fraction
    profile: ThetaProfile

    @property
    def null_disagreement(self) -> bool:
        """True iff the two languages differ by a null set — the xor's
        θ-profile is all-zero, so the distance is 0 for every
        full-support ``p``, not just the one measured."""
        return not any(bit for (_, bit) in self.profile.entries)


def distance(
    a: Invariant, b: Invariant, p: Optional[Dict[Letter, Fraction]] = None
) -> DistanceResult:
    """``d_p`` of the two invariants' languages (default uniform ``p``),
    as an exact `Fraction` with the xor θ-profile. Both invariants must
    share one alphabet; the aligned product is materialized, so the cost
    is ``O(n_a * n_b)``-bounded in table size."""
    la = Table.of(a).language(a.accept)
    lb = Table.of(b).language(b.accept)
    prod = materialize(align(la, lb), la, lb)
    xor = prod.table.invariant(prod.pairs_a ^ prod.pairs_b)
    result = measure(xor, p)
    return DistanceResult(value=result.value, profile=result.profile)
