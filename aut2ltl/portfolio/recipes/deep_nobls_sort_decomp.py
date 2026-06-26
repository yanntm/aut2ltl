"""deep_nobls_sort_decomp recipe — `deep_nobls_sort` with the decomp-woven peel.

Identical to `deep_nobls_sort` but both engines use `peel_decomp` instead of `peel`:
the (de)compositions are woven into EVERY descent level (inv → strength → acc → scc
around the sorted peel), so a stem exit re-enters the full decomposition on the way
down, rather than being peeled flat. Same two-engine floor split as
`deep_nobls_sort` — forward seed `peel_decomp(bls)` (always answers), return labeler
`peel_decomp(decline)` (no cascade). The A/B against `deep_nobls_sort` measures
whether the recursive decomposition pays for itself on the survey.
"""
from __future__ import annotations

from typing import Optional

from aut2ltl.translator import Translator
from aut2ltl.options import Options
from aut2ltl.combinators.best_of import best_of
from aut2ltl.ltl_rewriter import identity, relabel, as_translator
from aut2ltl.roundtrip_deep import deep_roundtrip
from aut2ltl.simplify_ltl import Simplify
from ..builder import peel_decomp, decline, bls


def deep_nobls_sort_decomp(options: Optional[Options] = None) -> Translator:
    """Forward `peel_decomp(bls)` seeds a formula; `deep_roundtrip` re-presents every
    DAG node bottom-up via `peel_decomp(decline)` (no cascade), kept per node only when
    not larger; a final `hi` simplifier over the whole."""
    forward = Simplify(peel_decomp(bls(options)), "hi")
    represent = best_of([identity, relabel(Simplify(peel_decomp(decline), "hi"))],
                        name="deep_nobls_sort_decomp_arm")
    rewriter = deep_roundtrip(represent)
    return Simplify(as_translator(forward, rewriter), "hi")


__all__ = ["deep_nobls_sort_decomp"]
