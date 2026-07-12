"""calculus — align, operate, reduce over the syntactic omega-semigroup.

Pure functions over `sosl.sos` objects: a `Table` (one algebra) hosts many pair
sets (its languages), `surgery` moves between them for free, `align` puts two
languages over different algebras on a common node set, `decide` answers by
scanning cells and always ships a `Witness`, and `reduce` returns the canonical
`Invariant`. Re-exports; see README.md / algorithm.md.
"""
from .align import Aligned, align
from .decide import (
    Decision,
    byte_equivalent,
    equivalent,
    included,
    intersecting_word,
    is_empty,
    is_universal,
    member,
)
from .product import Product, materialize, product
from .reduce import reduce, reduced_invariant, syntactic_blocks
from .surgery import (
    complement,
    difference,
    empty,
    interior,
    intersection,
    inverse_substitution,
    is_cosafety,
    is_obligation,
    is_safety,
    is_saturated,
    live,
    liveness_part,
    obligation_degree,
    pair_language,
    residual_count,
    rooting,
    safety_closure,
    saturate,
    union,
    universal,
    xor,
)
from .table import Cell, FoldedLanguage, Language, PairSet, Table, cells_in_order
from .witness import Oracle, Witness

__all__ = [
    "Table",
    "PairSet",
    "Cell",
    "Language",
    "FoldedLanguage",
    "cells_in_order",
    "Aligned",
    "align",
    "Product",
    "product",
    "materialize",
    "Witness",
    "Oracle",
    "Decision",
    "member",
    "is_empty",
    "is_universal",
    "included",
    "equivalent",
    "intersecting_word",
    "byte_equivalent",
    "empty",
    "universal",
    "complement",
    "union",
    "intersection",
    "difference",
    "xor",
    "rooting",
    "residual_count",
    "saturate",
    "is_saturated",
    "pair_language",
    "inverse_substitution",
    "live",
    "safety_closure",
    "interior",
    "liveness_part",
    "is_safety",
    "is_cosafety",
    "is_obligation",
    "obligation_degree",
    "reduce",
    "reduced_invariant",
    "syntactic_blocks",
]
