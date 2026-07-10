"""The `KAnchor` combinator Translator — the graded anchored SCC read-off.

`KAnchor` labels the SCC `C` of the initial state of the state-based form
(`sbacc(tgba(L))`) when the component's phase is recoverable from the last
k adjacent letters modulo stuttering (algorithm.md), delegating every exit
target to a child translator. The label is

    Final = STAY∞ ∨ LEAVE

assembled by `label.assemble` from the trigger table of the smallest window
level whose preconditions pass — k = 1 (anchor's letter windows, P1 + P2),
then k = 2 (adjacent pairs, P1² + P2² + P0²). Every level is exact by
construction: first-fit needs no equivalence gate. One equation covers
terminal, rejecting, accepting-with-exits and single-state components alike.

A NOT_LTL exit child is absorbed and its counting family lifted back to the
initial state across an exact reaching word (`lift.exit_word`, level-blind);
when no exact word exists the verdict does not lift and the peel degrades to
a non-absorbing decline.
"""

import os
import sys
from typing import Dict, List, Optional, TYPE_CHECKING

import spot

from aut2ltl.language import Language
from aut2ltl.result import LTLResult, Status
from aut2ltl.printer import format_language, format_result
from aut2ltl.ltl.twa import reroot
from .shape import init_scc_states, lame_data
from .windows import k1_violation, k1_table, k2_violation, k2_table
from .label import TriggerTable, assemble
from .pieces import Pieces
from .lift import exit_word

if TYPE_CHECKING:
    from aut2ltl.translator import Translator

_NAME = "kanchor"

# KANCHOR_TRACE, or the global TRANSLATOR_TRACE_ON which lights every
# translator trace at once. Every use guards with `if _TRACE:` BEFORE building
# its message, so a formula is never flattened for a trace that will not print.
_TRACE = "KANCHOR_TRACE" in os.environ or "TRANSLATOR_TRACE_ON" in os.environ


def _out(res: "LTLResult") -> "LTLResult":
    """Trace the outgoing result (status / size / formula), pass it through unchanged."""
    if _TRACE:
        print("[kanchor] out " + format_result(res), file=sys.stderr)
    return res


class KAnchor:
    """The graded anchored SCC read-off as a `Translator`
    (`Language → LTLResult`). Constructed with the child labeler for exit
    targets; holds no state. Tries the window levels k = 1 … `k_max` in order
    and adopts the first whose preconditions pass; declines when none does.
    `collapse=False` disables the sojourn-tautology collapse (the label then
    transcribes every sojourn literally)."""

    name = _NAME

    def __init__(self, child: "Translator", k_max: int = 2,
                 collapse: bool = True) -> None:
        self._child = child
        self._k_max = k_max
        self._collapse = collapse

    def __call__(self, lang: "Language") -> "LTLResult":
        aut = spot.postprocess(lang.tgba(), "sbacc")
        if _TRACE:
            print("[kanchor] in " + format_language(lang, aut), file=sys.stderr)
        return self.core(aut)

    def core(self, aut: "spot.twa_graph") -> "LTLResult":
        """The read-off after form acquisition: takes a prepared state-based
        automaton untouched — the delegation hook of `language_adapter/`
        (its algorithm.md), bypassing the `Language` input above."""
        res = LTLResult.start(_NAME)

        # State-based generalized Büchi is what the fairness read-off
        # transcribes; sbacc(tgba) yields it by construction — a guard, not a gate.
        if not aut.acc().is_generalized_buchi():
            return _out(res.fail(Status.DECLINED,
                                 "acceptance is not generalized Büchi after sbacc"))

        q0 = aut.get_init_state_number()
        C = init_scc_states(aut, q0)
        Lr, Ar, Mr, exits, P = lame_data(aut, C)
        # The k = 1 form of the δ↑ reclassification (algorithm.md, layer 4):
        # the promoted guard joins the triggers (A) and the legal stay-enders
        # (M) and leaves the loops (L); the k = 2 windows consume P directly
        # as the pseudo-edges (s, P[s], s).
        L = {s: Lr[s] - P[s] for s in C}
        A = {s: Ar[s] | P[s] for s in C}
        M = {s: Mr[s] | P[s] for s in C}

        # The k-ladder: smallest level first; every level's label is exact.
        table: Optional[TriggerTable] = None
        whys: List[str] = []
        why1 = k1_violation(L, A)
        if why1 is None:
            table = k1_table(aut, C, L, A)
        else:
            whys.append(f"k=1: {why1}")
            if self._k_max >= 2:
                why2 = k2_violation(aut, C, q0, L, A, P)
                if why2 is None:
                    table = k2_table(aut, C, q0, L, A, P)
                else:
                    whys.append(f"k=2: {why2}")
        if table is None:
            return _out(res.fail(Status.DECLINED,
                                 "phase not anchored (" + "; ".join(whys) + ")"))
        if _TRACE:
            print(f"[kanchor] level k={2 if whys else 1} "
                  f"(full={len(table.full)} starts={len(table.starts)})",
                  file=sys.stderr)

        # Delegate each distinct exit target to Λ; credit, bail on NOK.
        dsts: List[int] = [dst for s in C for _, dst in exits[s]]
        phi: Dict[int, "spot.formula"] = {}
        for dst in dict.fromkeys(dsts):
            sub = Language.of(reroot(aut, dst))
            if _TRACE:
                print(f"[kanchor] delegating exit {dst} as language: "
                      + format_language(sub, sub.tgba()), file=sys.stderr)
            child = self._child(sub)
            if child.not_ltl:
                # A NotLTL child lifts back to q0 by an EXACT reaching word
                # q0 ⟶* s →(g) dst (every step's letters restricted to fork
                # nowhere else — `lift.exit_word`), making the quotient
                # argument sound with no replay; no exact word ⇒ no lift.
                w_dst = exit_word(aut, C, q0, dst)
                if w_dst is None:
                    return _out(res.fail(Status.DECLINED,
                        "PROBABLY_NOT_LTL -- a non-LTL residue does not lift: no "
                        "exact reaching word through the SCC (every route's "
                        "letters also enable another target), so no verdict is "
                        "asserted"))
                res.prefix(child, "; ".join(w_dst), _NAME)
                return _out(res)
            res.credit(child)
            if res.nok:
                return _out(res)
            phi[dst] = child.formula

        pieces = Pieces(aut, L, M, exits, phi, collapse=self._collapse)
        res.formula = assemble(aut, C, q0, table, pieces)
        return _out(res)
