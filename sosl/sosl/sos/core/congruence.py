"""The syntactic congruence on the closed monoid — Key II of the construction.

Arnold's two-sided congruence, computed with right moves alone. It factors
into two independently checkable halves (the collapse), each seeded here:

  - ``~lin`` — pointwise residual equality: elements ``e, f`` agree when the
    states ``st_e(q)`` and ``st_f(q)`` accept the same omega-language, for
    every ``q``. The base is `residual_classes`, the language equivalence of
    the automaton's states, recovered from the loop-verdict matrix the
    profiles already hold — no external decision procedure.
  - ``~omega`` — right-invariant profile equality: ``Aprof(e.b) = Aprof(f.b)``
    for every right extension ``b``. The seed is `profile`, the per-state
    verdict of iterating an element forever.

The rotation lemma makes a left factor act on the seeds only by re-indexing a
state slot, so the coarsest **right**-invariant equivalence refining the seed
pair is the full two-sided congruence: one Moore refinement to fixpoint
computes ``~ = ~lin ∧ ~omega`` exactly. `refine` is that engine, shared by
both levels: on the monoid's right table for ``~``, on the letter maps of
``D`` for the residual base.
"""
from __future__ import annotations

from typing import Dict, Hashable, List, Optional, Sequence, Set, Tuple

import spot

from .closure import Monoid
from .enriched import Elem

Profile = Tuple[bool, ...]
"""``Aprof(c)``: for each state ``q``, the acceptance of iterating ``c``
forever from ``q``."""


def residual_classes(mon: Monoid, prof: Sequence[Profile]) -> List[int]:
    """The residual class of every state: ``out[q] == out[q']`` iff the
    omega-languages accepted from ``q`` and ``q'`` are equal — dense ids in
    order of first appearance.

    State-level Moore refinement on the loop-verdict matrix. The seed is the
    profile *column* of each state (``A(q, c)`` for every element ``c`` — the
    verdicts of all pure loops from ``q``, the empty-stem lassos; the identity
    column is constant, hence inert). Refinement under the letter maps closes
    the agreement under letter stems, hence — ``EM1`` being letter-generated —
    under all stems; by lasso density the fixpoint is exactly language
    equivalence of states."""
    n_states: int = len(mon.elems[0])
    letters: List[int] = mon.right[0]        # identity row: letter elements
    delta: List[List[int]] = [
        [mon.elems[le][q][0] for le in letters] for q in range(n_states)]
    seed: List[Tuple[bool, ...]] = [
        tuple(p[q] for p in prof) for q in range(n_states)]
    return refine(delta, seed)


def profile(acc: "spot.acc_cond", elem: Elem) -> Profile:
    """``A(q, elem)`` for every state ``q``: walk the functional graph of the
    element's state map, evaluate the acceptance condition on the marks
    collected around each closed cycle (the ones seen infinitely often),
    propagate the verdict to the transients (their marks are visited finitely
    often). One ``O(|Q|)`` pass."""
    n: int = len(elem)
    out: List[Optional[bool]] = [None] * n
    for start in range(n):
        if out[start] is not None:
            continue
        path: List[int] = []
        pos: Dict[int, int] = {}
        q = start
        while out[q] is None and q not in pos:
            pos[q] = len(path)
            path.append(q)
            q = elem[q][0]
        if out[q] is not None:
            verdict = out[q]
        else:
            inf: Set[int] = set()
            for s in path[pos[q]:]:
                inf |= elem[s][1]
            verdict = bool(acc.accepting(spot.mark_t(sorted(inf))))
        for s in path:
            out[s] = verdict
    return tuple(out)  # type: ignore[arg-type]


def refine(succ: Sequence[Sequence[int]], seed: Sequence[Hashable]) -> List[int]:
    """The coarsest refinement of ``seed`` stable under every translation
    ``i -> succ[i][a]`` — class ids per node, dense in first-appearance order.
    Each round appends the classes of all successors to each node's label; the
    class count is non-decreasing and bounded by ``len(succ)``, so the loop
    terminates. The Moore engine of both congruence levels: on the monoid's
    right table the fixpoint is the syntactic congruence (the seed components
    are right-invariant), on the letter maps of ``D`` it is state language
    equivalence."""
    labels = _canon(seed)
    while True:
        sigs: List[Tuple[int, Tuple[int, ...]]] = [
            (labels[i], tuple(labels[j] for j in succ[i]))
            for i in range(len(succ))
        ]
        new = _canon(sigs)
        if max(new) == max(labels):
            return new
        labels = new


def _canon(keys: Sequence[Hashable]) -> List[int]:
    """Dense ids in order of first appearance."""
    seen: Dict[Hashable, int] = {}
    out: List[int] = []
    for k in keys:
        if k not in seen:
            seen[k] = len(seen)
        out.append(seen[k])
    return out


__all__ = ["Profile", "residual_classes", "profile", "refine"]
