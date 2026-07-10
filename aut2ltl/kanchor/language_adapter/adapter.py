"""The language-adapter Translator (algorithm.md): explores several
presentations of the language, in order, delegating each prepared automaton
to the kanchor core hook (`KAnchor.core`, bypassing form acquisition). The
first non-declined answer returns — `OK`, or `NOT_LTL` at any presentation
(a witness is a property of the language, not of a form); a decline falls
through to the next presentation; exhaustion declines naming what was
tried. Presentations: identity, deterministic, and the start peel in its
blind staging (no context handoff yet — the child is explored afresh, one
letter deeper, under the `k−1` saturation budget).
"""

from typing import List, Optional, TYPE_CHECKING

import spot

from aut2ltl.language import Language
from aut2ltl.result import LTLResult
from ..kanchor import KAnchor
from aut2ltl.twa import reroot

if TYPE_CHECKING:
    from aut2ltl.translator import Translator

_NAME = "kanchor"


class AdaptedKAnchor:
    """kanchor behind the presentation exploration — a `Translator`
    (`Language → LTLResult`), constructed exactly like `KAnchor`; the
    identity presentation is the bare brick. `peel_budget` is the number of
    start peels still allowed down this exploration (defaults to
    `k_max − 1`, the window-saturation bound of algorithm.md)."""

    name = _NAME

    def __init__(self, child: "Translator", k_max: int = 2,
                 collapse: bool = True,
                 peel_budget: Optional[int] = None) -> None:
        self._child = child
        self._k_max = k_max
        self._collapse = collapse
        self._peel_budget = k_max - 1 if peel_budget is None else peel_budget
        self._brick = KAnchor(child, k_max=k_max, collapse=collapse)

    def _deterministic(self, aut: "spot.twa_graph"
                       ) -> Optional["spot.twa_graph"]:
        """Presentation 2: the state-based deterministic form, or `None` when
        it adds nothing (already deterministic) or the production does not
        yield deterministic generalized Büchi (skipped)."""
        if spot.is_deterministic(aut):
            return None
        try:
            det = spot.postprocess(aut, "deterministic", "sbacc")
        except (RuntimeError, ValueError):
            return None
        if not spot.is_deterministic(det) \
                or not det.acc().is_generalized_buchi():
            return None
        return det

    def _peel(self, det: "spot.twa_graph") -> "LTLResult":
        """Presentation 3 — the start peel, blind staging: on a deterministic
        form the position-0 cells are exactly `q0`'s out-edges (disjoint
        guards), so `Final = ⋁ g ∧ X φ_dst` with each child explored by a
        budget-decremented adapter; a NOT_LTL child lifts across the peeled
        letter by the standard peeler move (`result.prefix`)."""
        q0 = det.get_init_state_number()
        d = det.get_dict()
        res = LTLResult.start(_NAME + "@peel")
        parts: List["spot.formula"] = []
        sub_rec = AdaptedKAnchor(self._child, k_max=self._k_max,
                                 collapse=self._collapse,
                                 peel_budget=self._peel_budget - 1)
        for e in det.out(q0):
            g = spot.bdd_to_formula(e.cond, d)
            r = sub_rec(Language.of(reroot(det, int(e.dst))))
            res.prefix(r, str(g))
            if res.nok:
                return res
            parts.append(spot.formula.And([g, spot.formula.X(r.formula)]))
        res.formula = spot.formula.Or(parts)
        return res

    def __call__(self, lang: "Language") -> "LTLResult":
        base = spot.postprocess(lang.tgba(), "sbacc")
        res = self._brick.core(base)
        if not res.declined:
            return res
        tried: List[str] = [f"identity: {res.diagnosis}"]
        det = self._deterministic(base)
        if det is None:
            det = base if spot.is_deterministic(base) else None
            if det is None:
                tried.append("det: no deterministic GB form produced")
        else:
            res = self._brick.core(det).credit(LTLResult.start(_NAME + "@det"))
            if not res.declined:
                return res
            tried.append(f"det: {res.diagnosis}")
        if det is not None and self._peel_budget > 0:
            res = self._peel(det)
            if not res.declined:
                return res
            tried.append(f"peel: {res.diagnosis}")
        return LTLResult.decline("; ".join(tried), _NAME)
