"""The superchain numbers ``(n_plus, n_minus)`` over the R-order of stems.

An X-superchain (C section 6, [CP97 Thm. 7]) is a sequence of maximal-length
chains ``C_0, ..., C_n``, alternately positive and negative, whose stems are
strictly R-descending ``s_0 >_R s_1 >_R ... >_R s_n``. Its length is ``n``;
``n_plus`` (resp. ``n_minus``) is the greatest length of one starting positive
(resp. negative), ``-1`` when none exists.

The search marks every stem carrying a maximal chain (length ``m = max(m_plus,
m_minus)``) with the sign(s) it carries — read off the chain engine's per-stem
best lengths — collapses marked stems into R-classes, and runs a longest
sign-alternating strictly-R-descending path DP over those classes, ``O(N^2)``
after the chain engine. Normative math:
`research_notes/sos_classification.md` section 6.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ...invariant import Invariant
from ..chains import ChainResult, chains
from ..primitives import Green


@dataclass(frozen=True)
class Superchain:
    """A superchain witness: ``stems`` strictly R-descending, ``signs``
    alternating with ``signs[0]`` the start sign (``True`` positive). Each stem
    carries a maximal chain of its level's sign. ``length`` is ``n``."""

    stems: Tuple[int, ...]
    signs: Tuple[bool, ...]

    @property
    def length(self) -> int:
        """``n`` — one less than the number of chains in the superchain."""
        return len(self.stems) - 1


@dataclass(frozen=True)
class SuperchainResult:
    """The superchain numbers with one maximal witness of each sign.
    ``tops_plus`` (resp. ``tops_minus``) lists every stem that tops a
    positive (negative) superchain of the maximal length ``n_plus``
    (``n_minus``) — the data the degree derivation zones from (C section 8);
    empty when that sign has no superchain."""

    n_plus: int
    n_minus: int
    witness_plus: Optional[Superchain]
    witness_minus: Optional[Superchain]
    tops_plus: Tuple[int, ...] = ()
    tops_minus: Tuple[int, ...] = ()


def superchains(inv: Invariant,
                chain_res: Optional[ChainResult] = None) -> SuperchainResult:
    """Compute ``(n_plus, n_minus)`` with a maximal witness of each sign. Reuses
    ``chain_res`` when supplied, else runs the chain engine."""
    cr = chain_res if chain_res is not None else chains(inv)
    m = max(cr.m_plus, cr.m_minus)
    if m < 0:
        return SuperchainResult(-1, -1, None, None)

    # Mark stems: sign it carries a maximal (length-m) chain of.
    carries: Dict[int, Tuple[bool, bool]] = {}
    for s, (bp, bn) in cr.stem_best.items():
        p, n = (bp == m), (bn == m)
        if p or n:
            carries[s] = (p, n)
    if not carries:
        return SuperchainResult(-1, -1, None, None)

    g = Green.of(inv)
    rclasses = g.r_classes(tuple(carries))
    reps = [rc[0] for rc in rclasses]
    # Sign availability per R-class: positive/negative carried by some member.
    avail: List[Tuple[bool, bool]] = []
    for rc in rclasses:
        p = any(carries[s][0] for s in rc)
        n = any(carries[s][1] for s in rc)
        avail.append((p, n))
    # Strict R-descent edges between R-classes (by representative).
    below: List[List[int]] = [
        [j for j in range(len(rclasses)) if g.lt_r(reps[j], reps[i])]
        for i in range(len(rclasses))
    ]

    memo: Dict[Tuple[int, bool], Tuple[int, Optional[int]]] = {}

    def dp(i: int, want_plus: bool) -> Tuple[int, Optional[int]]:
        """Longest alternating strictly-R-descending path from R-class ``i`` when
        ``i`` supplies sign ``want_plus``, as ``(node_count, next)``; ``(0, None)``
        if ``i`` does not carry that sign."""
        if not (avail[i][0] if want_plus else avail[i][1]):
            return (0, None)
        key = (i, want_plus)
        if key in memo:
            return memo[key]
        best_len, best_next = 1, None
        for j in below[i]:
            jlen, _ = dp(j, not want_plus)
            if jlen and 1 + jlen > best_len:
                best_len, best_next = 1 + jlen, j
        memo[key] = (best_len, best_next)
        return memo[key]

    def witness(start_plus: bool) -> Optional[Superchain]:
        best_len, start_i = 0, None
        for i in range(len(rclasses)):
            length = dp(i, start_plus)[0]
            if length > best_len:
                best_len, start_i = length, i
        if start_i is None:
            return None
        stems: List[int] = []
        signs: List[bool] = []
        i: Optional[int] = start_i
        want = start_plus
        while i is not None:
            stem = next(s for s in rclasses[i] if carries[s][0 if want else 1])
            stems.append(stem)
            signs.append(want)
            i = dp(i, want)[1]
            want = not want
        return Superchain(tuple(stems), tuple(signs))

    wp = witness(True)
    wn = witness(False)
    n_plus = wp.length if wp is not None else -1
    n_minus = wn.length if wn is not None else -1

    def tops(start_plus: bool, n: int) -> Tuple[int, ...]:
        """Every stem topping a maximal (length-``n``) superchain of the given
        start sign: the sign-carrying members of each R-class whose DP reaches
        the full node count."""
        if n < 0:
            return ()
        out: List[int] = []
        for i in range(len(rclasses)):
            if dp(i, start_plus)[0] == n + 1:
                out.extend(s for s in rclasses[i]
                           if carries[s][0 if start_plus else 1])
        return tuple(sorted(out))

    return SuperchainResult(n_plus=n_plus, n_minus=n_minus,
                            witness_plus=wp, witness_minus=wn,
                            tops_plus=tops(True, n_plus),
                            tops_minus=tops(False, n_minus))
