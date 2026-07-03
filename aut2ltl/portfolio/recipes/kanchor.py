"""kanchor recipe — `deep_memo` with the graded k-anchor brick in place of the
pair it subsumes (`DaisystarDet` + `PartScc`).

The A/B copy of `deep_memo`: same fully-inlined pipeline on one shared `Memo`
store, with every peel level reading `Daisy` → `Daisy2` → `KAnchor` →
`Daisystar` — `Daisy2` stays above the anchor because its labels are more
compact when it applies (it is Spot-gated, not sound alone; `KAnchor` is the
exact-by-construction fallback below it).
`KAnchor` (`aut2ltl/kanchor/algorithm.md`) is the graded anchored SCC
read-off: it labels the initial SCC of the state-based form whenever its
phase is recoverable from the last k adjacent letters modulo stuttering
(`STAY∞ ∨ LEAVE`, exact by construction), trying the window levels
k = 1 … k_max in order and adopting the smallest that passes. At k = 1 it
covers what `DaisystarDet` (rejecting, input-deterministic) and `PartScc`
(terminal, input-deterministic) covered as separate regimes; the higher
levels extend the anchored region beyond either. Consequently the explicit
`PartScc` floors disappear: the rich arm's peel is its own floor (a
non-anchored residual declines — the no-cascade discipline), and the
incumbent's floor is the bare `bls` cascade.

The raw read-off deliberately keeps trivial identities (the transcription is
as tight as the structure requires, cleanup is the pipeline's job), so the
brick is wrapped in a `hi` simplifier: each anchored label is collapsed
BEFORE the parent embeds it, so the peel composes small forms, not raw laws.

A/B against `deep_memo` (the pair) and `deep_anchor` (the k = 1 brick): same
seed/deep/simplify skeleton, the peel bricks are the only variable.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict, List, Optional

from aut2ltl.translator import Translator
from aut2ltl.options import Options
from aut2ltl.combinators.best_of import best_of, significantly_smaller
from aut2ltl.combinators.compose import compose
from aut2ltl.combinators.first_success import first_success
from aut2ltl.combinators.memo import Memo
from aut2ltl.ltl_rewriter import identity, relabel, as_translator
from aut2ltl.roundtrip import deep_roundtrip
from aut2ltl.simplify_ltl import Simplify
from aut2ltl.kanchor import KAnchor
from aut2ltl.daisy import Daisy
from aut2ltl.daisy2 import Daisy2
from aut2ltl.daisystar import Daisystar
from aut2ltl.decomp.inv import Invariant
from aut2ltl.decomp.acceptance import AccDecompose
from aut2ltl.decomp.scc import SccDecompose
from aut2ltl.decomp.strength import StrengthDecompose
from ..builder import bls

if TYPE_CHECKING:
    from aut2ltl.language import Language
    from aut2ltl.result import LTLResult
    from aut2ltl.combinators.memo.memo import Store

Decorator = Callable[[Translator], Translator]
Wrap = Callable[[Translator], Translator]


def _kanchor_fix(m: Wrap, floor: Optional[Translator], inv: bool) -> Translator:
    """The memoized k-anchored peel fixpoint: per descent level try `Daisy`
    (TGBA, transition-based petal acceptance) → `Daisy2` (compact when it
    applies) → `KAnchor` (the graded anchored SCC read-off, `hi`-simplified as
    it is built) → `Daisystar` → `floor` (when given), every member wrapped on
    the shared store, exits re-entering the WHOLE level. The knot is tied by
    hand so the memo can sit inside it. `inv=True` weaves the per-descent
    `Invariant` strip."""
    holder: Dict[str, Translator] = {}

    def leaf(lang: "Language") -> "LTLResult":
        return holder["fix"](lang)

    members: List[Translator] = [
        m(Daisy(leaf)), m(Daisy2(leaf)), m(Simplify(KAnchor(leaf), "hi")),
        m(Daisystar(leaf))]
    if floor is not None:
        members.append(floor)
    level = first_success(members, name="daisy_kanchor")
    holder["fix"] = m(Invariant(level)) if inv else m(level)
    return holder["fix"]


def kanchor(options: Optional[Options] = None) -> Translator:
    """`deep_memo` with the graded k-anchored peel (see the module docstring)."""
    store: "Store" = Memo.new_store()        # the single compute table for the recipe

    def m(child: Translator) -> Translator:
        return Memo(child, store=store)

    def md(decorator: Decorator) -> Decorator:
        return lambda child: m(decorator(child))

    # [1] The no-cascade labeler (the rich arm AND the deep arm — one instance,
    #     shared cache entries): Inv ∘ Strength ∘ Scc ∘ Inv ∘ Acc over the
    #     inv-woven k-anchored peel, no explicit floor (KAnchor is the
    #     terminal-SCC labeler; a non-anchored residual declines), a memoized
    #     `hi` simplifier.
    rich_peel = _kanchor_fix(m, None, inv=True)
    rich_pipeline = compose(md(Invariant), md(StrengthDecompose), md(SccDecompose),
                            md(Invariant), md(AccDecompose))(rich_peel)
    noblob_arm = m(Simplify(m(rich_pipeline), "hi"))

    # [2] The seed: the incumbent arm — Strength ∘ Acc over the k-anchored
    #     peel, floored on the bare `bls` cascade (the always-answers floor;
    #     PartScc's old slot in `core` is KAnchor's job now) — against the rich
    #     arm, which displaces it only on a significant form win.
    inc_peel = _kanchor_fix(m, m(bls(options)), inv=False)
    incumbent = m(Simplify(
        compose(md(StrengthDecompose), md(AccDecompose))(inc_peel), "hi"))
    seed = m(best_of([incumbent, noblob_arm], name="cake_kanchor",
                     beats=significantly_smaller(rel=0.25, floor=2)))

    # [3] The deep pass: re-present every node of the seed's DAG bottom-up via the
    #     SAME no-cascade labeler, kept per node only when not larger.
    represent = best_of([identity, relabel(noblob_arm)], name="deep_arm")
    rewriter = deep_roundtrip(represent)

    # [4] One final `hi` simplifier over the whole, memoized like everything else.
    return m(Simplify(as_translator(seed, rewriter), "hi"))


__all__ = ["kanchor"]
