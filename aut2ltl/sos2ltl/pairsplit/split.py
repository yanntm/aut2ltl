"""pairsplit/split.py — the acceptance-pair decomposition combinator.

Transcription of `algorithm.md`: recurse on the top ∧/∨ connective of the
acceptance condition over the deterministic generic body (∨ → union split on
any body, ∧ → intersection split, sound by determinism), fuse sibling atoms
of matching polarity into single pieces, translate atomic pieces through the
inner translator, recombine the labels with the same connective. Verdict
discipline per algorithm.md: all-success is exact; any piece failure (decline
or piece-NOT_LTL, which is inconclusive for L) is a DECLINE.
"""
from __future__ import annotations

from typing import Callable, List, Tuple, TYPE_CHECKING

import spot

from aut2ltl.language import Language
from aut2ltl.ltl.builders import _And, _Or, _simp_f
from aut2ltl.ltl.twa import clone_structural
from aut2ltl.result import LTLResult, fuse

if TYPE_CHECKING:
    from aut2ltl.translator import Translator

TAG_PAIRSPLIT = "pairsplit"

# The structural recursion shrinks the acceptance code at every level; the cap
# only guards the indirect risk that a PIECE's own det_generic normalization
# re-widens its condition (turning a pathological cycle into a pass-through).
_MAX_DEPTH = 8


def _atom_kind(code: "spot.acc_code") -> str:
    """'inf' / 'fin' for a single-mark atom, '' for anything else."""
    marks = list(code.used_sets().sets())
    if len(marks) == 1:
        if code == spot.acc_code.inf(marks):
            return "inf"
        if code == spot.acc_code.fin(marks):
            return "fin"
    return ""


def _fuse_atoms(children: List["spot.acc_code"], op: str) -> List[Tuple["spot.acc_code", bool]]:
    """Group the children of one ∧/∨ node (algorithm.md "Pair fusion"):
    pure-Inf atoms under ∨ (resp. pure-Fin atoms under ∧) collapse into a
    single piece whose acceptance is their connective — the mark-set union.
    Returns (code, fused) pairs; a fused piece is a LEAF for the recursion
    (re-entering would just re-split it). Opposite polarities never fuse."""
    fusable_kind = "inf" if op == "or" else "fin"
    fused_group: List["spot.acc_code"] = []
    out: List[Tuple["spot.acc_code", bool]] = []
    for c in children:
        if _atom_kind(c) == fusable_kind:
            fused_group.append(c)
        else:
            out.append((c, False))
    if len(fused_group) == 1:
        out.append((fused_group[0], False))
    elif fused_group:
        code = fused_group[0]
        for c in fused_group[1:]:
            code = (code | c) if op == "or" else (code & c)
        out.append((code, True))
    return out


def _piece(body: "spot.twa_graph", code: "spot.acc_code") -> "Language":
    """One piece: the same body carrying one sub-condition as acceptance."""
    aut = clone_structural(body)
    aut.set_acceptance(aut.num_sets(), code)
    return Language.of(aut)


class PairSplit:
    """Decorator on the `Translator` protocol: acceptance-pair decomposition
    around `inner` (README.md). Invisible (pure pass-through) on atomic
    acceptance."""

    def __init__(self, inner: "Translator") -> None:
        self.inner = inner

    def __call__(self, lang: "Language", _depth: int = 0) -> "LTLResult":
        if _depth >= _MAX_DEPTH:
            return self.inner(lang)
        aut = lang.det_generic()
        code = aut.get_acceptance()

        djs = list(code.top_disjuncts())
        if len(djs) >= 2:
            children, combine, op = djs, _Or, "or"
        else:
            cjs = list(code.top_conjuncts())
            if len(cjs) >= 2 and spot.is_deterministic(aut):
                # The intersection identity needs the unique run — determinism
                # is established by det_generic; checked, never assumed.
                children, combine, op = cjs, _And, "and"
            else:
                return self.inner(lang)

        parts = _fuse_atoms(children, op)
        if len(parts) < 2:
            # Fusion collapsed the node to one piece == the whole language.
            return self.inner(lang)

        results: List["LTLResult"] = []
        for part, fused in parts:
            piece = _piece(aut, part)
            r = self.inner(piece) if fused else self(piece, _depth + 1)
            if not r.ok:
                why = "piece NOT_LTL (inconclusive for L)" if r.not_ltl else "piece declined"
                out = LTLResult.decline(
                    f"pairsplit: {why} on {part} under {op}"
                    + (f" -- {r.diagnosis}" if r.diagnosis else ""),
                    TAG_PAIRSPLIT)
                return fuse(out, r, *results)
            results.append(r)

        f = _simp_f(combine(*[r.formula for r in results]))
        return fuse(LTLResult.success(f, TAG_PAIRSPLIT), *results)


__all__ = ["PairSplit", "TAG_PAIRSPLIT"]
