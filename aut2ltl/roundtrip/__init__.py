"""
aut2ltl.roundtrip — the round-trip re-presentation family and its `Finder` contract.

The base `roundtrip(R, Φ)` is a Rewriter (`LTLResult → LTLResult`): locate one node
via the finder `Φ`, re-present the subformula there with the Rewriter `R`, relink in
place. See algorithm.md; the finder strategies live in `cutpoints/`.

Three further scopes live in submodules, re-exported here so callers need not know
their location: `roundtrip_decomp` (a located node's operands), `deep_roundtrip`
(the whole DAG, bottom-up), and `Roundtrip` (the Translator-level round trip).

Public entries: `roundtrip`, `roundtrip_decomp`, `deep_roundtrip`, `Roundtrip`, `Finder`.
"""

from .finder import Finder
from .roundtrip import roundtrip
from .roundtrip_decomp import roundtrip_decomp
from .roundtrip_deep import deep_roundtrip
from .roundtrip_top import Roundtrip

__all__ = ["roundtrip", "roundtrip_decomp", "deep_roundtrip", "Roundtrip", "Finder"]
