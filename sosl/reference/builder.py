"""Build the reference invariant I(L) from an automaton.

Adapter over the in-repo definability pipeline (``tests/probes/dg_common`` over
``aut2ltl/bls/definability``), which computes the canonical syntactic
omega-semigroup ``S(L)+1`` of a deterministic automaton's language. This reads
that algebra's raw tables, maps its letters onto the sosl alphabet, adjoins the
identity as a fresh element (see ``algorithm.md`` — the enriched monoid merges a
neutral word into its identity, which this undoes), and runs the result through
the shared `sosl.objects.canonical.canonicalize` normal form — so a reference
invariant is byte-comparable with a learned one.

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
    letter_alg = [0] * alphabet.size
    for li, val in enumerate(valuations):
        trues = [ap for ap, truth in val.items() if truth]
        letter_alg[alphabet.letter_of(trues)] = alg.letter_cls[li]

    amult = [list(row) for row in alg.mult]

    # Fresh-identity adjunction (see algorithm.md). The enriched monoid `alg`
    # quotients over *elements*, so a non-empty word whose enriched element
    # coincides with the empty word's (e.g. `!a` in one-state `GF a`) is merged
    # into alg's identity — a presentation-dependent class count that breaks
    # `.sos` byte-equality. Keep only the elements reachable as images of
    # *non-empty* words (the subsemigroup the letters generate under `amult`)
    # and adjoin a fresh identity `fresh` that no word class can collide with.
    reachable = _generated_subsemigroup(letter_alg, amult)
    old_ids = sorted(reachable)
    remap = {c: i for i, c in enumerate(old_ids)}
    fresh = len(old_ids)
    n = fresh + 1

    mult = [[0] * n for _ in range(n)]
    for c in old_ids:
        i = remap[c]
        for d in old_ids:
            mult[i][remap[d]] = remap[amult[c][d]]
        mult[i][fresh] = i        # fresh is a two-sided unit on every class,
        mult[fresh][i] = i        # yet stays a distinct class of its own
    mult[fresh][fresh] = fresh

    letter_class = [remap[c] for c in letter_alg]
    accept = {
        (remap[s], remap[e])
        for (s, e) in alg.accepting_pairs()
        if s in reachable and e in reachable
    }
    return canonicalize(alphabet, fresh, letter_class, mult, accept)


def _generated_subsemigroup(generators: list[int], mult: list[list[int]]) -> set[int]:
    """The set of algebra classes reachable as images of non-empty words: the
    closure of ``generators`` (the letter classes) under the product ``mult``."""
    reachable = set(generators)
    work = list(reachable)
    while work:
        c = work.pop()
        for d in list(reachable):
            for p in (mult[c][d], mult[d][c]):
                if p not in reachable:
                    reachable.add(p)
                    work.append(p)
    return reachable


def reference_of_ltl(formula: str, scratch_dir: str = _SCRATCH) -> Invariant:
    """The canonical reference `Invariant` of an LTL/PSL formula's language,
    via a deterministic translation materialized under ``scratch_dir``."""
    aut = spot.translate(spot.formula(formula), "deterministic", "generic", "complete")
    os.makedirs(scratch_dir, exist_ok=True)
    path = os.path.join(scratch_dir, "_reference_input.hoa")
    with open(path, "w") as fh:
        fh.write(aut.to_str("hoa"))
    return reference_of_hoa(path)
