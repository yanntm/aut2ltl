"""The ladder rungs, index lengths, and Wagner data as functions of the four
chain/superchain integers.

Every verdict of C section 7 and the non-derived part of C section 8 is
arithmetic on ``(m_plus, m_minus, n_plus, n_minus)``:

  - rungs: open ``m=0 & n_plus<=0``, closed ``m=0 & n_minus<=0``, weak ``m=0``,
    dba ``m_plus<=0``, dca ``m_minus<=0`` (the C section 7 table);
  - parity length ``m_plus+1``, co-parity length ``m_minus+1``, boolean level
    ``min(n_plus, n_minus)+1`` (the least indices meeting the table's
    inequalities), the boolean level reported only when weak;
  - ``mu = n`` when ``m=0`` and the superchain signs differ, else
    ``omega^m * (n+1)``; sign ``sigma / pi / delta`` from the superchain
    comparison; and ``gamma = mu`` whenever ``m=0`` or ``n_plus != n_minus``.

The one case left open here is ``m>=1 & n_plus=n_minus``: sign and ``gamma``
then need the derivative language (C section 8), signalled by
``needs_derivative`` with ``sign="PARTIAL"`` and ``gamma=None``. Normative math:
`research_notes/sos_classification.md` sections 7-8.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .ordinal import Ordinal

SIGMA, PI, DELTA, PARTIAL = "sigma", "pi", "delta", "PARTIAL"


@dataclass(frozen=True)
class Rungs:
    """The safety-progress / topological rung membership of C section 7."""

    open: bool
    closed: bool
    weak: bool
    dba: bool
    dca: bool


@dataclass(frozen=True)
class ReadOff:
    """The full C section 7-8 read-off of one ``(m_plus, m_minus, n_plus,
    n_minus)`` tuple. ``sign`` is ``PARTIAL`` and ``gamma`` is ``None`` exactly
    when ``needs_derivative`` — the ``m>=1 & n_plus=n_minus`` case the degree
    recursion resolves."""

    m: int
    n: int
    rungs: Rungs
    boolean_level: Optional[int]
    parity_length: int
    co_parity_length: int
    mu: Ordinal
    sign: str
    gamma: Optional[Ordinal]
    needs_derivative: bool


def in_gen_buchi_spectrum(m_plus: int, m_minus: int,
                          n_plus: int, n_minus: int) -> bool:
    """The generalized-Büchi degree spectrum of C section 11 (Prop. 11.1): a
    language recognized by a deterministic complete ``⋀ Inf`` automaton has
    ``m_plus <= 0`` and Wagner degree in
    ``{(0,σ),(0,π)} ∪ {(n,s):1<=n<ω} ∪ {(ω,σ)}`` — never the derivative regime.
    In the four integers that is ``m_plus <= 0`` together with either a weak
    body (``m_minus <= 0``, the trivial and boolean levels) or the single
    properly-``Gδ`` shape ``m_minus = 1, (n_plus, n_minus) = (-1, 0)``. A
    generalized-Büchi input classified outside this set is a bug in the
    classifier or in the corpus's acceptance labeling (spec harness 4.6)."""
    if m_plus > 0:
        return False
    if m_minus <= 0:
        return True
    return m_minus == 1 and n_plus == -1 and n_minus == 0


def read_off(m_plus: int, m_minus: int, n_plus: int, n_minus: int) -> ReadOff:
    """Assemble the C section 7-8 read-off from the four chain/superchain
    integers (each ``>= -1``, ``-1`` meaning 'none')."""
    m = max(m_plus, m_minus)
    n = max(n_plus, n_minus)

    rungs = Rungs(
        open=(m == 0 and n_plus <= 0),
        closed=(m == 0 and n_minus <= 0),
        weak=(m == 0),
        dba=(m_plus <= 0),
        dca=(m_minus <= 0),
    )
    boolean_level = (min(n_plus, n_minus) + 1) if m == 0 else None
    parity_length = m_plus + 1
    co_parity_length = m_minus + 1

    if m == 0 and n_plus != n_minus:
        mu = Ordinal.finite(n)
    else:
        mu = Ordinal.term(m, n + 1)

    needs_derivative = (m >= 1 and n_plus == n_minus)
    if n_minus > n_plus:
        sign = SIGMA
    elif n_minus < n_plus:
        sign = PI
    elif m == 0:
        sign = DELTA
    else:
        sign = PARTIAL

    gamma: Optional[Ordinal] = None if needs_derivative else mu
    return ReadOff(m=m, n=n, rungs=rungs, boolean_level=boolean_level,
                   parity_length=parity_length, co_parity_length=co_parity_length,
                   mu=mu, sign=sign, gamma=gamma, needs_derivative=needs_derivative)
