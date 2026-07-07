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
    # Spot keeps (or infers) the state-based reading when one exists — a
    # state-based HOA input survives postprocessing with its `state-acc`
    # property set, and renderers then draw accepting *states*. D is
    # transition-based by definition: the marks already sit on the edges
    # (Spot stores them there in every case), so dropping the property is
    # a pure re-reading, not a transformation.
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
