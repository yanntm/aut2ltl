"""aut2ltl.twa — copying and re-rooting a Spot automaton without going through HOA.

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

Spot-facing, so it does not belong under `ltl/`; a floor module, because the
alternative is each subpackage carrying its own copy of a Spot subtlety.
"""
from __future__ import annotations

import spot


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
