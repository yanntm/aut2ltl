"""The measure ``mu_p(L)`` of an invariant's language, exact.

``mu_p(L) = sum_C theta_C * Pr[absorption in C]`` over the bottom SCCs of
the right-Cayley graph (Theorem 3.4 of the paper); the absorption
probabilities solve the standard transient linear system, done here by
hand-rolled Gauss–Jordan elimination over `fractions.Fraction` with one
right-hand-side column per bottom SCC. Everything is exact — no floats —
and nothing assumes the table is reduced, so a complement-flipped ``P``
works unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, FrozenSet, List, Optional, Tuple

from ..sos.alphabet import Alphabet, Letter
from ..sos.invariant import Invariant
from .chain import bottom_sccs
from .theta import ThetaProfile, theta_profile


@dataclass(frozen=True)
class MeasureResult:
    """The measure of a language under one Bernoulli ``p``, with its
    certificate: the theta-profile and the absorption probability of each
    bottom SCC from the identity, in the canonical bottom-SCC order
    (entries keyed like the profile's)."""

    value: Fraction
    profile: ThetaProfile
    absorption: Tuple[Tuple[str, Fraction], ...]


def uniform(inv: Invariant) -> Dict[Letter, Fraction]:
    """The uniform Bernoulli measure on ``inv``'s alphabet:
    ``p(a) = 1/|Sigma|`` for every letter."""
    size = inv.alphabet.size
    return {a: Fraction(1, size) for a in inv.alphabet.letters()}


def _validate_p(alphabet: Alphabet, p: Dict[Letter, Fraction]) -> None:
    """Assert ``p`` is a full-support rational Bernoulli measure: every
    letter of the alphabet present, every value an exact rational > 0
    (no floats), values summing to exactly 1."""
    letters = alphabet.letters()
    assert set(p.keys()) == set(letters), (
        f"p must weight exactly the {len(letters)} alphabet letters"
    )
    total = Fraction(0)
    for a in letters:
        v = p[a]
        assert isinstance(v, (int, Fraction)) and not isinstance(v, bool), (
            f"p({a}) must be an exact rational, got {type(v).__name__}"
        )
        assert v > 0, f"p({a}) = {v} is not > 0 (full support required)"
        total += v
    assert total == 1, f"p sums to {total}, not 1"


def _solve(
    a: List[List[Fraction]], b: List[List[Fraction]]
) -> List[List[Fraction]]:
    """Solve ``a @ x = b`` in place by Gauss–Jordan elimination over
    `Fraction`, ``b`` holding any number of right-hand-side columns.
    ``a`` must be nonsingular: a zero pivot column after full row search
    is an assertion failure."""
    t = len(a)
    for col in range(t):
        piv = next((r for r in range(col, t) if a[r][col] != 0), None)
        assert piv is not None, "singular system (zero pivot column)"
        a[col], a[piv] = a[piv], a[col]
        b[col], b[piv] = b[piv], b[col]
        d = a[col][col]
        a[col] = [v / d for v in a[col]]
        b[col] = [v / d for v in b[col]]
        for r in range(t):
            f = a[r][col]
            if r == col or f == 0:
                continue
            a[r] = [vr - f * vc for vr, vc in zip(a[r], a[col])]
            b[r] = [vr - f * vc for vr, vc in zip(b[r], b[col])]
    return b


def measure(
    inv: Invariant, p: Optional[Dict[Letter, Fraction]] = None
) -> MeasureResult:
    """The measure of ``inv``'s language under the Bernoulli measure ``p``
    (default uniform), as an exact `Fraction` with its certificate.

    Unknowns are the transient classes (those in no bottom SCC — always
    including the identity); each satisfies ``x_c = sum_a p(a) *
    rhs(M(c, lambda(a)))`` where ``rhs`` is the unknown of a transient
    successor and the per-SCC boundary indicator otherwise. Solved once
    with one column per bottom SCC, giving the absorption probabilities
    from the identity; these must sum to exactly 1, and the value is the
    theta-weighted sum."""
    if p is None:
        p = uniform(inv)
    _validate_p(inv.alphabet, p)
    bottoms: List[FrozenSet[int]] = bottom_sccs(inv)
    profile = theta_profile(inv)
    scc_of: Dict[int, int] = {
        c: j for j, scc in enumerate(bottoms) for c in scc
    }
    transient = [c for c in range(inv.n) if c not in scc_of]
    assert inv.identity in set(transient), "the identity must be transient"
    idx = {c: i for i, c in enumerate(transient)}
    nb = len(bottoms)
    zero = Fraction(0)
    a = [[zero] * len(transient) for _ in transient]
    b = [[zero] * nb for _ in transient]
    for c in transient:
        i = idx[c]
        a[i][i] += 1
        for letter, weight in p.items():
            d = inv.mult[c][inv.letter_class[letter]]
            if d in idx:
                a[i][idx[d]] -= weight
            else:
                b[i][scc_of[d]] += weight
    x = _solve(a, b)
    root = x[idx[inv.identity]]
    assert sum(root, zero) == 1, (
        f"absorption probabilities sum to {sum(root, zero)}, not 1"
    )
    absorption = tuple(
        (profile.entries[j][0], root[j]) for j in range(nb)
    )
    value = sum(
        (root[j] for j in range(nb) if profile.entries[j][1]), zero
    )
    return MeasureResult(value=value, profile=profile, absorption=absorption)
