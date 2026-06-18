"""The `Simplify` Translator decorator (see README.md).

`Simplify(child, level)` wraps any Translator: forward the Language to `child`, and
on an OK result replace its formula with a language-preserving simplification at the
chosen level — `'lo'` our DAG-size-aware rules (`own_simplify`), `'hi'` those plus
Spot's `tl_simplifier` (`_simp_f`). A declined / NOT_LTL result passes through
unchanged; the technique tags stay the child's (simplification is representation, not
a reconstruction method, so it stamps no tag of its own).
"""

from __future__ import annotations

from typing import Callable, TYPE_CHECKING

from aut2ltl.ltl.builders import own_simplify, _simp_f

if TYPE_CHECKING:
    import spot

    from aut2ltl.translator import Translator
    from aut2ltl.result import LTLResult
    from aut2ltl.language import Language

# level → the simplifier it applies. 'lo' is our own DAG rules; 'hi' also runs Spot's
# tl_simplifier after ours (both, to a fixpoint).
_LEVELS: "dict[str, Callable[[spot.formula], spot.formula]]" = {
    "lo": own_simplify,
    "hi": _simp_f,
}


class Simplify:
    """Simplify a child Translator's formula. `level` in {'lo','hi'}: 'lo' = our DAG
    rules only; 'hi' = our rules then Spot's LTL simplifier. Transparent otherwise —
    a NOK result and the child's technique tags pass through unchanged."""

    name = "simplify"

    def __init__(self, child: "Translator", level: str = "lo") -> None:
        if level not in _LEVELS:
            raise ValueError(f"level must be 'lo' or 'hi', got {level!r}")
        self._child = child
        self._level = level
        self._simp = _LEVELS[level]

    def __call__(self, lang: "Language") -> "LTLResult":
        res = self._child(lang)
        if res.ok:
            res.formula = self._simp(res.formula)
        return res
