"""sos2ltl_pairs recipe — the cascade-delegated sos2ltl under the
acceptance-pair decomposition, under `hi`.

`sos2ltl_casc` wrapped in `PairSplit` (`aut2ltl/sos2ltl/pairsplit/`): the
translation splits per acceptance pair over the deterministic generic body —
complementing first when the dual side splits thinner — and ORs the piece
labels; pass-through where no side splits. Targets the conjunctive-recurrence
stratum (`GFa ∧ GFb` and friends). The one `hi` simplification sits outside
the whole, at the recipe boundary.
"""
from __future__ import annotations

from typing import Optional

from aut2ltl.options import Options
from aut2ltl.simplify_ltl import Simplify
from aut2ltl.translator import Translator


def sos2ltl_pairs_recipe(options: Optional[Options] = None) -> Translator:
    """PairSplit around the cascade-delegated sos2ltl, under a final `hi`
    simplifier (options unused)."""
    from aut2ltl.sos2ltl.translator import sos2ltl_casc
    from aut2ltl.sos2ltl.pairsplit import PairSplit
    return Simplify(PairSplit(sos2ltl_casc), "hi")


__all__ = ["sos2ltl_pairs_recipe"]
