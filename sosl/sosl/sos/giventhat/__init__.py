"""giventhat — the interval of legal choices given prior knowledge.

Re-exports; see README.md / algorithm.md.
"""
from .interval import (
    ConjClass,
    Interval,
    choose,
    decompose,
    given_that,
    k_refutes_phi,
    k_settles_phi,
)

__all__ = [
    "ConjClass",
    "Interval",
    "given_that",
    "k_settles_phi",
    "k_refutes_phi",
    "choose",
    "decompose",
]
