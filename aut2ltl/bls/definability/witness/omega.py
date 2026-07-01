"""
bls/definability/witness/omega.py — complete the Ω-POWER counting family shape.

The linear shape fails structurally when the orbit phases are residual-equal
(any prefix-independent language): the count, if genuine, lives in the
acceptance collected along the loop. This module searches for a return word
making membership of `u . (v^n . y)^w` toggle with `n mod p`.

Exact periodicity for ALL n is secured structurally, never sampled on faith:
the enriched powers of `v` close into a cycle (`E_v^{a+c} = E_v^a`, index `a`,
period `c`, `enriched.power_index_period`), and absorbing the index into the
tail — `ŷ = v^a . y` — makes `n ↦ [ (v^n . ŷ)^w from q ]` exactly `c`-periodic
from `n = 0`: equal enriched elements induce identical run skeletons, hence
equal lasso acceptance. The declared period is the minimal cyclic period of
that pattern over one `c`-cycle; non-constant ⟹ a genuine modular count.

Candidates `y` range over one shortest representative per enriched element
(`enriched.bfs_words`) — exhaustive modulo the caps below, which bound work:
truncation costs completeness, never soundness (nothing found ⟹ the caller
abstains, no verdict).
"""
from __future__ import annotations

from typing import Dict, List, TYPE_CHECKING

import spot

from aut2ltl.verifier import member
from .enriched import bfs_words, elem_of_factor, letter_elems, power_index_period
from .support import copy_with_init, induced_transform, min_cyclic_period, orbits, \
    valuation_to_letter, word_to

if TYPE_CHECKING:
    from aut2ltl.witness import Witness

_MAX_ELEMS = 512     # enriched elements enumerated as y-candidates
_MAX_QUERIES = 2048  # lasso membership queries per completion
_MAX_PERIOD = 64     # bound on the enriched index+period scan of v's powers


def complete_omega(
    w: "Witness",
    aut: "spot.twa_graph",
    gens: List[List[int]],
    valuations: List[Dict[str, bool]],
) -> bool:
    """Try to fill `w.u` / `w.y` / `w.p` (the ω-power shape). Anchors on each
    reachable cycle of `v`'s state action — falling back to the initial state
    when `v` has none: the enriched-power cycle, not the state orbit, is what
    carries the periodicity. True on success."""
    try:
        letters = letter_elems(aut, valuations)
    except Exception:
        return False
    ev = elem_of_factor(letters, w.factor)
    ip = power_index_period(ev, _MAX_PERIOD)
    if ip is None:
        return False
    a, c = ip
    if c <= 1:
        return False  # enriched powers stabilize: nothing counts along v

    names = [valuation_to_letter(val) for val in valuations]
    v_letters = [names[i - 1] for i in w.factor]
    t = induced_transform(gens, w.factor)
    init = aut.get_init_state_number()
    anchors = [cyc[0] for cyc in orbits(t)] or [init]

    budget = _MAX_QUERIES
    for q in anchors:
        u = word_to(gens, valuations, init, q)
        if u is None:
            continue
        aq = copy_with_init(aut, q)
        for y_word, _elem in bfs_words(letters, names, _MAX_ELEMS):
            if budget < c:
                return False
            yhat = v_letters * a + y_word
            pattern: List[bool] = []
            for n in range(c):
                budget -= 1
                lasso = "cycle{" + "; ".join(v_letters * n + yhat) + "}"
                pattern.append(member(aq, lasso))
            p = min_cyclic_period(pattern)
            if p > 1:
                w.u, w.y, w.p = u, yhat, p
                return True
    return False


__all__ = ["complete_omega"]
