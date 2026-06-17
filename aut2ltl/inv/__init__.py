"""
aut2ltl.inv — the invariant-layer Translator decorator.

A sibling of the translator engines (`aut2ltl.kr`, `aut2ltl.sl`): `Invariant(child)`
factors the global safety invariant `Σ = ⋁(edge guards)` out of a Language,
delegates the simplified Language to `child`, and re-asserts `G(Σ)` on `child`'s
result. Defined entirely against the Translator contract — it imports only the
floor (`aut2ltl.language`, `aut2ltl.result`, `aut2ltl.contract`) and assumes
nothing about `child`.

Public entry: `Invariant`. See README.md for the algorithm.
"""

from .invariant import Invariant

__all__ = ["Invariant"]
