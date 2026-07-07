"""The chain numbers ``(m_plus, m_minus)`` by longest-alternating-path DP.

An X-chain in normal form (C section 5, [CP97 Thm. 6]) is a stem ``s`` and a
strictly H-descending sequence of idempotents ``e0 >_H e1 >_H ... >_H em``, each
``(s, e_i)`` a linked pair, whose acceptance bits ``(s, e_i) in P`` alternate.
Its length is ``m`` (the number of alternations) and its sign is that of the
top: positive when ``(s, e0) in P``. ``m_plus`` (resp. ``m_minus``) is the
greatest length of a positive (resp. negative) chain, ``-1`` when none exists.

The search fixes a stem, restricts the idempotents to those linked to it,
and runs a longest strictly-alternating strictly-H-descending path DP over that
sub-DAG — once per admissible stem, ``O(N.|E|^2)`` overall. The per-stem best
lengths are retained so the superchain engine can mark the stems carrying a
maximal chain. Normative math: `research_notes/sos_classification.md` section 5.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ...invariant import Invariant
from ..primitives import h_descents, idempotents


@dataclass(frozen=True)
class Chain:
    """A normal-form X-chain witness: ``stem`` linked to every idempotent of
    ``idems`` (listed H-top ``e0`` first, H-bottom ``em`` last), with acceptance
    bits alternating along the descent. ``positive`` is the sign (``(stem, e0)``
    accepting); ``length`` is ``m``, the number of alternations."""

    stem: int
    idems: Tuple[int, ...]
    bits: Tuple[bool, ...]
    positive: bool

    @property
    def length(self) -> int:
        """``m`` — the number of alternations (one less than the idempotent
        count)."""
        return len(self.idems) - 1


@dataclass(frozen=True)
class ChainResult:
    """The chain numbers of an invariant with one maximal witness of each sign,
    plus, per stem, the best positive/negative chain length carried there
    (``-1`` for a sign the stem carries no chain of) — the input the superchain
    engine marks stems from."""

    m_plus: int
    m_minus: int
    witness_plus: Optional[Chain]
    witness_minus: Optional[Chain]
    stem_best: Dict[int, Tuple[int, int]]


def _best_from(e: int, desc: Dict[int, List[int]], bit: Dict[int, bool],
               memo: Dict[int, Tuple[int, Optional[int]]]) -> Tuple[int, Optional[int]]:
    """Longest alternating H-descending path starting at idempotent ``e``, as
    ``(node_count, next)`` where ``next`` is the chosen H-successor or ``None``.
    Memoised over the strict-``>_H`` DAG."""
    if e in memo:
        return memo[e]
    best_len, best_next = 1, None
    for g in desc[e]:
        if bit[g] != bit[e]:
            glen, _ = _best_from(g, desc, bit, memo)
            if 1 + glen > best_len:
                best_len, best_next = 1 + glen, g
    memo[e] = (best_len, best_next)
    return memo[e]


def _reconstruct(top: int, desc: Dict[int, List[int]], bit: Dict[int, bool],
                 memo: Dict[int, Tuple[int, Optional[int]]]) -> Tuple[List[int], List[bool]]:
    """Walk the memoised ``next`` pointers from ``top`` to read off the idempotent
    path and its acceptance bits."""
    idems: List[int] = []
    bits: List[bool] = []
    cur: Optional[int] = top
    while cur is not None:
        idems.append(cur)
        bits.append(bit[cur])
        cur = memo[cur][1]
    return idems, bits


def chains(inv: Invariant) -> ChainResult:
    """Compute ``(m_plus, m_minus)`` with a maximal witness of each sign and the
    per-stem best lengths."""
    E = idempotents(inv)
    desc_all = dict(zip(E, h_descents(inv, E)))
    mult, accept = inv.mult, inv.accept

    m_plus, m_minus = -1, -1
    w_plus: Optional[Chain] = None
    w_minus: Optional[Chain] = None
    stem_best: Dict[int, Tuple[int, int]] = {}

    for s in range(inv.n):
        if s == inv.identity:
            continue
        linked = [e for e in E if mult[s][e] == s]
        if not linked:
            continue
        linked_set = set(linked)
        bit = {e: (s, e) in accept for e in linked}
        desc = {e: [g for g in desc_all[e] if g in linked_set] for e in linked}
        memo: Dict[int, Tuple[int, Optional[int]]] = {}

        best_p, best_n = -1, -1
        top_p: Optional[int] = None
        top_n: Optional[int] = None
        for e in linked:
            length = _best_from(e, desc, bit, memo)[0] - 1
            if bit[e]:
                if length > best_p:
                    best_p, top_p = length, e
            else:
                if length > best_n:
                    best_n, top_n = length, e
        stem_best[s] = (best_p, best_n)

        if best_p > m_plus:
            idems, bits = _reconstruct(top_p, desc, bit, memo)  # type: ignore[arg-type]
            m_plus = best_p
            w_plus = Chain(stem=s, idems=tuple(idems), bits=tuple(bits), positive=True)
        if best_n > m_minus:
            idems, bits = _reconstruct(top_n, desc, bit, memo)  # type: ignore[arg-type]
            m_minus = best_n
            w_minus = Chain(stem=s, idems=tuple(idems), bits=tuple(bits), positive=False)

    return ChainResult(m_plus=m_plus, m_minus=m_minus,
                       witness_plus=w_plus, witness_minus=w_minus,
                       stem_best=stem_best)
