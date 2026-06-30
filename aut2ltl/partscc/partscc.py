"""The `partscc` leaf Translator (see algorithm.md).

`PartScc` labels a Language whose (state-based) automaton is a single terminal
(escape-free) SCC by partitioning it: each state gets a uniquely-characterizing
label `L(s)`, and when the labels are tight and pairwise disjoint it emits

    φ = O(q0) ∧ G(⋀_s (L(s) → X O(s))) ∧ ⋀_colors i GF(⋁_{s ∈ color i} L(s))

— the safety transition law anchored at the init state, plus one generalized-Büchi
conjunct per acceptance color — adopted **only** if it is language-equivalent to
the component. Otherwise it declines. Self-contained: no child, no composer
cooperation, no entry-timing. See algorithm.md.
"""

import os
import sys
from typing import TYPE_CHECKING

import spot

from aut2ltl.language import Language
from aut2ltl.result import LTLResult
from aut2ltl.printer import format_language, format_result
from .labels import scc_states, partition, outgoing_or

if TYPE_CHECKING:  # spot imported above for runtime use
    pass

_NAME = "partscc"
_F = spot.formula

# On when PARTSCC_TRACE or the global TRANSLATOR_TRACE_ON is set (presence). Built
# only inside `if _TRACE:`.
_TRACE = "PARTSCC_TRACE" in os.environ or "TRANSLATOR_TRACE_ON" in os.environ


def _out(res: "LTLResult") -> "LTLResult":
    """Trace the outgoing result (status / size), pass it through unchanged."""
    if _TRACE:
        print("[partscc] out " + format_result(res), file=sys.stderr)
    return res


def _validates(aut: "spot.twa_graph", phi: "spot.formula") -> bool:
    """Soundness gate: `φ` is adopted only if it is language-equivalent to the
    component `aut`. A wrong partition guess simply fails here and is declined, so
    partscc can never answer unsoundly."""
    try:
        cand = phi.translate("GeneralizedBuchi", "Small", "High")
        return spot.are_equivalent(aut, cand)
    except Exception:
        return False


class PartScc:
    """The terminal-SCC partition as a leaf `Translator` (`Language → LTLResult`).

    A producer, not a decorator: it takes no child and holds no state."""

    name = _NAME

    def __call__(self, lang: "Language") -> "LTLResult":
        # State-based acceptance: each color (acc set) becomes a SET OF STATES, so
        # the fairness conjunct below can characterize "visit color i i.o." by the
        # L-labels of its states.
        aut = spot.postprocess(lang.tgba(), "sbacc")
        if _TRACE:
            print("[partscc] in " + format_language(lang, aut), file=sys.stderr)

        states = scc_states(aut)
        if states is None:
            return _out(LTLResult.decline("not a single SCC of size >= 2"))

        labels = partition(aut, states)
        if labels is None:
            return _out(LTLResult.decline(
                "L-labels are not a tight pairwise-disjoint partition"))

        d = aut.get_dict()

        def _f(bdd: "buddy.bdd") -> "spot.formula":
            return spot.bdd_to_formula(bdd, d)

        # Safety skeleton (deterministic via the L-partition):
        #   O(q0)  ∧  G( ⋀_s ( L(s) → X O(s) ) )
        # The G-part is the steady-state transition law (if the last letter put us
        # in s, the next is a valid move out of s); the O(q0) conjunct anchors
        # position 0 to the init state's outgoing availability (no incoming letter
        # there — exactly the entry phase a bare steady G over-approximates).
        steady = _F.G(_F.And([
            _F.Or([_F.Not(_f(labels[s])), _F.X(_f(outgoing_or(aut, s)))])
            for s in states
        ]))
        anchor = _f(outgoing_or(aut, aut.get_init_state_number()))
        conjuncts = [anchor, steady]

        # Fairness: generalized-Büchi acceptance ⋀_i Inf(color i). Since "in state
        # s" ⟺ "previous letter ∈ L(s)", "visit color i i.o." is GF(⋁_{s∈i} L(s)).
        # Only generalized-Büchi acceptance fits this; other shapes fall through to
        # the equivalence gate (decline).
        if aut.acc().is_generalized_buchi():
            for i in range(aut.num_sets()):
                color = [s for s in states if i in aut.state_acc_sets(s).sets()]
                inf_i = _F.Or([_f(labels[s]) for s in color]) if color else _F.ff()
                conjuncts.append(_F.G(_F.F(inf_i)))

        phi = _F.And(conjuncts)

        if not _validates(aut, phi):
            return _out(LTLResult.decline(
                "candidate not language-equivalent to the component"))

        if _TRACE:
            print("[partscc] gate PASS", file=sys.stderr)
        return _out(LTLResult.success(phi, _NAME))
