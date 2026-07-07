"""The idempotent set ``E`` and the H-order structure the chain search descends.

An idempotent is a non-identity class ``e`` with ``mult[e][e] == e``; the
identity is excluded throughout (linked pairs range over word classes). On
idempotents the H-order has the one-line test ``e <=_H f  <=>  e.f = f.e = e``
of `research_notes/sos_classification.md` section 2; it agrees with the
ideal-membership `Green.leq_h`, and this module offers both the direct test and
the strict descents ``f >_H g`` used to enumerate H-descending idempotent paths.
"""
from __future__ import annotations

from typing import List, Tuple

from ...invariant import Invariant


def idempotents(inv: Invariant) -> Tuple[int, ...]:
    """The idempotents of the invariant, in ascending id order: the non-identity
    classes ``e`` with ``mult[e][e] == e``."""
    mult = inv.mult
    return tuple(e for e in range(inv.n)
                 if e != inv.identity and mult[e][e] == e)


def leq_h_idem(inv: Invariant, e: int, f: int) -> bool:
    """The one-line H-order test on idempotents: ``e <=_H f`` iff
    ``e.f == f.e == e``. Valid only when both ``e`` and ``f`` are idempotent."""
    mult = inv.mult
    return mult[e][f] == e and mult[f][e] == e


def lt_h_idem(inv: Invariant, e: int, f: int) -> bool:
    """Strict ``e <_H f`` on idempotents: ``e <=_H f`` and ``e != f`` (the
    one-line test is antisymmetric on idempotents, so ``e != f`` gives
    strictness)."""
    return e != f and leq_h_idem(inv, e, f)


def h_descents(inv: Invariant, E: Tuple[int, ...]) -> Tuple[Tuple[int, ...], ...]:
    """For each idempotent ``e`` in ``E`` (indexed by position in ``E``), the
    idempotents ``g`` in ``E`` with ``e >_H g`` — the strict H-descendants,
    returned as a tuple parallel to ``E``."""
    out: List[Tuple[int, ...]] = []
    for e in E:
        out.append(tuple(g for g in E if lt_h_idem(inv, g, e)))
    return tuple(out)
