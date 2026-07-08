"""core — the canonical construction of the syntactic omega-semigroup.

The clean implementation of the paper (``research_notes/sos_constructed.md``):
from a deterministic complete Emerson-Lei automaton ``D`` to the canonical
invariant ``I(L)`` of its language. Self-contained over spot and the ``sos``
data structures — no dependency on ``aut2ltl``. See ``algorithm.md``.
"""
from .canonical import canonicalize, shortlex_bfs
from .closure import Monoid, close
from .congruence import Profile, profile, refine, residual_classes
from .enriched import Elem, compose, identity_elem, letter_elems
from .quotient import SosData, freeze, invariant_of, pipeline

__all__ = [
    "Elem",
    "identity_elem",
    "compose",
    "letter_elems",
    "Monoid",
    "close",
    "Profile",
    "profile",
    "refine",
    "residual_classes",
    "SosData",
    "pipeline",
    "freeze",
    "invariant_of",
    "canonicalize",
    "shortlex_bfs",
]
