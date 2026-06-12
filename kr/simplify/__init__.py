"""
kr/simplify — generic LTL simplification rules over spot.formula DAGs.

Independent of the kr/ decomposition; see README.md for the rule catalog,
lineage and soundness notes.
"""

from .context_pass import context_simplify
from .now_eval import now_rewrite


def simplify(f: "spot.formula") -> "spot.formula":
    """Combined pipeline: context pass (rule 1) with the now-evaluation
    hook (rule 2). Language-preserving."""
    return context_simplify(f, now_hook=now_rewrite)


__all__ = ["context_simplify", "now_rewrite", "simplify"]
