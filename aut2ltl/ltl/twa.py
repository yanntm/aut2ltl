"""aut2ltl.ltl.twa — copying and re-rooting a Spot automaton without going through HOA.

`spot.automaton(aut.to_str("hoa"))` looks like a deep copy and is not one. It
serializes and reparses, so every property the text does not carry is *re-inferred
by the parser* rather than copied: a source with `complete=maybe` comes back
`complete=yes`, and one whose `state_acc` was deliberately cleared comes back
`state_acc=yes`, because the printer re-declares state-based acceptance whenever
it can. Algorithms that branch on those properties then see an automaton that is
not the one they meant to copy. It is also far more expensive than a graph copy.

Spot's own clone is `make_twa_graph(aut, prop_set)`, which copies the graph and
exactly the properties named by `prop_set` (Spot uses it internally, in
`ensure_digraph`).

`clone` preserves everything, for a copy that is only re-rooted or trimmed.
`clone_structural` drops the two properties an acceptance rewrite invalidates —
state-based acceptance and inherent weakness — leaving them to be re-derived,
while keeping the ones a rewrite cannot disturb. `reroot` is the copy-then-trim
those callers actually want.

`dump_hoa` is the canonical serialization. `aut.to_str("hoa")` is not a normal
form: it re-declares state-based acceptance whenever it can — even after
`prop_state_acc` was cleared — and lists the atomic propositions in the bdd
dictionary's variable order, so two Spot builds emit different bytes for one
automaton. `dump_hoa` forces the acceptance onto the edges, registers the APs in
name order on a fresh dictionary, and then renumbers the states with
`canon.normalize`. The AP pass runs first: `canon.normalize` orders successors by
the *printed* edge condition, so its result is fixed only once the AP names are.
"""
from __future__ import annotations

import spot

from aut2ltl.ltl import canon


def clone(aut: "spot.twa_graph") -> "spot.twa_graph":
    """An independent copy of `aut`, every property preserved."""
    return spot.make_twa_graph(aut, spot.twa_prop_set.all())


def clone_structural(aut: "spot.twa_graph") -> "spot.twa_graph":
    """An independent copy of `aut` for a caller about to change its acceptance.

    Keeps determinism, completeness and stutter invariance — none of which an
    acceptance rewrite can invalidate — and drops state-based acceptance and
    inherent weakness, which it can.
    """
    keep = spot.twa_prop_set(False,   # state_based:     acceptance may move to edges
                             False,   # inherently_weak: depends on the condition
                             True,    # deterministic
                             False,   # improve_det
                             True,    # complete
                             True)    # stutter_inv
    return spot.make_twa_graph(aut, keep)


def reroot(aut: "spot.twa_graph", state: int) -> "spot.twa_graph":
    """A fresh copy of `aut` rooted at `state` and trimmed to the states reachable
    from it — the sub-automaton `A↓state`, whose language is exactly what is
    accepted from `state`. Does not mutate `aut`."""
    sub = clone(aut)
    sub.set_init_state(state)
    sub.purge_unreachable_states()
    return sub


def ap_canonical(aut: "spot.twa_graph") -> "spot.twa_graph":
    """A copy of `aut` whose atomic propositions are registered in name order.

    Built on a **fresh** bdd dictionary, because the order the HOA printer indexes
    is the dictionary's variable order, not the automaton's AP list: re-registering
    onto the source's own dictionary reorders the list and emits the same bytes.
    Each edge condition is therefore carried across as a formula and rebuilt
    against the new dictionary, where the variable numbers follow the names.
    """
    res = spot.make_twa_graph(spot.make_bdd_dict())
    for p in sorted(aut.ap(), key=lambda f: f.ap_name()):
        res.register_ap(p)
    res.new_states(aut.num_states())
    res.set_init_state(aut.get_init_state_number())
    res.copy_acceptance_of(aut)
    src = aut.get_dict()
    for e in aut.edges():
        cond = spot.formula_to_bdd(spot.bdd_to_formula(e.cond, src), res.get_dict(), res)
        res.new_edge(e.src, e.dst, cond, e.acc)
    res.prop_copy(aut, spot.twa_prop_set.all())
    return res


def dump_hoa(aut: "spot.twa_graph") -> str:
    """`aut` as canonical HOA: APs in name order, states renumbered, acceptance on
    the transitions. A function of the automaton, not of the Spot build.

    Idempotent. Nothing here determinizes: serialization normalizes a presentation,
    and obtaining the presentation worth serializing is the caller's business.
    `canon.normalize` is exact on a deterministic automaton (the edge condition
    picks the successor, so its successor order cannot tie) and heuristic
    otherwise, as its own docstring says.
    """
    return canon.normalize(ap_canonical(aut)).to_str("hoa", "t")
