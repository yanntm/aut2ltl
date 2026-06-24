"""The `Roundtrip` combinator Translator (see algorithm.md).

`Roundtrip(labeler, finder)` labels a Language with `labeler`, lets `finder` pick a
node of the resulting formula, relabels that node's language with `labeler`, and
relinks the result in place. The whole-formula relabel is the special case of a
finder that returns the root. Constructed with the child `labeler` it applies on
both ends and the `finder`; holds no other state.
"""

from typing import Optional, TYPE_CHECKING

from aut2ltl.language import Language, UntranslatableLanguage
from aut2ltl.result import LTLResult
from .subst import substitute

if TYPE_CHECKING:
    import spot
    from aut2ltl.translator import Translator
    from .finder import Finder

_NAME = "roundtrip"


class Roundtrip:
    """A `Translator` (`Language → LTLResult`): `roundtrip(Λ, Φ)` of algorithm.md.

    `Λ` = `labeler` (applied on both ends), `Φ` = `finder`. Holds no other state."""

    name = _NAME

    def __init__(self, labeler: "Translator", finder: "Finder") -> None:
        self._labeler = labeler
        self._finder = finder

    def __call__(self, lang: "Language") -> "LTLResult":
        # Λ(L): a declined label has no formula to cut — propagate it (⊥ → ⊥).
        seed = self._labeler(lang)
        if seed.nok:
            return seed

        # Φ(φ): a declined finder returns the label verbatim, uncredited (Some φ).
        node: "Optional[spot.formula]" = self._finder(seed.formula)
        if node is None:
            return seed

        # Λ(lang(φ↓n)): relabel the node's language (φ↓n is the node itself). When the
        # subformula is too large for ltl2tgba the labeler raises rather than blow Spot
        # up — the relabel is then unavailable: decline.
        try:
            relabel = self._labeler(Language.of_ltl(node))
        except UntranslatableLanguage:
            return LTLResult.decline()
        if relabel.nok:
            return relabel        # a declined relabel is our decline; we do not mask it

        # φ[n ↦ ψ]: relink, crediting the round trip and both labelings (Some φ[n↦ψ]).
        res = LTLResult.start(_NAME)
        res.credit(seed)
        res.credit(relabel)
        res.formula = substitute(seed.formula, node, relabel.formula)
        return res
