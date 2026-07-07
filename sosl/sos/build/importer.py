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
    return spot.postprocess(aut, "deterministic", "generic", "complete")


def import_hoa(path: str) -> "spot.twa_graph":
    """The canonical form D of the automaton in HOA file ``path``, determinizing
    and completing a nondeterministic or partial input as needed."""
    return canonical(spot.automaton(path))


def import_ltl(formula: str) -> "spot.twa_graph":
    """The canonical form D of an LTL/PSL formula's language, via a
    deterministic Spot translation."""
    return canonical(
        spot.translate(spot.formula(formula), "deterministic", "generic", "complete"))
