"""The given-that interval and its endpoint decisions.

Two invariants — the property's complement and the prior knowledge — are
aligned once and materialized onto one product table; the endpoints

    P_min := P_neg_phi & P_K        P_max := P_neg_phi | P_K^c

are free Boolean moves on it, and the legal choices between them form the
powerset lattice of the *freedom* classes (conjugacy classes outside `P_K`) —
the Prop 3.1 identity, asserted on every construction (a violation is an
upstream align / materialize / saturate bug, never handled here). Endpoint
decisions are one emptiness scan each, minimal-lasso witnesses always; see
`algorithm.md` for the ideas, `README.md` to use the package.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import FrozenSet, Iterable, List, Optional, Tuple

from ..calculus import Table, align, materialize
from ..calculus.decide import is_empty
from ..calculus.surgery import (
    complement,
    conjugacy_classes,
    difference,
    intersection,
    is_saturated,
    union,
)
from ..calculus.table import PairSet
from ..calculus.witness import Witness
from ..invariant import Invariant

ConjClass = PairSet
"""One conjugacy class of linked pairs — one freedom bit of the interval."""


@dataclass(frozen=True)
class Interval:
    """The given-that interval `[P_min, P_max]` on the materialized product
    table, with its freedom classes in first-representative discipline order.
    Frozen; every field is over `table`."""

    table: Table
    p_neg_phi: PairSet
    p_k: PairSet
    p_min: PairSet
    p_max: PairSet
    freedom: Tuple[ConjClass, ...]

    @property
    def bits(self) -> int:
        """`|F|` of paper Prop 3.1 — the freedom of the choice, in bits."""
        return len(self.freedom)


def given_that(neg_phi: Invariant, k: Invariant) -> Interval:
    """The interval of legal choices given that the system satisfies `k`,
    for the property whose complement is `neg_phi`. Both invariants must be
    over the same alphabet (same AP set and order) — a mismatch is a caller
    error (`inverse_substitution` is the adapter, out of scope here)."""
    if neg_phi.alphabet != k.alphabet:
        raise ValueError(
            f"given_that: alphabets differ ({neg_phi.alphabet.aps} vs "
            f"{k.alphabet.aps}); adapt with inverse_substitution first")

    t_phi, t_k = Table.of(neg_phi), Table.of(k)
    lang_phi = t_phi.language(neg_phi.accept)
    lang_k = t_k.language(k.accept)
    prod = materialize(align(lang_phi, lang_k), lang_phi, lang_k)

    table = prod.table
    p_neg_phi, p_k = prod.pairs_a, prod.pairs_b
    p_min = intersection(table, p_neg_phi, p_k)
    p_max = union(table, p_neg_phi, complement(table, p_k))

    freedom: List[ConjClass] = []
    for cls in conjugacy_classes(table):
        if cls.isdisjoint(p_k):
            freedom.append(cls)
        elif not cls <= p_k:
            straddler = sorted(cls - p_k)[0]
            raise AssertionError(
                f"conjugacy class straddles P_K (P_K not saturated?): "
                f"pair {straddler} outside, class of {sorted(cls)[0]}")

    # Paper Prop 3.1, the always-on law: P_max \ P_min = P_K^c, and the freedom
    # classes tile that set disjointly. A violation is an upstream bug.
    band = difference(table, p_max, p_min)
    p_k_c = complement(table, p_k)
    if band != p_k_c:
        raise AssertionError(
            f"Prop 3.1 violated: P_max \\ P_min != P_K^c at pair "
            f"{sorted(band ^ p_k_c)[0]}")
    covered: FrozenSet[Tuple[int, int]] = frozenset().union(*freedom) if freedom else frozenset()
    if covered != p_k_c or sum(len(c) for c in freedom) != len(p_k_c):
        raise AssertionError(
            f"Prop 3.1 violated: freedom classes do not tile P_K^c "
            f"(covered {len(covered)}, tiled {sum(len(c) for c in freedom)}, "
            f"expected {len(p_k_c)})")

    return Interval(table=table, p_neg_phi=p_neg_phi, p_k=p_k,
                    p_min=p_min, p_max=p_max, freedom=tuple(freedom))


# --- the endpoint decisions --------------------------------------------------


def k_settles_phi(iv: Interval) -> Tuple[bool, Optional[Witness]]:
    """Does `K` settle `phi` — is `L(P_min) = L(neg_phi) & L(K)` empty? True
    means `K |= phi`, done, no model checker. On False the witness is the
    minimal lasso `K` leaves open, i.e. in `L(neg_phi) & L(K)`."""
    empty, wit = is_empty(iv.table, iv.p_min)
    if empty:
        return True, None
    assert wit is not None
    return False, replace(wit, operation="k_settles_phi")


def k_refutes_phi(iv: Interval) -> Tuple[bool, Optional[Witness]]:
    """Does `K` refute `phi` — is `L(P_max)` universal? Decided as emptiness
    of the complement (the paper's symmetry with `k_settles_phi`; there is no
    separate universality scan). True means `K |= not phi`: every run of a
    nonempty system is a counterexample. On False the witness is the minimal
    lasso in `L(phi) & L(K)`."""
    empty, wit = is_empty(iv.table, complement(iv.table, iv.p_max))
    if empty:
        return True, None
    assert wit is not None
    return False, replace(wit, operation="k_refutes_phi")


# --- the choice API ----------------------------------------------------------


def choose(iv: Interval, chosen: Iterable[int], check: bool = True) -> PairSet:
    """The legal `B` selected by turning on the freedom classes at the given
    indices: `P_min | union(freedom[i])`. Saturated and inside the interval by
    Prop 3.1; `check=True` (the default — harness runs checked) asserts both,
    campaigns may pass `check=False`."""
    out = iv.p_min
    for i in chosen:
        out = union(iv.table, out, iv.freedom[i])
    if check:
        assert is_saturated(iv.table, out), "choose: result not saturated"
        assert iv.p_min <= out <= iv.p_max, "choose: result left the interval"
    return out


def decompose(iv: Interval, q: PairSet) -> Optional[FrozenSet[int]]:
    """The inverse of `choose`: the freedom-index set of a legal `q`, or
    `None` when `q` is not in the interval (not saturated, or outside
    `[P_min, P_max]`). Each freedom class is all-in or all-out of a legal `q`
    — asserted, a straddle would convict Prop 3.1."""
    if not (iv.p_min <= q <= iv.p_max) or not is_saturated(iv.table, q):
        return None
    rest = difference(iv.table, q, iv.p_min)
    indices: List[int] = []
    for i, cls in enumerate(iv.freedom):
        hit = intersection(iv.table, cls, rest)
        if hit:
            assert hit == cls, f"freedom class {i} straddles a legal choice"
            indices.append(i)
            rest = difference(iv.table, rest, cls)
    assert not rest, f"legal choice not tiled by freedom classes: {sorted(rest)}"
    return frozenset(indices)
