"""Structure helpers behind the `anchor` combinator (see algorithm.md).

anchor peels the SCC `C` of the initial state when the component's phase — the
state occupied while the run remains inside `C` — is recoverable from the last
anchor letter. These helpers expose the per-state guard data the read-off
consumes and decide that precondition:

* `init_scc_states` — the states of `C`, the SCC of the initial state.
* `lame_data` — the raw per-state L/A/M/E split plus the promoted guards
  (algorithm.md, layer 4): `L` (Loop letters, self-loop guards), `A` (Anchor
  letters, in-`C` non-self in-guards), `M` (Move letters, in-`C` non-self
  out-guards), `exits` (`state → [(guard, dst ∉ C)]`), and `P` — per state,
  the part of `L[s]` occurring nowhere else in `C`, whose self-loop is
  reclassified as the entering edge `(s, P[s], s)` of the set `δ↑`. The
  split is returned raw: each window level applies the reclassification in
  its own form (the k = 1 split surgery, the k ≥ 2 pseudo-edges).
* `anchored_violation` — the precondition test: P1 (anchors pairwise disjoint)
  and P2 (a loop letter fires no foreign anchor). Returns the reason a test
  fails, or `None` when the component is anchored.

All guard work is symbolic (BDD conjunctions against `bddfalse`): no letter
enumeration, cost quadratic in `|C|` and linear in the edges.
"""

from typing import Dict, List, Optional, Set, Tuple

import spot
import buddy

__all__ = ["init_scc_states", "lame_data", "anchored_violation"]

# The L/A/M/E data of a component: per-state Loop / Anchor / Move guard
# disjunctions (BDDs), the exit list `state -> [(guard, dst)]`, and the
# per-state promoted guard `P` (the loop letters reclassified as entering
# edges of `δ↑`).
LameData = Tuple[
    Dict[int, "buddy.bdd"], Dict[int, "buddy.bdd"], Dict[int, "buddy.bdd"],
    Dict[int, List[Tuple["buddy.bdd", int]]], Dict[int, "buddy.bdd"],
]


def init_scc_states(aut: "spot.twa_graph", q0: int) -> Set[int]:
    """The states of the SCC containing the initial state `q0` — the component
    `C` anchor peels. Being initial, `C` has no incoming edge from outside."""
    si = spot.scc_info(aut)
    return {int(s) for s in si.states_of(si.scc_of(q0))}


def lame_data(aut: "spot.twa_graph", C: Set[int]) -> LameData:
    """The raw L/A/M/E split of `C` plus the promoted guards: one edge pass,
    then the identifiability test. For each state `s ∈ C`: `L[s] = ⋁`
    self-loop guards, `A[s] = ⋁` guards entering `s` from another `C`-state,
    `M[s] = ⋁` guards leaving `s` toward another `C`-state, and
    `exits[s] = [(g, dst)]` for the edges leaving `C`. `P[s]` is the part of
    `L[s]` foreign to every other state's loops and anchors — letters whose
    every in-`C` occurrence is at `s`, so reading one names the state; their
    self-loop is reclassified as the entering edge `(s, P[s], s)` of `δ↑`
    (algorithm.md, layer 4). The split itself is left raw."""
    L = {s: buddy.bddfalse for s in C}
    A = {s: buddy.bddfalse for s in C}
    M = {s: buddy.bddfalse for s in C}
    exits: Dict[int, List[Tuple["buddy.bdd", int]]] = {s: [] for s in C}
    for src in C:
        for e in aut.out(src):
            if e.dst == src:
                L[src] = L[src] | e.cond
            elif e.dst in C:
                A[e.dst] = A[e.dst] | e.cond
                M[src] = M[src] | e.cond
            else:
                exits[src].append((e.cond, e.dst))
    P = {s: buddy.bddfalse for s in C}
    for s in C:
        foreign = buddy.bddfalse
        for t in C:
            if t != s:
                foreign = foreign | L[t] | A[t]
        P[s] = L[s] - foreign
    return L, A, M, exits, P


def anchored_violation(
    L: Dict[int, "buddy.bdd"], A: Dict[int, "buddy.bdd"]
) -> Optional[str]:
    """The anchored-phase precondition (algorithm.md P1 + P2): `None` when it
    holds, else a one-line reason.

    * P1 — anchors partition: `A(s) ∧ A(t) = false` for `s ≠ t`.
    * P2 — loop letters fire no foreign anchor: `L(s) ∧ A(t) = false` for
      `s ≠ t` (`s = t` is exempt: a letter both looping at `s` and entering `s`
      lands the run at `s` under every reading).

    Tightness needs no test: it is derived from P1 and strong connectivity."""
    states = list(A)
    for i, s in enumerate(states):
        for j, t in enumerate(states):
            if s == t:
                continue
            if j > i and (A[s] & A[t]) != buddy.bddfalse:
                return f"P1: anchors of states {s} and {t} overlap"
            if (L[s] & A[t]) != buddy.bddfalse:
                return f"P2: a loop letter of state {s} fires the anchor of state {t}"
    return None


