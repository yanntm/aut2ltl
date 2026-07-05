"""Build the reference invariant I(L) from an automaton.

Adapter over the in-repo definability pipeline (``tests/probes/dg_common`` over
``aut2ltl/bls/definability``), which computes the canonical syntactic
omega-semigroup ``S(L)+1`` of a deterministic automaton's language. This reads
that algebra's raw tables, maps its letters onto the sosl alphabet, and runs it
through the shared `sosl.objects.canonical.canonicalize` normal form — so a
reference invariant is byte-comparable with a learned one.

Spot-backed and heavy: the teacher and the validator use it; the learner never
does. The underlying builder is precariously placed under ``tests/`` and will
move; when it does, only this adapter changes.
"""
from __future__ import annotations

import os

import spot

from aut2ltl.bls.definability.generators import extract_generators
from tests.probes.dg_common import quotient_of_hoa

from sosl.objects.alphabet import Alphabet
from sosl.objects.canonical import canonicalize
from sosl.objects.invariant import Invariant

_SCRATCH = os.path.join(os.path.dirname(__file__), os.pardir, "logs")


class ReferenceError(Exception):
    """The reference algebra could not be built (e.g. the monoid closure blew
    its cap)."""


def reference_of_hoa(path: str) -> Invariant:
    """The canonical reference `Invariant` of the language of HOA file ``path``."""
    data = quotient_of_hoa(path)
    if data is None:
        raise ReferenceError(f"algebra closure exceeded cap for {path}")
    alg, aut = data.alg, data.aut

    alphabet = Alphabet.of(ap.ap_name() for ap in aut.ap())
    # The pipeline's letter index li is the automaton's own mask; recover the
    # per-letter valuation (deterministic, same order as alg.letter_cls) and map
    # it onto the sosl mask, so the letter map is in our alphabet's terms.
    _gens, _masks, valuations = extract_generators(aut)
    letter_class = [0] * alphabet.size
    for li, val in enumerate(valuations):
        trues = [ap for ap, truth in val.items() if truth]
        letter_class[alphabet.letter_of(trues)] = alg.letter_cls[li]

    mult = [list(row) for row in alg.mult]
    accept = set(alg.accepting_pairs())
    identity = alg.word_cls(())
    return canonicalize(alphabet, identity, letter_class, mult, accept)


def reference_of_ltl(formula: str, scratch_dir: str = _SCRATCH) -> Invariant:
    """The canonical reference `Invariant` of an LTL/PSL formula's language,
    via a deterministic translation materialized under ``scratch_dir``."""
    aut = spot.translate(spot.formula(formula), "deterministic", "generic", "complete")
    os.makedirs(scratch_dir, exist_ok=True)
    path = os.path.join(scratch_dir, "_reference_input.hoa")
    with open(path, "w") as fh:
        fh.write(aut.to_str("hoa"))
    return reference_of_hoa(path)
