"""Build the reference invariant I(L) from an automaton or a formula.

Thin adapter over the canonical construction (``sos.core``): normalize the
input to the deterministic complete generic form D (`importer.canonical`),
run the pipeline, and own the resource policy — a blown monoid-closure cap
surfaces as `ReferenceError` here, the core stays pure.

Spot-backed and heavy: the teacher and the validator use it; the learner never
does (see README.md — the layering forbids the edge).
"""
from __future__ import annotations

import os

from ..core.quotient import invariant_of
from ..invariant import Invariant
from .importer import import_hoa, import_ltl

_SCRATCH = os.path.join(os.path.dirname(__file__), os.pardir, "logs")


class ReferenceError(Exception):
    """The reference algebra could not be built (e.g. the monoid closure blew
    its cap)."""


def reference_of_hoa(path: str) -> Invariant:
    """The canonical reference `Invariant` of the language of HOA file ``path``."""
    inv = invariant_of(import_hoa(path))
    if inv is None:
        raise ReferenceError(f"algebra closure exceeded cap for {path}")
    return inv


def reference_of_ltl(formula: str, scratch_dir: str = _SCRATCH) -> Invariant:
    """The canonical reference `Invariant` of an LTL/PSL formula's language.

    The deterministic form D the construction runs on (`importer.import_ltl`)
    is materialized under ``scratch_dir`` — the scratch file is exactly the
    automaton the pipeline consumed, for inspection after the fact."""
    aut = import_ltl(formula)
    os.makedirs(scratch_dir, exist_ok=True)
    path = os.path.join(scratch_dir, "_reference_input.hoa")
    with open(path, "w") as fh:
        fh.write(aut.to_str("hoa", "t"))  # "t": never re-declare state-acc
    inv = invariant_of(aut)
    if inv is None:
        raise ReferenceError(f"algebra closure exceeded cap for {formula}")
    return inv
