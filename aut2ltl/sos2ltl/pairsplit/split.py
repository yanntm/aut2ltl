"""pairsplit/split.py — the acceptance-pair decomposition combinator.

Transcription of `algorithm.md`: put both sides' (L / dual) acceptance in DNF
over the deterministic generic body, pick the side that splits into the
thinnest pieces, translate each single-disjunct piece as a fresh `Language`
through the decorated translator itself (language-plane recursion, the inner
translator as base), OR the labels, negate back if the dual side was chosen.
Verdict discipline per algorithm.md: all-success is exact; any piece failure
(decline or piece-NOT_LTL, which is inconclusive for L) is a DECLINE.
"""
from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

import spot

from aut2ltl.language import Language
from aut2ltl.ltl.builders import _Or, _Not, _simp_f
from aut2ltl.ltl.twa import clone_structural
from aut2ltl.result import LTLResult, fuse

if TYPE_CHECKING:
    from aut2ltl.translator import Translator

TAG_PAIRSPLIT = "pairsplit"

# Language-plane recursion is bounded by the shrinking disjunct width
# (algorithm.md "Recursion"); the cap only guards against a pathological
# normalization that re-widens a piece, turning a cycle into a pass-through.
_MAX_DEPTH = 8


def _disjuncts(aut: "spot.twa_graph") -> List["spot.acc_code"]:
    """The DNF disjuncts of the automaton's acceptance condition."""
    return list(aut.get_acceptance().to_dnf().top_disjuncts())


def _width(disjunct: "spot.acc_code") -> int:
    """Atom count of one DNF disjunct (its Fin/Inf conjuncts)."""
    return len(list(disjunct.top_conjuncts()))


def _score(disjuncts: List["spot.acc_code"]) -> Tuple[int, int]:
    """(max piece width, piece count) — the lexicographic choice rule."""
    return (max((_width(d) for d in disjuncts), default=0), len(disjuncts))


def _piece(body: "spot.twa_graph", disjunct: "spot.acc_code") -> "Language":
    """One piece: the same body carrying a single DNF disjunct as acceptance."""
    aut = clone_structural(body)
    aut.set_acceptance(aut.num_sets(), disjunct)
    return Language.of(aut)


class PairSplit:
    """Decorator on the `Translator` protocol: acceptance-pair decomposition
    around `inner` (README.md). Invisible (pure pass-through) on inputs whose
    acceptance offers no split on either side."""

    def __init__(self, inner: "Translator") -> None:
        self.inner = inner

    def __call__(self, lang: "Language", _depth: int = 0) -> "LTLResult":
        if _depth >= _MAX_DEPTH:
            return self.inner(lang)
        aut = lang.det_generic()
        if not spot.is_deterministic(aut):
            return self.inner(lang)

        # Candidate sides: only a side with >= 2 disjuncts carries a union
        # split (a single-disjunct dual would just ping-pong under recursion).
        sides: List[Tuple[Tuple[int, int], bool, "spot.twa_graph", List["spot.acc_code"]]] = []
        for negate, body in ((False, aut), (True, spot.dualize(aut))):
            djs = _disjuncts(body)
            if len(djs) >= 2:
                sides.append((_score(djs), negate, body, djs))
        if not sides:
            return self.inner(lang)
        # Lexicographic score; ties go to the uncomplemented side (False < True).
        sides.sort(key=lambda s: (s[0], s[1]))
        _, negate, body, djs = sides[0]

        results: List["LTLResult"] = []
        for dj in djs:
            r = self(_piece(body, dj), _depth + 1)
            if not r.ok:
                why = "piece NOT_LTL (inconclusive for L)" if r.not_ltl else "piece declined"
                out = LTLResult.decline(
                    f"pairsplit: {why} on {dj}{' (dual side)' if negate else ''}"
                    + (f" -- {r.diagnosis}" if r.diagnosis else ""),
                    TAG_PAIRSPLIT)
                return fuse(out, r, *results)
            results.append(r)

        f = _simp_f(_Or(*[r.formula for r in results]))
        if negate:
            f = _simp_f(_Not(f))
        return fuse(LTLResult.success(f, TAG_PAIRSPLIT), *results)


__all__ = ["PairSplit", "TAG_PAIRSPLIT"]
