"""sos2ltl_casc recipe — sos2ltl with the decomposition fallback, under `hi`.

The `sos2ltl` assembly with the per-layer KR-cascade delegate below the
engine (paper §6, `aut2ltl/sos2ltl/cascade/`): a no-width layer takes the
stem half (Prop 4.14, cascade extractor), a window-undetermined
final-candidate layer the loop half (tail-restricted acceptor, `Fin(C)`
combination); dg stays the floor when the delegate declines. The one `hi`
simplification sits outside the whole — the critical juncture; the
construction path itself never pays Spot's full simplifier.
"""
from __future__ import annotations

from typing import Optional

from aut2ltl.options import Options
from aut2ltl.simplify_ltl import Simplify
from aut2ltl.translator import Translator


def sos2ltl_casc_recipe(options: Optional[Options] = None) -> Translator:
    """The cascade-delegated sos2ltl translator under a final `hi` simplifier
    (options unused)."""
    from aut2ltl.sos2ltl.translator import sos2ltl_casc
    return Simplify(sos2ltl_casc, "hi")


__all__ = ["sos2ltl_casc_recipe"]
