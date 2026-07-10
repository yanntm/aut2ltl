"""Daisy structure helpers behind the `daisy` combinator.

A **daisy** is the initial state `q` whose only incoming edges are self-loops: a
center with **petals** (self-loops `q → q`) and **stems** (exits `q → dst ≠ q`).
`is_daisy` is the accept/decline test (purely local to `q`'s incoming edges);
`split` partitions `q`'s out-edges into petals (guard + acceptance sets) and stems
(guard + target); `reroot` builds `A↓dst`, the sub-automaton rooted at a stem target
that becomes the unit of child delegation. See algorithm.md.
"""

from typing import FrozenSet, List, Tuple

import spot

from aut2ltl.twa import clone

# A petal is a self-loop's (guard, acceptance sets); a stem is an exit's
# (guard, destination state).
Petal = Tuple["spot.formula", FrozenSet[int]]
Stem = Tuple["spot.formula", int]


def is_daisy(aut: "spot.twa_graph", q: int) -> bool:
    """True iff `q`'s only incoming edges are self-loops — the negation of "some
    state other than `q` has an edge into `q`". Necessary and sufficient (the
    automaton is reachable from its initial state) and purely local to `q`'s incoming
    edges: it already guarantees every stem strictly descends, so a return path would
    show up here as a non-self incoming edge."""
    for s in range(aut.num_states()):
        if s == q:
            continue  # self-loops do not count as "incoming" for the daisy test
        for e in aut.out(s):
            if e.dst == q:
                return False
    return True


def split(aut: "spot.twa_graph", q: int) -> Tuple[List[Petal], List[Stem]]:
    """Partition `q`'s out-edges into petals (self-loops `q → q`, each with its
    acceptance sets) and stems (exits `q → dst ≠ q`, each with its target). Guards
    are returned as `spot.formula`s; stem order is preserved (children are zipped
    against it)."""
    bdict = aut.get_dict()
    petals: List[Petal] = []
    stems: List[Stem] = []
    for e in aut.out(q):
        guard = spot.bdd_to_formula(e.cond, bdict)
        if e.dst == q:
            petals.append((guard, frozenset(e.acc.sets())))
        else:
            stems.append((guard, e.dst))
    return petals, stems


def reroot(aut: "spot.twa_graph", state: int) -> "spot.twa_graph":
    """A fresh copy of `aut` rooted at `state` and trimmed to the states reachable
    from it — the sub-automaton `A↓state`, whose language is exactly what is accepted
    from `state`. Does not mutate `aut`."""
    sub = clone(aut)
    sub.set_init_state(state)
    sub.purge_unreachable_states()
    return sub
