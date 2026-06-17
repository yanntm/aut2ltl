"""
aut2ltl.decomp.inv — the invariant-layer Translator decorator.

`Invariant(child)` factors the global safety invariant `Σ = ⋁(edge guards)` out of a
Language, delegates the simplified Language to `child`, and re-asserts `G(Σ)` on
`child`'s result. Defined entirely against the Translator contract — it imports only
the floor (`aut2ltl.language`, `aut2ltl.result`, `aut2ltl.contract`) and assumes
nothing about `child`.

Public entry: `Invariant`. See algorithm.md for the construction.
"""

from .invariant import Invariant

__all__ = ["Invariant"]
