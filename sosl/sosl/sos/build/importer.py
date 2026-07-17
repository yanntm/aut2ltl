"""Normalize an input automaton to the canonical form every sos consumer reads.

The reference builder and the membership teacher are defined over a
**deterministic, complete, transition-based, generic-acceptance** automaton D.
Any omega-automaton — nondeterministic, partial, state-based — is brought to that
form here, so no input has to be rejected or special-cased upstream.

Determinization and completion are a single in-process ``spot.postprocess``,
imitating the definability pipeline's idiom; the call is idempotent on an
automaton already in canonical form.
"""
from __future__ import annotations

import spot


def canonical(aut: "spot.twa_graph") -> "spot.twa_graph":
    """``aut`` normalized to the deterministic, complete, generic,
    transition-based form D (idempotent when ``aut`` is already in that form)."""
    a = spot.postprocess(aut, "deterministic", "generic", "complete")
    # Force transition-based acceptance. Spot's simplifications may hand back
    # a *state-based* marking (WDBA minimization of weak languages paints the
    # mark on every out-edge of an accepting state, dead edges included), and
    # the enrichment reads marks per edge, so placement must be normalized,
    # not merely re-read. The invariant enforced here: a mark sits only on an
    # edge inside its SCC. A mark on an edge leaving its SCC can never repeat,
    # hence never enters the inf-set any Inf/Fin atom evaluates — stripping it
    # is language-preserving for every Emerson-Lei condition.
    si = spot.scc_info(a)
    for e in a.edges():
        if si.scc_of(e.src) != si.scc_of(e.dst):
            e.acc = spot.mark_t([])
    a.prop_state_acc(spot.trival_maybe())
    return a


def import_hoa(path: str) -> "spot.twa_graph":
    """The canonical form D of the automaton in HOA file ``path``, determinizing
    and completing a nondeterministic or partial input as needed."""
    return canonical(spot.automaton(path))


def import_ltl(formula: str) -> "spot.twa_graph":
    """The canonical form D of an LTL/PSL formula's language, via a
    deterministic Spot translation."""
    return canonical(
        spot.translate(spot.formula(formula), "deterministic", "generic", "complete"))
