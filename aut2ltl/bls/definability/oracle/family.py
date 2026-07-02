"""
bls/definability/oracle/family.py — the certificate: a counting family from a
separated pair of powers.

Given a group class of the quotient (the power ladder of `v`), the chased
separating word `b`, and the seed tables, assemble a `Witness` of the matching
shape:

  * a residual difference at slot `q`  →  linear family `u·vⁿ·x` with
    `x = b·w`, `w` an ultimately-periodic separator of the two residuals;
  * a profile difference at slot `q`   →  ω-power family `u·(vⁿ·y)^ω` with
    `y = b` — its membership pattern is a pure lookup in the profile table.

In both shapes `u` is a shortest word reaching `q` on the automaton, and the
power index is absorbed — into the anchor (`u ← u·vᵃ`) for the linear shape,
into the return word (`y ← vᵃ·y`) for the ω-power shape — so the declared
pattern is exactly periodic from `n = 0`. The declared period is the minimal
cyclic period of the membership pattern around one class cycle; it is
non-constant by construction (the chased pair differs), so `p > 1` always.
This module knows nothing of partitions: it consumes indices, tables and
words, and emits the floor value.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import spot

from aut2ltl.verifier import member
from aut2ltl.witness import Witness
from ..witness.support import copy_with_init, min_cyclic_period, valuation_to_letter, word_to
from .closure import Monoid
from .profile import Profile
from .quotient import Group
from .residuals import separator


def _walk(mon: Monoid, e: int, word: List[int]) -> int:
    """The element index of `elems[e] · word` via the right-translation table."""
    for li in word:
        e = mon.right[e][li]
    return e


def assemble(
    aut: "spot.twa_graph",
    gens: List[List[int]],
    valuations: List[Dict[str, bool]],
    mon: Monoid,
    lin: Sequence[Tuple[int, ...]],
    prof: Sequence[Profile],
    group: Group,
    b: List[int],
) -> Optional[Witness]:
    """The counting family for `group`, whose consecutive cycle powers
    `v^a, v^{a+1}` are separated by the word `b` (`seed(v^a·b) ≠ seed(v^{a+1}·b)`).
    Returns `None` only on an internal inconsistency — never asserts."""
    a, c = group.a, group.c
    e1 = _walk(mon, group.powers[a - 1], b)
    e2 = _walk(mon, group.powers[a], b)

    names = [valuation_to_letter(v) for v in valuations]
    v_word = mon.rep[group.v]
    v_letters = [names[li] for li in v_word]
    b_letters = [names[li] for li in b]
    factor = [li + 1 for li in v_word]
    init = aut.get_init_state_number()

    # The base difference names the shape: residuals first, then profiles.
    lin_diff = next((q for q in range(len(lin[e1])) if lin[e1][q] != lin[e2][q]), None)
    if lin_diff is not None:
        q = lin_diff
        u0 = word_to(gens, valuations, init, q)
        if u0 is None:
            return None
        sep = separator(aut, mon.elems[e1][q][0], mon.elems[e2][q][0])
        if sep is None:
            return None
        w_prefix, w_cycle = sep
        lasso = "; ".join(w_prefix + ["cycle{" + "; ".join(w_cycle) + "}"])
        pattern: List[bool] = []
        for n in range(c):
            eb = _walk(mon, group.powers[a + n - 1], b)
            pattern.append(member(copy_with_init(aut, mon.elems[eb][q][0]), lasso))
        p = min_cyclic_period(pattern)
        if p <= 1:
            return None
        return Witness(p=p, v=v_letters, factor=factor, u=u0 + v_letters * a,
                       x_prefix=b_letters + w_prefix, x_cycle=w_cycle)

    prof_diff = next((q for q in range(len(prof[e1])) if prof[e1][q] != prof[e2][q]), None)
    if prof_diff is None:
        return None  # the chase said the seeds differ; unreachable
    q = prof_diff
    u0 = word_to(gens, valuations, init, q)
    if u0 is None:
        return None
    pattern = [prof[_walk(mon, group.powers[a + n - 1], b)][q] for n in range(c)]
    p = min_cyclic_period(pattern)
    if p <= 1:
        return None
    return Witness(p=p, v=v_letters, factor=factor, u=u0,
                   y=v_letters * a + b_letters)


__all__ = ["assemble"]
