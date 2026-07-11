"""Symmetries of a language read off its canonical invariant — see README.md
and algorithm.md in this folder."""
from .relations import (
    independence,
    independence_letters,
    invisible_letters,
    is_closed,
    ladder_entry,
    stutter_rung,
    word_class,
)
from .sigma import (
    SignedPerm,
    all_b_ap,
    anti_possible,
    apply_perm,
    generators_b_ap,
    in_kernel,
    inert_aps,
    is_antisymmetry,
    is_symmetry,
)

__all__ = [
    "SignedPerm",
    "all_b_ap",
    "anti_possible",
    "apply_perm",
    "generators_b_ap",
    "in_kernel",
    "inert_aps",
    "is_antisymmetry",
    "is_symmetry",
    # SY3 — relational read-offs
    "word_class",
    "is_closed",
    "invisible_letters",
    "stutter_rung",
    "ladder_entry",
    "independence",
    "independence_letters",
]
