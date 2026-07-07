"""The flat classification record and its assembly from one `Invariant`.

``classify`` runs the band engines — aperiodicity (C section 4), chains
(C section 5), superchains (C section 6) — and the C section 7-8 read-off, then
packages every coordinate, the rung table, the Wagner data, and the witnesses
into one flat `Record`. The always-on internal laws of the soundness harness
(spec section 4.1) are asserted during assembly: the chain/superchain bounds,
``n>=1 => m_plus=m_minus``, and a self-replay of each chain witness against
``Invariant.member`` (an `AssertionError` here is the tool's exit-code-4 case).

The derivative recursion (C section 8, ``m>=1 & n_plus=n_minus``) is not done
here: such a record carries ``gamma_partial`` with ``gamma=None`` and
``sign="PARTIAL"`` until the degree assembly resolves it from a presentation.
Normative math: `research_notes/sos_classification.md`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from ..invariant import Invariant
from .aperiodic import first_group
from .chains import ChainResult, chains
from .readoff import Ordinal, ReadOff, Rungs, read_off
from .superchains import SuperchainResult, superchains
from .witness import chain_lassos, chain_witness, group_witness, superchain_witness


@dataclass(frozen=True)
class Record:
    """The complete classification of one language's invariant. ``gamma`` is
    ``None`` exactly when ``gamma_partial`` (the derivative case, unresolved);
    ``phi`` pairs the degree with the sign."""

    aperiodic: bool
    m_plus: int
    m_minus: int
    n_plus: int
    n_minus: int
    rungs: Rungs
    boolean_level: Optional[int]
    parity_length: int
    co_parity_length: int
    mu: Ordinal
    sign: str
    gamma: Optional[Ordinal]
    gamma_partial: bool
    witnesses: Dict

    @property
    def phi(self) -> Tuple[str, str]:
        """The Wagner degree ``(gamma, sign)`` as strings; ``gamma`` shows
        ``PARTIAL(mu)`` when unresolved."""
        g = str(self.gamma) if self.gamma is not None else f"PARTIAL({self.mu})"
        return (g, self.sign)


def _assert_internal_laws(cr: ChainResult, sr: SuperchainResult) -> None:
    """The free, always-on laws of spec section 4.1 ([CP97 Props. 6, 10])."""
    assert cr.m_plus >= -1 and cr.m_minus >= -1, (cr.m_plus, cr.m_minus)
    assert abs(cr.m_plus - cr.m_minus) <= 1, (cr.m_plus, cr.m_minus)
    assert abs(sr.n_plus - sr.n_minus) <= 1, (sr.n_plus, sr.n_minus)
    if max(sr.n_plus, sr.n_minus) >= 1:
        assert cr.m_plus == cr.m_minus, (cr.m_plus, cr.m_minus)


def _assert_witness_replay(inv: Invariant, cr: ChainResult) -> None:
    """Each chain witness lasso, folded by ``Invariant.member``, matches its
    expected bit — the algebraic verdict tied back to concrete words."""
    for ch in (cr.witness_plus, cr.witness_minus):
        if ch is None:
            continue
        for la, bit in zip(chain_lassos(inv, ch), ch.bits):
            assert inv.member(la) == bit, (ch.stem, la, bit)


def classify(inv: Invariant) -> Record:
    """The full non-derived classification record of ``inv``. Raises
    ``AssertionError`` if an internal law or a witness replay fails."""
    orbit = first_group(inv)
    cr = chains(inv)
    sr = superchains(inv, cr)
    _assert_internal_laws(cr, sr)
    _assert_witness_replay(inv, cr)

    ro: ReadOff = read_off(cr.m_plus, cr.m_minus, sr.n_plus, sr.n_minus)

    witnesses: Dict = {}
    if orbit is not None:
        witnesses["group"] = group_witness(inv, orbit)
    if cr.witness_plus is not None:
        witnesses["chain_plus"] = chain_witness(inv, cr.witness_plus)
    if cr.witness_minus is not None:
        witnesses["chain_minus"] = chain_witness(inv, cr.witness_minus)
    if sr.witness_plus is not None:
        witnesses["superchain_plus"] = superchain_witness(inv, sr.witness_plus)
    if sr.witness_minus is not None:
        witnesses["superchain_minus"] = superchain_witness(inv, sr.witness_minus)

    return Record(
        aperiodic=(orbit is None),
        m_plus=cr.m_plus, m_minus=cr.m_minus,
        n_plus=sr.n_plus, n_minus=sr.n_minus,
        rungs=ro.rungs, boolean_level=ro.boolean_level,
        parity_length=ro.parity_length, co_parity_length=ro.co_parity_length,
        mu=ro.mu, sign=ro.sign, gamma=ro.gamma,
        gamma_partial=ro.needs_derivative, witnesses=witnesses,
    )
