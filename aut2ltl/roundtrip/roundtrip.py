"""The `Roundtrip` combinator Translator (see algorithm.md).

`Roundtrip(labeler)` labels a Language with `labeler`, re-describes the language by
the resulting formula, and labels that re-description with `labeler` again — returning
the second result. A declined first label propagates unchanged. Constructed with the
child `labeler` Translator it applies on both ends.
"""

from typing import TYPE_CHECKING

from aut2ltl.language import Language
from aut2ltl.result import LTLResult

if TYPE_CHECKING:
    from aut2ltl.translator import Translator

_NAME = "roundtrip"


class Roundtrip:
    """A `Translator` (`Language → LTLResult`) that re-derives its answer through one
    formula round trip: label with `labeler`, rebuild a Language from that formula,
    label that again.

    Constructed with the child `labeler` it applies on both ends; holds no other
    state."""

    name = _NAME

    def __init__(self, labeler: "Translator") -> None:
        self._labeler = labeler

    def __call__(self, lang: "Language") -> "LTLResult":
        res = LTLResult.start(_NAME)                   # start OK, credit ourselves

        seed = self._labeler(lang)
        res.credit(seed)
        if res.nok:                                    # nothing to re-describe
            return res

        relabel = self._labeler(Language.of_ltl(seed.formula))
        res.credit(relabel)
        if res.ok:                                     # finish: take the re-derivation
            res.formula = relabel.formula
        return res
