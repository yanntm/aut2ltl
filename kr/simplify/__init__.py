"""
kr/simplify — generic LTL simplification rules over spot.formula DAGs.

Independent of the kr/ decomposition; see README.md for the rule catalog,
lineage and soundness notes.
"""

from .context_pass import context_simplify
from .now_eval import now_rewrite, prop_minimize
from .factor_pass import factor_simplify


def simplify(f: "spot.formula") -> "spot.formula":
    """Combined pipeline: context pass (rule 1) with the now-evaluation
    hook (rule 2), then partial factoring (rule 3); one more context pass
    when factoring changed something (composites can expose new
    absorptions). Language-preserving."""
    g = context_simplify(f, now_hook=now_rewrite)
    h = factor_simplify(g)
    if h != g:
        h = context_simplify(h, now_hook=now_rewrite)
    return h


__all__ = ["context_simplify", "now_rewrite", "prop_minimize",
           "factor_simplify", "simplify"]
