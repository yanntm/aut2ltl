"""deep_memo recipe — the deep round trip FULLY inlined on one shared `Memo` store.

The finished form of `deep_nobls_memo`: same pipeline (a `cakedsdet`-shaped seed,
then a bottom-up `deep_roundtrip` re-presenting every DAG node via the no-bls
labeler, a final `hi` simplifier), but the seed is no longer an opaque import
wrapped in ONE `Memo` — every stage of the whole recipe is built here from basic
ingredients and wrapped on the SAME store, so the seed's internal peel/decompose
work is cached too, not just its outermost call.

Inlining buys one further sharing the opaque form could not express: `cakedsdet`'s
*rich* arm is structurally identical to the `nobls` labeler the deep pass uses, so
this recipe builds that labeler ONCE and uses the same instance in both places —
the seed's rich arm and the deep re-presentation arm. With `Memo` keyed on
`(id(operation), Language)`, identical work on a sub-language met by the seed and
met again by the deep pass is now a cache hit, not a re-peel.

Output is expected identical to `deep_nobls` / `deep_nobls_memo` (every `Memo` is
transparent; the arm-sharing swaps equal-by-construction instances); the change is
operational. A/B target: `tests/probes/gate_count.py` and the kinska counting
family, where the un-inlined seed re-validated one suffix 240x.
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
from aut2ltl.roundtrip_deep import deep_roundtrip
from aut2ltl.simplify_ltl import Simplify
from aut2ltl.daisy import Daisy
from aut2ltl.daisy2 import Daisy2
from aut2ltl.daisystar import Daisystar
from aut2ltl.daisystardet import DaisystarDet
from aut2ltl.partscc import PartScc
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


def _trio_det_fix(m: Wrap, floor: Optional[Translator], inv: bool) -> Translator:
    """The memoized `daisy_trio_det` fixpoint: per descent level try `Daisy` →
    `Daisy2` → `DaisystarDet` → `Daisystar` → `floor` (when given), every member
    wrapped on the shared store, exits re-entering the WHOLE level. `recurse` is
    untouched — the knot is tied by hand so the memo can sit inside it.
    `inv=True` weaves the per-descent `Invariant` strip (`daisy_trio_det_inv`)."""
    holder: Dict[str, Translator] = {}

    def leaf(lang: "Language") -> "LTLResult":
        return holder["fix"](lang)

    members: List[Translator] = [
        m(Daisy(leaf)), m(Daisy2(leaf)), m(DaisystarDet(leaf)), m(Daisystar(leaf))]
    if floor is not None:
        members.append(floor)
    level = first_success(members, name="daisy_trio_det")
    holder["fix"] = m(Invariant(level)) if inv else m(level)
    return holder["fix"]


def deep_memo(options: Optional[Options] = None) -> Translator:
    """The whole deep pipeline on one `(operation, Language)` compute table."""
    store: "Store" = Memo.new_store()        # the single compute table for the recipe

    def m(child: Translator) -> Translator:
        return Memo(child, store=store)

    def md(decorator: Decorator) -> Decorator:
        return lambda child: m(decorator(child))

    # [1] The no-bls labeler (== nobls, == cakedsdet's rich arm), built ONCE:
    #     Inv ∘ Strength ∘ Scc ∘ Inv ∘ Acc over the inv-woven det peel, floored on
    #     PartScc alone (no cascade), a memoized `hi` simplifier on top. Used both
    #     as the seed's rich arm [2] and as the deep re-presentation arm [3], so
    #     the two share every cache entry.
    rich_peel = _trio_det_fix(m, m(PartScc()), inv=True)
    rich_pipeline = compose(md(Invariant), md(StrengthDecompose), md(SccDecompose),
                            md(Invariant), md(AccDecompose))(rich_peel)
    nobls_arm = m(Simplify(m(rich_pipeline), "hi"))

    # [2] The seed (cakedsdet inlined): the incumbent arm —
    #     Strength ∘ Acc over the det peel, floored on core = first(partscc, bls)
    #     (the always-answers floor: the cascade may emit blobs, the deep pass
    #     shrinks them) — against the rich arm, which displaces it only on a
    #     significant form win.
    core = first_success([m(PartScc()), m(bls(options))], name="core")
    inc_peel = _trio_det_fix(m, core, inv=False)
    incumbent = m(Simplify(
        compose(md(StrengthDecompose), md(AccDecompose))(inc_peel), "hi"))
    seed = m(best_of([incumbent, nobls_arm], name="cakedsdet",
                     beats=significantly_smaller(rel=0.25, floor=2)))

    # [3] The deep pass: re-present every node of the seed's DAG bottom-up via the
    #     SAME no-bls labeler, kept per node only when not larger.
    represent = best_of([identity, relabel(nobls_arm)], name="deep_arm")
    rewriter = deep_roundtrip(represent)

    # [4] One final `hi` simplifier over the whole, memoized like everything else.
    return m(Simplify(as_translator(seed, rewriter), "hi"))


__all__ = ["deep_memo"]
