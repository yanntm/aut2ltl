"""The residual (right-congruence) automaton — an optional companion to `.sos`.

Pure data. The right congruence ``u ~ v  <=>  u^{-1}L = v^{-1}L`` of an
omega-regular language quotients to a finite deterministic automaton (the
minimal DFA of the residuals, no acceptance): states are the residual classes,
keyed by their shortlex-least reaching word (``id 0`` = ``eps``, the residual
``L`` itself), with a derivative table ``delta[r][a] = r.a``.

This is strictly weaker than the invariant `I(L)` — a right congruence, not the
two-sided syntactic one — so it is never part of an invariant's identity. It
rides along a `.sos` serialization only as an optional diagnostic trailer (see
`serialize.dump_invariant`'s ``residuals`` parameter), useful for figures; it is
computed on the automaton side (`sos.build.residuals_of_hoa`) and is absent
from a learner's export.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .alphabet import Word


@dataclass(frozen=True)
class Residuals:
    """The residual automaton of a language.

    ``keys[r]`` is the shortlex-least word reaching residual ``r`` (``keys[0]``
    is the empty word). ``delta[r][a]`` is the residual reached from ``r`` on the
    letter of mask ``a`` (columns in alphabet-mask order, ``0 .. size-1``)."""

    keys: Tuple[Word, ...]
    delta: Tuple[Tuple[int, ...], ...]

    @property
    def n(self) -> int:
        """The number of residual classes."""
        return len(self.keys)
