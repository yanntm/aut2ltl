"""`Language` → `sosl.sos.Invariant` — the reference construction adapter.

The only Spot-adjacent module of the package: pull the Language's minimal
deterministic generic form, normalize it to the construction's canonical
form D, and run the reference pipeline (`sosl.sos.core.quotient`). A blown
monoid-closure cap raises `BridgeDecline` — a decline, never a verdict.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sosl.sos import Invariant
from sosl.sos.build import canonical
from sosl.sos.core.quotient import invariant_of

if TYPE_CHECKING:
    from aut2ltl.language import Language


class BridgeDecline(Exception):
    """The invariant could not be built within the resource cap."""


def invariant_of_language(lang: "Language", cap: int = 20000) -> Invariant:
    """The canonical invariant `𝓘(L)` of the Language. `canonical` determinizes
    and completes the Language's base automaton (Spot postprocess), and the
    reference closure builds `𝓘(L)` from that form; the invariant is a
    *language* property (byte-equal per language, [SωS26 Thm 5.1]),
    independent of which equivalent deterministic presentation seeds it.
    Raises `BridgeDecline` when the closure exceeds `cap`."""
    inv = invariant_of(canonical(lang._base()), cap)
    if inv is None:
        raise BridgeDecline(f"invariant closure exceeded cap {cap}")
    return inv
