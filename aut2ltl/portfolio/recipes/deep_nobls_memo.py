"""deep_nobls_memo recipe — `deep_nobls` with the no-bls assembly MEMOIZED through a
SINGLE shared cache.

Identical assembly to `deep_nobls` (cakedsdet seed, then a bottom-up `deep_roundtrip`
re-presenting every DAG node via the no-bls decomposition), with one change: the whole
inlined `nobls` pipeline is wrapped, stage by stage, in ONE shared memo `m`:

    m( compose( m(Invariant), m(Strength), m(Scc), m(Invariant), m(Acc), m(daisy) )
               ( m(PartScc()) ) )

`m` is a single instance with one cache keyed on the interned `Language` (its BDD/HOA
identity) — deliberately "dumb": it does not key on *which* stage asks, only on the
language. That is SOUND by the combinator algebra (`combinators/README.md`): every
stage is faithful-or-⊥, so any OK answer cached for a language `L` is language-equivalent
to whatever another stage would have produced for `L` — never a wrong formula. The win
is operational: each distinct sub-language is decomposed/peeled ONCE, across the whole
pipeline and across every `deep_roundtrip` node (the cache is long-lived, a
`WeakKeyDictionary` that releases an entry when its `Language` is).

Motivation (kinska `counting_buchi_1ap_18`, `tests/probes/gate_count.py`): the soundness
gates fire 1271× on only 78 distinct (input, candidate) pairs — 94% exact recomputes,
one suffix re-validated 240× — because the büchi-tower suffixes are re-peeled on every
descent path. The gates are cheap (~17ms); the redundancy is the surrounding peel work.
The shared memo collapses it to DAG-size complexity. `Memo` stamps no technique tag, so
the credited stack is unchanged from `deep_nobls`.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict, Optional
from weakref import WeakKeyDictionary

from aut2ltl.translator import Translator
from aut2ltl.options import Options
from aut2ltl.combinators.best_of import best_of
from aut2ltl.combinators.compose import compose
from aut2ltl.combinators.first_success import first_success
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
from .cakedsdet import cakedsdet

if TYPE_CHECKING:
    from aut2ltl.language import Language
    from aut2ltl.result import LTLResult

Decorator = Callable[[Translator], Translator]


def _shared_memo() -> "tuple[Callable[[Translator], Translator], Callable[[Decorator], Decorator]]":
    """One cache, two lifts. `m(t)` memoizes a Translator on the shared cache; `md(d)`
    lifts a Decorator so the translator it builds is memoized on that SAME cache. The
    cache is keyed on `Language` identity (interned, so identity = BDD/HOA identity)
    and is a `WeakKeyDictionary`, so it never pins a `Language` against the intern LRU.
    Declines are cached too (a declined `LTLResult` is a real object; the miss sentinel
    is `None`) — sound because faithful-or-⊥ is closed under the algebra."""
    cache: "WeakKeyDictionary[Language, LTLResult]" = WeakKeyDictionary()

    def m(child: Translator) -> Translator:
        def memoized(lang: "Language") -> "LTLResult":
            hit = cache.get(lang)
            if hit is None:
                hit = child(lang)
                cache[lang] = hit
            return hit
        return memoized

    def md(decorator: Decorator) -> Decorator:
        return lambda child: m(decorator(child))

    return m, md


def _nobls_memo() -> Translator:
    """The `nobls` assembly inlined and memoized through one shared cache: the decomp
    pipeline (`Invariant ∘ Strength ∘ Scc ∘ Invariant ∘ Acc`) over the daisy peel, every
    stage + the floor + the whole wrapped in `m`. The daisy recursion's leaf is the
    memoized daisy fixpoint, so a shared suffix reached again is a cache hit, not a
    re-peel; floors on `PartScc()`. `recurse` is untouched — the knot is tied by hand
    so the shared memo can sit in it."""
    m, md = _shared_memo()

    holder: Dict[str, Translator] = {}

    def daisy_leaf(lang: "Language") -> "LTLResult":
        return holder["daisy"](lang)

    daisy_fix = Invariant(first_success(
        [Daisy(daisy_leaf), Daisy2(daisy_leaf), DaisystarDet(daisy_leaf),
         Daisystar(daisy_leaf), m(PartScc())],
        name="daisy_trio_det"))
    holder["daisy"] = m(daisy_fix)                       # the memoized recursion target

    pipeline = compose(md(Invariant), md(StrengthDecompose), md(SccDecompose),
                       md(Invariant), md(AccDecompose))(holder["daisy"])
    whole = m(pipeline)                                  # m(compose(m(a), m(b), …))
    return Simplify(whole, "hi")


def deep_nobls_memo(options: Optional[Options] = None) -> Translator:
    """`deep_nobls` with the no-bls return-labeler memoized through a single shared
    cache: `cakedsdet` seeds a formula, then `deep_roundtrip` re-presents every DAG
    node bottom-up via the memoized no-bls assembly, kept per node only when not larger
    (`best_of([identity, relabel])`); a final `hi` simplifier over the whole."""
    represent = best_of([identity, relabel(_nobls_memo())], name="deep_nobls_arm")
    rewriter = deep_roundtrip(represent)
    return Simplify(as_translator(cakedsdet(options), rewriter), "hi")


__all__ = ["deep_nobls_memo"]
