"""Structure helpers behind the daisystardet reachability read-off.

daisystardet peels a *rejecting* SCC whose entry-letter partition is
deterministic. These helpers detect that precondition and expose the per-state
guard data the read-off consumes:

* `init_scc_states` — the states of the initial SCC `C` daisystardet peels.
* `scc_data` — per-state `L` (⋁ guards entering the state within `C`), `O` (⋁ all
  out-guards) and `exits` (`state → [(guard, dst∉C)]`), in one edge pass.
* `is_deterministic` — `partscc`'s input-determinizing test on the `L`-partition.

The `A↓dst` rebase for an exit child is `aut2ltl.ltl.twa.reroot`.
"""

from typing import Dict, List, Optional, Set, Tuple

import spot
import buddy


__all__ = ["init_scc_states", "scc_data", "is_deterministic", "exit_word"]


def exit_word(
    aut: "spot.twa_graph", C: Set[int], h: int, dst: int
) -> Optional[List[str]]:
    """An EXACT word that traverses `C` from the hub `h` to an exit into `dst`: one
    path of in-`C` edges (self-loops skipped) reaching a state that carries an exit
    to `dst`, then that exit guard — with **every step's guard restricted to the
    letters enabling no edge to a different target** from its source. Under that
    restriction each step has a single continuation, so the word's left quotient IS
    the residue past the exit — what a witness lift needs (parallel edges to the
    same target are harmless: finite-prefix marks never touch an inf-set). Returns
    the restricted guards as Spot-syntax letter strings, or `None` when no exact
    path exists (every route's guards fully overlap other targets)."""
    d = aut.get_dict()

    def lit(cond: "buddy.bdd") -> str:
        return str(spot.bdd_to_formula(cond, d))

    def exact(cond: "buddy.bdd", src: int, target: int) -> "buddy.bdd":
        """`cond` minus every out-guard of `src` leading elsewhere than `target`."""
        for c, dd in [(e.cond, e.dst) for e in aut.out(src)]:
            if dd != target:
                cond = cond & buddy.bdd_not(c)
        return cond

    prev: Dict[int, Tuple[int, str]] = {}   # state -> (parent, exact guard reaching it)
    seen = {h}
    queue = [h]
    qi = 0
    while qi < len(queue):
        p = queue[qi]
        qi += 1
        for e in aut.out(p):                 # an exit p →(g) dst ends the word
            if e.dst == dst:
                g = exact(e.cond, p, dst)
                if g == buddy.bddfalse:
                    continue                 # this exit's letters all fork; try another
                word: List[str] = []
                cur = p
                while cur != h:
                    parent, guard = prev[cur]
                    word.append(guard)
                    cur = parent
                word.reverse()
                return word + [lit(g)]
        for e in aut.out(p):                 # else walk on through C (no self-loops)
            if e.dst in C and e.dst != p and e.dst not in seen:
                g = exact(e.cond, p, e.dst)
                if g == buddy.bddfalse:
                    continue                 # no exact letter for this step
                seen.add(e.dst)
                prev[e.dst] = (p, lit(g))
                queue.append(e.dst)
    return None


def init_scc_states(aut: "spot.twa_graph", h: int) -> Set[int]:
    """The states of the SCC containing the initial state `h` — the component `C`
    daisystardet peels."""
    si = spot.scc_info(aut)
    return {int(s) for s in si.states_of(si.scc_of(h))}


def scc_data(
    aut: "spot.twa_graph", C: Set[int], h: int
) -> Tuple[Dict[int, "buddy.bdd"], Dict[int, "buddy.bdd"],
          Dict[int, List[Tuple["buddy.bdd", int]]]]:
    """Per-state `L` (⋁ guards entering the state within `C`), `O` (⋁ all
    out-guards) and `exits` (`state → [(guard, dst∉C)]`), in one edge pass."""
    L = {p: buddy.bddfalse for p in C}
    O = {p: buddy.bddfalse for p in C}
    exits: Dict[int, List[Tuple["buddy.bdd", int]]] = {p: [] for p in C}
    for src in C:
        for e in aut.out(src):
            O[src] = O[src] | e.cond
            if e.dst in C:
                L[e.dst] = L[e.dst] | e.cond
            else:
                exits[src].append((e.cond, e.dst))
    return L, O, exits


def is_deterministic(L: Dict[int, "buddy.bdd"], h: int) -> bool:
    """The L-partition is deterministic iff each `L(p)` is tight (`⊊ true`, and
    non-empty except possibly the hub, which the anchor covers) and the `L(p)` are
    pairwise disjoint — `partscc`'s input-determinizing condition."""
    states = list(L)
    for p in states:
        if L[p] == buddy.bddtrue or (L[p] == buddy.bddfalse and p != h):
            return False
    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            if (L[states[i]] & L[states[j]]) != buddy.bddfalse:
                return False
    return True
