"""sos — the SoS vocabulary and services. Re-exports; see README.md / algorithm.md.

Self-contained package: data structures at the root, (de)serialization under
io/, constructors under build/. No dependency outside this package tree.
"""
from .alphabet import EMPTY, Alphabet, Letter, Word, shortlex_key
from .core.canonical import canonicalize
from .invariant import Invariant
from .io.serialize import (
    dump_invariant,
    load_invariant,
)
from .lasso import Lasso
from .residuals import Residuals

__all__ = [
    "Alphabet",
    "Letter",
    "Word",
    "EMPTY",
    "shortlex_key",
    "Lasso",
    "Invariant",
    "Residuals",
    "canonicalize",
    "dump_invariant",
    "load_invariant",
]
