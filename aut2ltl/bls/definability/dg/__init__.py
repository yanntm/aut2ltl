"""aut2ltl.bls.definability.dg — LTL synthesis from the syntactic ω-semigroup.

The Diekert–Gastin local-divisor construction (`algorithm.md`): consumes the
oracle's materialized quotient `S(L)₊¹` and synthesizes a defining LTL formula
on the aperiodic fragment. `morphism` freezes the algebra as the canonical
value every later stage computes over.
"""
from .morphism import Alg, build

__all__ = ["Alg", "build"]
