"""From the deterministic form ``D`` to the canonical invariant ``I(L)``.

The pipeline, station by station (`pipeline`), then the freeze (`invariant_of`):

  1. letter elements of ``D`` over the alphabet (`enriched`);
  2. the closed enriched monoid ``EM1(D)`` under a size cap (`closure`);
  3. the two congruence seeds — per-element residual vectors (``~lin``) and
     acceptance profiles (``~omega``) — refined to the syntactic congruence
     ``~`` (`congruence`);
  4. the freeze: quotient the images of **non-empty** words by ``~``, adjoin
     the identity as a *fresh* class, read the accepting linked pairs off the
     profiles at the initial state, and hand the raw algebra to `canonicalize`.

The identity convention of step 4 is normative (see ``algorithm.md``): a
quotient over monoid *elements* alone would merge a non-empty word into the
identity whenever their enriched elements coincide (e.g. ``!a`` in a one-state
automaton for ``GF a``), making the class count presentation-dependent and
breaking ``.sos`` byte-equality. Word classes are therefore the ``~``-classes
of the elements reachable as images of non-empty words — the identity element
included exactly when some non-empty word folds onto it — and ``[eps]`` is a
fresh class no word can collide with.

Input contract: ``aut`` is deterministic, complete, transition-based
Emerson-Lei (the form ``sos.build.importer.canonical`` produces). The result
is presentation-independent — any automaton of the same language yields the
byte-identical invariant.
"""
from __future__ import annotations

from typing import Dict, List, NamedTuple, Optional, Set, Tuple

import spot

from ..alphabet import Alphabet
from ..invariant import Invariant
from .canonical import canonicalize
from .closure import Monoid, close
from .congruence import Profile, profile, refine, residual_classes
from .enriched import Elem, letter_elems


class SosData(NamedTuple):
    """The pipeline's stations, deterministic form to refined congruence."""
    aut: "spot.twa_graph"       # the deterministic complete form D
    alphabet: Alphabet          # Sigma = 2^AP, canonical letter order
    init: int                   # initial state of D
    mon: Monoid                 # the closed enriched monoid EM1(D)
    cls: List[int]              # element -> ~-class (dense ids)
    prof: List[Profile]         # element -> acceptance profile Aprof


def pipeline(aut: "spot.twa_graph", cap: int = 20000) -> Optional[SosData]:
    """Run stations 1-3 on ``aut``, or ``None`` when the monoid closure blows
    ``cap`` elements."""
    alphabet = Alphabet.of(ap.ap_name() for ap in aut.ap())
    letters: List[Elem] = letter_elems(aut, alphabet)
    mon: Optional[Monoid] = close(letters, aut.num_states(), cap)
    if mon is None:
        return None
    st_cls: List[int] = residual_classes(aut)
    lin: List[Tuple[int, ...]] = [
        tuple(st_cls[st] for (st, _mk) in el) for el in mon.elems]
    acc = aut.acc()
    prof: List[Profile] = [profile(acc, el) for el in mon.elems]
    cls: List[int] = refine(mon, list(zip(lin, prof)))
    return SosData(aut=aut, alphabet=alphabet,
                   init=aut.get_init_state_number(),
                   mon=mon, cls=cls, prof=prof)


def invariant_of(aut: "spot.twa_graph", cap: int = 20000) -> Optional[Invariant]:
    """The canonical invariant ``I(L)`` of the language of ``aut``, or ``None``
    when the monoid closure blows ``cap``."""
    data = pipeline(aut, cap)
    return None if data is None else freeze(data)


def freeze(data: SosData) -> Invariant:
    """Station 4: the word-class quotient with a fresh identity, canonicalized.

    Word classes are the ``~``-classes of the elements that are images of
    non-empty words: every element the closure created past the identity, plus
    the identity element itself when it appears in the right table (some
    non-empty word then folds onto it). Each class's representative element
    stands in for it in every table read — the congruence makes the reads
    representative-independent.
    """
    mon, cls, prof, init = data.mon, data.cls, data.prof, data.init

    word_elems: List[int] = list(range(1, len(mon)))
    if any(0 in row for row in mon.right):
        word_elems.append(0)
    rep_of: Dict[int, int] = {}          # ~-class -> representative element
    for ei in word_elems:
        rep_of.setdefault(cls[ei], ei)
    wc: Dict[int, int] = {c: i for i, c in enumerate(rep_of)}
    reps: List[int] = list(rep_of.values())
    k: int = len(reps)                   # fresh identity gets class id k
    n: int = k + 1

    mult: List[List[int]] = [[0] * n for _ in range(n)]
    for i, ei in enumerate(reps):
        for j, ej in enumerate(reps):
            mult[i][j] = wc[cls[mon.mult(ei, ej)]]
        mult[i][k] = i                   # fresh is a two-sided unit on every
        mult[k][i] = i                   # class, yet a distinct class itself
    mult[k][k] = k

    letter_class: List[int] = [
        wc[cls[mon.right[0][a]]] for a in range(data.alphabet.size)]

    # P(s, e) = Aprof(rep(e))[st_{rep(s)}(init)] at the linked pairs — the
    # verdict of u.z^omega with [u] = s, [z] = e, read from the initial state.
    accept: Set[Tuple[int, int]] = set()
    for j, ej in enumerate(reps):
        if mult[j][j] != j:
            continue
        for i, ei in enumerate(reps):
            if mult[i][j] == i and prof[ej][mon.elems[ei][init][0]]:
                accept.add((i, j))

    return canonicalize(data.alphabet, k, letter_class, mult, accept)


__all__ = ["SosData", "pipeline", "invariant_of", "freeze"]
