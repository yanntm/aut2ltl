"""Exact equivalence for a white-box teacher: the transformation-closure decision.

Complete (unlike ``bounded``): decides whether a Cayley `Hypothesis` captures the
*exact* language of a deterministic complete Emerson-Lei automaton D, returning
either agreement or the minimal disagreeing lasso.

The verdict of a lasso ``(u, v)`` depends only on two finite abstractions:

  - on **D**: the pair (state reached by ``u``, transition/mark *profile* of
    ``v``). From a D-state, iterating ``v``'s profile reaches an eventual cycle
    whose union of marks the Emerson-Lei condition judges — so the profile (per
    state: successor after ``v``, and marks seen along ``v``) fixes the D-verdict
    for every stem landing on that state.
  - on the **hypothesis**: the pair (class of ``u``, transformation of ``v`` on
    the classes) — exactly the inputs of the Cayley prediction
    (`Hypothesis.stabilized_pair`).

Two lassos that share a *stem-config* ``(D-state, class)`` and a *loop-element*
``(D-profile, class-transformation)`` therefore get identical verdicts from both
sides. Enumerating one representative lasso per ``(stem-config, loop-element)`` —
the shortlex-least stem reaching the config and the shortlex-least non-empty loop
realizing the element — is a complete check, and the shortlex-least representative
on which the two sides disagree is the minimal counterexample.

Stem-configs are the reachable states of the product of D with the hypothesis's
right action; loop-elements are the monoid generated (under concatenation) by the
per-letter (profile, transformation) pairs — the transformation closure.
"""
from __future__ import annotations

from collections import deque
from typing import Callable, Dict, FrozenSet, List, Optional, Sequence, Tuple

from sosl.sos.alphabet import Alphabet, Word
from sosl.sos.hypothesis import Hypothesis, loop_reps
from sosl.sos.lasso import Lasso
from sosl.teacher.equiv import resolve_prediction

Member = Callable[[Lasso], bool]

# A D-profile: per state q, (successor after the word, union of marks seen).
Profile = Tuple[Tuple[int, FrozenSet[int]], ...]
# A loop-monoid element: (D-profile, hypothesis class-transformation).
Element = Tuple[Profile, Tuple[int, ...]]

# Work cap on the transformation closure. Exact mode is for the campaign's small
# instances; past this many loop-elements it raises rather than running unbounded
# (an honest "too big to decide exactly", not a silent incomplete answer).
DEFAULT_MAX_ELEMENTS = 200_000


def _compose_profile(p1: Profile, p2: Profile) -> Profile:
    """The profile of ``v1.v2`` from the profiles of ``v1`` and ``v2``: run
    ``v1`` (giving state ``q1`` and marks ``m1``), then ``v2`` from ``q1``."""
    out: List[Tuple[int, FrozenSet[int]]] = []
    for q1, m1 in p1:
        q2, m2 = p2[q1]
        out.append((q2, m1 | m2))
    return tuple(out)


def _compose_trans(t1: Tuple[int, ...], t2: Tuple[int, ...]) -> Tuple[int, ...]:
    """The class-transformation of ``v1.v2``: apply ``t1`` then ``t2``."""
    return tuple(t2[t1[c]] for c in range(len(t1)))


def _stem_configs(
    h: Hypothesis, dst: Sequence[Sequence[int]], init: int, letters: Sequence[int]
) -> List[Tuple[Tuple[int, int], Word]]:
    """Reachable ``(D-state, class)`` configs with a shortlex-least stem each,
    by BFS over the product of D and the hypothesis right action from
    ``(init, start)``."""
    start = (init, h.start)
    word_of: Dict[Tuple[int, int], Word] = {start: ()}
    queue: deque = deque([start])
    while queue:
        cfg = queue.popleft()
        q, c = cfg
        u = word_of[cfg]
        for a in letters:
            nxt = (dst[a][q], h.step[c][a])
            if nxt not in word_of:
                word_of[nxt] = u + (a,)
                queue.append(nxt)
    return [(cfg, word_of[cfg]) for cfg in word_of]


def _loop_elements(
    h: Hypothesis,
    dst: Sequence[Sequence[int]],
    mark: Sequence[Sequence["object"]],
    n_states: int,
    letters: Sequence[int],
    max_elements: int,
) -> List[Tuple[Element, Word]]:
    """The transformation-closure elements with a shortlex-least non-empty loop
    each: the monoid generated (under right concatenation) by the per-letter
    ``(profile, transformation)`` pairs, BFS'd so the first witness of an element
    is shortlex-least."""
    def letter_element(a: int) -> Element:
        profile = tuple((dst[a][q], frozenset(mark[a][q].sets()))
                        for q in range(n_states))
        trans = tuple(h.step[c][a] for c in range(h.n))
        return (profile, trans)

    gens = [(a, letter_element(a)) for a in letters]
    word_of: Dict[Element, Word] = {}
    queue: deque = deque()
    for a, elt in gens:
        if elt not in word_of:
            word_of[elt] = (a,)
            queue.append(elt)
    while queue:
        elt = queue.popleft()
        w = word_of[elt]
        p1, t1 = elt
        for a, (p2, t2) in gens:
            nxt = (_compose_profile(p1, p2), _compose_trans(t1, t2))
            if nxt not in word_of:
                if len(word_of) >= max_elements:
                    raise ValueError(
                        f"exact: transformation closure exceeds {max_elements} "
                        "elements (instance too large for exact mode)"
                    )
                word_of[nxt] = w + (a,)
                queue.append(nxt)
    return [(elt, word_of[elt]) for elt in word_of]


def exact_counterexample(
    member: Member,
    alphabet: Alphabet,
    h: Hypothesis,
    dst: Sequence[Sequence[int]],
    mark: Sequence[Sequence["object"]],
    init: int,
    n_states: int,
    max_elements: int = DEFAULT_MAX_ELEMENTS,
) -> Tuple[Optional[Lasso], bool]:
    """Decide ``h`` against D exactly. Returns ``(lasso, True)`` with the minimal
    counterexample, or ``(None, True)`` if the hypothesis is exactly correct.

    ``dst``/``mark`` are D's per-letter successor and mark tables indexed
    ``[letter mask][state]`` (as compiled by the white-box teacher), ``init`` its
    initial state. Raises ``ValueError`` if the transformation closure exceeds
    ``max_elements`` (the instance is too large for an exact decision)."""
    assert h.alphabet.aps == alphabet.aps, "hypothesis/teacher alphabet mismatch"
    letters = alphabet.letters()
    loops = loop_reps(h)
    configs = _stem_configs(h, dst, init, letters)
    elements = _loop_elements(h, dst, mark, n_states, letters, max_elements)

    best: Optional[Lasso] = None
    best_key: Optional[Tuple[int, int, Word, Word]] = None
    for _cfg, u in configs:
        for _elt, v in elements:
            lasso = Lasso(u, v)
            if resolve_prediction(member, h, lasso, loops) != member(lasso):
                key = (len(u), len(v), u, v)
                if best_key is None or key < best_key:
                    best, best_key = lasso, key
    return best, True
