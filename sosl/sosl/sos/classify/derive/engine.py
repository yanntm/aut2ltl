"""The Wagner-degree derivative recursion, on the invariant's own table.

Resolves the one case the read-off leaves open — ``m >= 1 & n_plus = n_minus``
(the tied case) — per C section 8 (Theorem 4.5): the derivative ``dX`` is not
recognized by any re-marking of the accepting pairs, but on the right regular
representation it is a *restriction of the admissible stems*. Each level:

  1. **Zone.** From the current level's maximal superchain tops, keep the
     elements that still reach a maximal top of *both* signs in their right
     ideal: ``B = T+ ∩ T-``, a union of R-classes (C Cor. 8.3). Everything
     else is collapsed into two virtual sinks — one accepting, one rejecting,
     each reachable from every kept stem, absorbing.
  2. **Re-run the engines restricted to ``B``**, the marking unchanged. Each
     sink contributes a length-0 chain of its sign and nothing longer, so
     ``m'± = max(0, restricted m±)``. When ``m' >= 1`` the sinks carry no
     maximal chain and ``n'± `` are the restricted numbers; when ``m' = 0``
     every descent may end with one virtual stem of the opposite sign and a
     bare sink floors both signs, so ``n'± = max(0, restricted n± + 1)``.
  3. **Read off** the level's ``mu``; the trace ``mu_0, mu_1, ...`` sums (CNF
     ordinal addition) to ``gamma``, the recursion's Cantor normal form, and
     the first untied level supplies the sign. ``m`` strictly decreases
     (asserted), so at most ``m(X)`` levels run.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, List, Tuple

from ...invariant import Invariant
from ..chains import ChainResult, chains
from ..primitives import Green
from ..readoff import ReadOff, read_off
from ..readoff.ordinal import Ordinal
from ..superchains import SuperchainResult, superchains


@dataclass(frozen=True)
class Level:
    """One derivation level: the four integers the restricted engines returned
    (sink contributions folded in), the level's ``mu`` term, and the stems the
    level's engines ran on (empty at the deepest collapse)."""

    m_plus: int
    m_minus: int
    n_plus: int
    n_minus: int
    mu: Ordinal
    kept: Tuple[int, ...]


@dataclass(frozen=True)
class DeriveResult:
    """The resolved degree tail: ``gamma`` (the CNF sum of the level ``mu``
    terms, level 0 included), the sign read at the last level, and the level
    trace (level 0 = the unrestricted read-off, then one entry per
    derivation)."""

    gamma: Ordinal
    sign: str
    trace: Tuple[Level, ...]


def _kept(g: Green, sr: SuperchainResult,
          within: FrozenSet[int]) -> FrozenSet[int]:
    """The stems of ``within`` whose right ideal still reaches a maximal
    superchain top of **both** signs — ``B = T+ ∩ T-`` restricted to the word
    classes, a union of R-classes (R-equivalent elements share their right
    ideal)."""
    return frozenset(
        t for t in within
        if any(g.leq_r(s, t) for s in sr.tops_plus)
        and any(g.leq_r(s, t) for s in sr.tops_minus))


def derive(inv: Invariant, cr: ChainResult, sr: SuperchainResult,
           ro: ReadOff) -> DeriveResult:
    """Run the derivative recursion from an unrestricted classification —
    the chain result ``cr``, superchain result ``sr``, and read-off ``ro``
    (which must have ``needs_derivative``). Every step is a table search; no
    automaton is built."""
    assert ro.needs_derivative, "derive() is only for the tied case"
    g = Green.of(inv)
    stems = frozenset(s for s in range(inv.n) if s != inv.identity)
    trace: List[Level] = [Level(
        m_plus=cr.m_plus, m_minus=cr.m_minus,
        n_plus=sr.n_plus, n_minus=sr.n_minus,
        mu=ro.mu, kept=tuple(sorted(stems)))]
    gamma = ro.mu
    m_prev = ro.m

    while True:
        stems = _kept(g, sr, stems)
        rcr = chains(inv, stems=stems)
        rsr = superchains(inv, rcr)
        m_plus = max(0, rcr.m_plus)           # the accepting sink's 0-chain
        m_minus = max(0, rcr.m_minus)         # the rejecting sink's 0-chain
        if max(m_plus, m_minus) == 0:
            # Sinks join the superchain search: one opposite-sign virtual stem
            # may end any descent, and a bare sink floors each sign at 0.
            n_plus = max(0, rsr.n_plus + 1)
            n_minus = max(0, rsr.n_minus + 1)
        else:
            n_plus, n_minus = rsr.n_plus, rsr.n_minus
        level = read_off(m_plus, m_minus, n_plus, n_minus)
        assert level.m < m_prev, (level.m, m_prev)
        m_prev = level.m
        gamma = gamma + level.mu
        trace.append(Level(m_plus=m_plus, m_minus=m_minus,
                           n_plus=n_plus, n_minus=n_minus,
                           mu=level.mu, kept=tuple(sorted(stems))))
        if not level.needs_derivative:
            return DeriveResult(gamma=gamma, sign=level.sign,
                                trace=tuple(trace))
        sr = rsr
