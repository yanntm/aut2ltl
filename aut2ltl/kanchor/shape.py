"""Structure helpers behind the `anchor` combinator (see algorithm.md).

anchor peels the SCC `C` of the initial state when the component's phase — the
state occupied while the run remains inside `C` — is recoverable from the last
anchor letter. These helpers expose the per-state guard data the read-off
consumes and decide that precondition:

* `init_scc_states` — the states of `C`, the SCC of the initial state.
* `lame_data` — the per-state L/A/M/E split by *identifiability* (algorithm.md,
  layer 4): `A` (Anchor letters — every letter whose in-`C` occurrences all
  land at `s`, entering edges and promoted self-loops alike), `L` (the
  necessary Loop letters only — stay letters shared with another state's loops
  or anchors, which no stateless observer can attribute), `M` (Move letters,
  in-`C` non-self out-guards) and `exits` (`state → [(guard, dst ∉ C)]`).
* `anchored_violation` — the precondition test: P1 (anchors pairwise disjoint)
  and P2 (a loop letter fires no foreign anchor). Returns the reason a test
  fails, or `None` when the component is anchored.
* `reroot` — the `A↓dst` rebase handing an exit target to a child.

All guard work is symbolic (BDD conjunctions against `bddfalse`): no letter
enumeration, cost quadratic in `|C|` and linear in the edges.
"""

from typing import Dict, List, Optional, Set, Tuple

import spot
import buddy

__all__ = ["init_scc_states", "lame_data", "anchored_violation", "reroot"]

# The L/A/M/E data of a component: per-state Loop / Anchor / Move guard
# disjunctions (BDDs) and the exit list `state -> [(guard, dst)]`.
LameData = Tuple[
    Dict[int, "buddy.bdd"], Dict[int, "buddy.bdd"], Dict[int, "buddy.bdd"],
    Dict[int, List[Tuple["buddy.bdd", int]]],
]


def init_scc_states(aut: "spot.twa_graph", q0: int) -> Set[int]:
    """The states of the SCC containing the initial state `q0` — the component
    `C` anchor peels. Being initial, `C` has no incoming edge from outside."""
    si = spot.scc_info(aut)
    return {int(s) for s in si.states_of(si.scc_of(q0))}


def lame_data(aut: "spot.twa_graph", C: Set[int]) -> LameData:
    """The L/A/M/E split of `C`: one edge pass, then the identifiability
    promotion. For each state `s ∈ C`: `L[s] = ⋁` self-loop guards,
    `A[s] = ⋁` guards entering `s` from another `C`-state, `M[s] = ⋁` guards
    leaving `s` toward another `C`-state, and `exits[s] = [(g, dst)]` for the
    edges leaving `C`. Then a loop letter whose every in-`C` occurrence is at
    `s` — foreign to every other state's loops and anchors — names its state
    and is **promoted** from `L[s]` into `A[s]`: `L[s]` keeps only the
    necessary stay letters, and every window width consuming this split
    inherits the correction (algorithm.md, layer 4)."""
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
    for s in C:
        foreign = buddy.bddfalse
        for t in C:
            if t != s:
                foreign = foreign | L[t] | A[t]
        promoted = L[s] - foreign
        if promoted != buddy.bddfalse:
            # Both faces of the promotion: trigger side (the letter anchors s —
            # fires s's own row) and consequence side (a unit re-entry ends a
            # sojourn exactly as a move does, so it must be a legal stay-ender).
            A[s] = A[s] | promoted
            M[s] = M[s] | promoted
            L[s] = L[s] - promoted
    return L, A, M, exits


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


def reroot(aut: "spot.twa_graph", state: int) -> "spot.twa_graph":
    """A fresh copy of `aut` rooted at `state` and trimmed to the states
    reachable from it — the sub-automaton `A↓state`, whose language is exactly
    what is accepted from `state`. Does not mutate `aut`."""
    sub = spot.automaton(aut.to_str("hoa"))
    sub.set_init_state(state)
    sub.purge_unreachable_states()
    return sub
