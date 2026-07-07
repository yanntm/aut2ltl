"""sos2ltl recipe — the syntactic ω-semigroup translator under a hi simplifier.

The single-engine assembly of `aut2ltl/sos2ltl/`: bridge to the canonical
invariant, certificate-or-formula (transcription engine behind its
conformance gate, dg local-divisor fallback). One `hi` simplification sits
outside the whole (our DAG rules then Spot's LTL simplifier, size-gated); a
declined / NOT_LTL result and the engine's technique tags pass through
unchanged.
"""
from __future__ import annotations

from typing import Optional

from aut2ltl.options import Options
from aut2ltl.simplify_ltl import Simplify
from aut2ltl.translator import Translator


def sos2ltl_recipe(options: Optional[Options] = None) -> Translator:
    """The sos2ltl translator under a final `hi` simplifier (options unused)."""
    from aut2ltl.sos2ltl.translator import sos2ltl
    return Simplify(sos2ltl, "hi")


__all__ = ["sos2ltl_recipe"]
