"""
aut2ltl/combinators.py — composite translators built over the contract.

A composite is itself a translator: it delegates to a collection of
sub-translators and combines their `ReconResult`s. Because every sub-result obeys
the contract invariant (language-faithful or DECLINED, never wrong), the
composite is sound by construction. The combinators here are generic over the
input type, so they apply to both `Translator` (automaton in) and
`CascadeTranslator` (cascade in) stages.

`first_success` is the chain-of-responsibility composite: try the stages in
order, take the first language-faithful result, else decline. The kr
acceptance-dispatch chain (acc → weak → buchi → cobuchi → bls) is one such
composition.
"""
from __future__ import annotations

from typing import Callable, Sequence, TypeVar

from aut2ltl.contract import ReconResult

_In = TypeVar("_In")


def first_success(
    stages: Sequence[Callable[[_In], ReconResult]],
) -> Callable[[_In], ReconResult]:
    """Compose `stages` into a single translator that returns the first stage
    whose result is OK (language-faithful), or a DECLINE if every stage declines.

    Each stage is self-gating: a stage that does not apply to the input returns a
    DECLINED `ReconResult`, and the chain moves on. The winning stage's result —
    including its `technique` set — is returned unchanged.
    """

    def run(x: _In) -> ReconResult:
        for stage in stages:
            r = stage(x)
            if r.ok:
                return r
        return ReconResult.decline()

    return run
