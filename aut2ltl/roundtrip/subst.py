"""aut2ltl/roundtrip/subst.py — subtree substitution on an LTL formula DAG.

The `φ[n ↦ ψ]` primitive of algorithm.md. Generic over the formula DAG; kept local
for now, a candidate to move to `aut2ltl/ltl` if it proves reusable elsewhere.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import spot


def substitute(formula: "spot.formula", node: "spot.formula",
               repl: "spot.formula") -> "spot.formula":
    """`φ[node ↦ repl]`: `formula` with every occurrence of the subformula `node`
    replaced by `repl`. Occurrences match by hash-consed identity, so all shared
    instances are rewritten at once; `node == formula` rewrites the root."""
    if formula == node:
        return repl
    return formula.map(lambda child: substitute(child, node, repl))
