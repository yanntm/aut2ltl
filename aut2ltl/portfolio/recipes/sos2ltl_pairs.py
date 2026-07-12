"""sos2ltl_pairs recipe — sos2ltl_casc under the SoS pair decomposition,
under `hi`.

The `sos2ltl_pairs` assembly (`aut2ltl/sos2ltl/pairsplit/algorithm.md`): the
accepting pair set of the invariant — or its free complement — split into
saturation atoms over the same table where the whole-language engine
declines, pieces translated engine-then-dg, labels recombined `⋁` (outer `¬`
iff complemented); the cascade assembly unchanged everywhere else. The one
`hi` simplification sits outside the whole, at the recipe boundary.
"""
from __future__ import annotations

from typing import Optional

from aut2ltl.options import Options
from aut2ltl.simplify_ltl import Simplify
from aut2ltl.translator import Translator


def sos2ltl_pairs_recipe(options: Optional[Options] = None) -> Translator:
    """The pairsplit sos2ltl assembly under a final `hi` simplifier (options
    unused)."""
    from aut2ltl.sos2ltl.translator import sos2ltl_pairs
    return Simplify(sos2ltl_pairs, "hi")


__all__ = ["sos2ltl_pairs_recipe"]
