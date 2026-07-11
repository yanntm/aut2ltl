"""The entropy ``h(L) = log2 rho(A)`` as a certified enclosure.

``A`` is the letter-count matrix on the live classes of an invariant:
``Live`` is the calculus liveness scan (classes with a nonempty
residual) and ``A[c][c'] = |{a in Sigma : M(c, lambda(a)) = c'}|``,
restricted to ``Live x Live``. ``rho(A)`` is bracketed exactly over
`fractions.Fraction`, per irreducible diagonal block of the live
subgraph (``rho(A) = max_B rho(A_B)``; a flat Collatz-Wielandt loop
never tightens on a reducible matrix). The only float is the final
``log2``, widened one ulp outward on each side; the result carries a
replayable rational certificate (live set, blocks, per-block bracket).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, FrozenSet, List, Optional, Tuple

from ..sos.calculus import Table, live
from ..sos.invariant import Invariant
from .kernel import _sccs

WIDTH_TARGET: Fraction = Fraction(1, 10**9)
MAX_ITERATIONS: int = 10_000
SCALE: int = 10**40


@dataclass(frozen=True)
class BlockBracket:
    """A certified rational enclosure ``lo <= rho(A_B) <= hi`` for one
    irreducible diagonal block ``B`` of the live letter-count matrix."""

    classes: Tuple[int, ...]
    lo: Fraction
    hi: Fraction
    iterations: int
    converged: bool


@dataclass(frozen=True)
class EntropyResult:
    """The entropy enclosure of one language: an exact rational bracket
    ``[rho_lo, rho_hi]`` on the spectral radius of its live letter-count
    matrix, the float bracket ``[h_lo, h_hi]`` on ``log2`` of it, and
    the certificate (live set + per-block brackets) that replays the
    rational part with no floats."""

    live: FrozenSet[int]
    blocks: Tuple[BlockBracket, ...]
    rho_lo: Fraction
    rho_hi: Fraction
    h_lo: float
    h_hi: float

    @property
    def converged(self) -> bool:
        """True iff every block bracket closed under the width target."""
        return all(b.converged for b in self.blocks)


def live_classes(inv: Invariant) -> FrozenSet[int]:
    """The live classes of the invariant: the calculus liveness scan of
    its pair set on its own table (a class is live iff some right
    multiple is the stem of an accepted pair)."""
    return live(Table.of(inv), inv.accept)


def letter_counts(
    inv: Invariant, alive: FrozenSet[int]
) -> Dict[int, Dict[int, int]]:
    """The letter-count matrix restricted to ``alive x alive``, sparse:
    ``counts[c][c'] = |{a : M(c, lambda(a)) = c'}|`` for ``c, c'`` in
    ``alive``, zero entries absent. One row per live class."""
    counts: Dict[int, Dict[int, int]] = {c: {} for c in alive}
    for c in alive:
        row = counts[c]
        for x in inv.letter_class:  # one entry per letter, duplicates kept
            d = inv.mult[c][x]
            if d in counts:
                row[d] = row.get(d, 0) + 1
    return counts


def _cw_bracket(mat: List[List[int]]) -> Tuple[Fraction, Fraction, int, bool]:
    """A Collatz-Wielandt enclosure of ``rho(mat)`` for an irreducible
    nonnegative integer matrix: power-iterate ``B' = I + mat`` (primitive,
    ``rho(mat) = rho(B') - 1``) and intersect the per-step brackets
    ``[min_j (B'v)_j/v_j, max_j (B'v)_j/v_j]`` — valid for every strictly
    positive ``v``, so soundness never depends on convergence. ``v`` is
    kept in fixed point (positive integer numerators over the common
    denominator `SCALE`); rounding only slows the geometric contraction.
    Returns ``(lo, hi, iterations, converged)``."""
    k = len(mat)
    bp = [[mat[i][j] + (1 if i == j else 0) for j in range(k)] for i in range(k)]
    num: List[int] = [SCALE] * k
    lo = Fraction(0)
    hi: Optional[Fraction] = None
    for it in range(1, MAX_ITERATIONS + 1):
        w = [sum(bp[i][j] * num[j] for j in range(k)) for i in range(k)]
        ratios = [Fraction(w[i], num[i]) for i in range(k)]
        lo = max(lo, min(ratios))
        hi = max(ratios) if hi is None else min(hi, max(ratios))
        if hi - lo < WIDTH_TARGET:
            return lo - 1, hi - 1, it, True
        top = max(w)
        num = [max(1, x * SCALE // top) for x in w]
    assert hi is not None
    return lo - 1, hi - 1, MAX_ITERATIONS, False


def _log2_out(x: Fraction, toward: float) -> float:
    """``log2(x)`` as a float pushed one ulp toward ``toward`` — the
    package's only float step. ``x`` must be positive."""
    return math.nextafter(math.log2(float(x)), toward)


def entropy(inv: Invariant) -> EntropyResult:
    """The certified entropy enclosure of the invariant's language:
    ``h = 0`` exactly (width 0) on the empty language; otherwise the
    live subgraph is SCC-condensed and ``rho(A) = max_B rho(A_B)`` is
    bracketed per irreducible block — singletons exactly, nontrivial
    blocks by `_cw_bracket`. Blocks are listed sorted by least class.
    Asserts at least one cyclic block on a nonempty language (every
    live class has a live letter-successor)."""
    alive = live_classes(inv)
    if not alive:
        return EntropyResult(
            live=alive, blocks=(), rho_lo=Fraction(0), rho_hi=Fraction(0),
            h_lo=0.0, h_hi=0.0,
        )
    counts = letter_counts(inv, alive)
    succs: Dict[int, List[int]] = {c: sorted(counts[c]) for c in sorted(alive)}
    blocks: List[BlockBracket] = []
    for comp in _sccs(succs):
        if len(comp) == 1:
            c = comp[0]
            loops = counts[c].get(c, 0)
            if loops == 0:
                continue  # nilpotent singleton: rho 0, no bracket needed
            f = Fraction(loops)
            blocks.append(BlockBracket((c,), f, f, 0, True))
        else:
            order = sorted(comp)
            mat = [[counts[a].get(b, 0) for b in order] for a in order]
            lo, hi, iterations, converged = _cw_bracket(mat)
            blocks.append(BlockBracket(tuple(order), lo, hi, iterations, converged))
    assert blocks, (
        f"nonempty language with an acyclic live subgraph — the liveness "
        f"scan is convicted (n={inv.n}, |live|={len(alive)})"
    )
    rho_lo = max(b.lo for b in blocks)
    rho_hi = max(b.hi for b in blocks)
    assert rho_lo >= 0 and rho_hi >= rho_lo
    blocks.sort(key=lambda b: b.classes)
    h_lo = _log2_out(rho_lo, -math.inf) if rho_lo > 0 else -math.inf
    h_hi = _log2_out(rho_hi, math.inf) if rho_hi > 0 else -math.inf
    return EntropyResult(
        live=alive, blocks=tuple(blocks), rho_lo=rho_lo, rho_hi=rho_hi,
        h_lo=h_lo, h_hi=h_hi,
    )
