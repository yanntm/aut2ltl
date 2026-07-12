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
from .ladder import (
    RungAnswer,
    exists_cosafety,
    exists_obligation,
    exists_persistence,
    exists_recurrence,
    exists_safety,
    forced,
    h_below,
    is_persistence,
    is_recurrence,
    rec_hull,
    rung_of,
)
from .quotient import (
    Quotient,
    admits,
    congruence,
    greatest_member,
    hull,
    least_member,
    syntactic_congruence,
)
from .simplify import Options, Simplification, simplify
from .stutter import exists_stutter_invariant, sc, stutter_seeds

__all__ = [
    "ConjClass",
    "Interval",
    "given_that",
    "k_settles_phi",
    "k_refutes_phi",
    "choose",
    "decompose",
    "RungAnswer",
    "exists_safety",
    "exists_cosafety",
    "exists_obligation",
    "exists_recurrence",
    "exists_persistence",
    "forced",
    "h_below",
    "is_recurrence",
    "is_persistence",
    "rec_hull",
    "rung_of",
    "Quotient",
    "congruence",
    "syntactic_congruence",
    "hull",
    "admits",
    "least_member",
    "greatest_member",
    "stutter_seeds",
    "sc",
    "exists_stutter_invariant",
    "Options",
    "Simplification",
    "simplify",
]
