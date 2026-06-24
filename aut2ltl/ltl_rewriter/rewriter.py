"""
aut2ltl/ltl_rewriter/rewriter.py — the contract floor: the `Rewriter` signature.

A Rewriter is a callable `LTLResult -> LTLResult`: it re-presents an already-held
formula, keeping the `LTLResult` algebra (status, techniques, diagnosis) so rewriters
compose through the same monoids as translators. Like translator.py this module is an
interface — it states the signature and the load-bearing invariant and names no
implementor. The trivial `identity` rewriter (the never-regress floor) lives here.
"""
from __future__ import annotations

from typing import Protocol, TYPE_CHECKING, runtime_checkable

if TYPE_CHECKING:
    from aut2ltl.result import LTLResult


@runtime_checkable
class Rewriter(Protocol):
    """The behavioral contract: re-present one LTL result as another.

    A Rewriter is a callable `LTLResult -> LTLResult`. The input is an OK result
    carrying a formula (and the provenance accumulated so far); the output is either
    language-faithful (status OK, `.formula` ≡ the input's) or a NOK (DECLINED) —
    NEVER a wrong formula. Decline closes composition (`first_of` / `best_of`);
    `identity` is the floor that never declines.
    """

    def __call__(self, res: "LTLResult") -> "LTLResult": ...


def identity(res: "LTLResult") -> "LTLResult":
    """The unit Rewriter: return the result unchanged. Faithful, never declines —
    the never-regress floor for `best_of(identity, R)`."""
    return res
