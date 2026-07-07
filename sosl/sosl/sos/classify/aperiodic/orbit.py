"""Power orbits of the multiplication table — the aperiodicity read-off.

For a non-identity class ``c`` of an `Invariant`, the powers ``c, c², c³, …``
eventually close a cycle. The orbit records the entry exponent (index ``m``:
``c^m`` is the first power on the cycle) and the cycle length (eventual
period ``p``). The algebra is aperiodic iff every class has period 1; a class
with period > 1 carries a group, and the first such class in shortlex key
order (ascending canonical id) is the canonical group carrier. Normative
math: `research_notes/sos_classification.md` §4.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ...invariant import Invariant


@dataclass(frozen=True)
class Orbit:
    """The power orbit of one class ``cls``: ``powers[i]`` is ``cls^{i+1}``,
    listing the pairwise-distinct powers ``cls^1 .. cls^{m+p-1}``; ``index``
    is the least exponent ``m >= 1`` with ``cls^m`` on the closed cycle;
    ``period`` is the cycle length ``p >= 1``."""

    cls: int
    index: int
    period: int
    powers: Tuple[int, ...]

    @property
    def cycle(self) -> Tuple[int, ...]:
        """The closed cycle ``cls^m .. cls^{m+p-1}``."""
        return self.powers[self.index - 1:]


def orbit(inv: Invariant, c: int) -> Orbit:
    """The power orbit of class ``c`` (must not be the identity)."""
    first_exp: Dict[int, int] = {}
    powers: List[int] = []
    p: int = c
    exp: int = 1
    while p not in first_exp:
        first_exp[p] = exp
        powers.append(p)
        p = inv.mult[p][c]
        exp += 1
    m: int = first_exp[p]
    return Orbit(cls=c, index=m, period=exp - m, powers=tuple(powers))


def first_group(inv: Invariant) -> Optional[Orbit]:
    """The orbit of the first class (ascending id = shortlex key order) with
    period > 1 — the canonical group carrier — or None when every orbit has
    period 1. Classes already met as a power inside an earlier orbit are
    skipped: their powers are powers of the earlier class, so their period is
    1 whenever the scan got past it."""
    seen: set = set()
    for c in range(inv.n):
        if c == inv.identity or c in seen:
            continue
        o = orbit(inv, c)
        if o.period > 1:
            return o
        seen.update(o.powers)
    return None


def is_aperiodic(inv: Invariant) -> bool:
    """Whether the algebra is aperiodic: no power orbit of period > 1."""
    return first_group(inv) is None
