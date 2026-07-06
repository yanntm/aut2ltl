"""Read the residual (right-congruence) automaton off a known automaton.

The right congruence ``u ~ v  <=>  u^{-1}L = v^{-1}L`` collapses the states of a
deterministic automaton onto its residual classes; this reads that quotient and
keys it canonically — residuals numbered by shortlex-least reaching word in the
sosl alphabet's mask order (so the numbering is presentation-independent, like an
invariant's), ``id 0`` = ``eps``.

Automaton-side and aut2ltl-backed, like `builder`; the learner never calls it.
Its output is the optional trailer of a `.sos` figure export (see
`sos.io.serialize.dump_invariant`'s ``residuals`` parameter).
"""
from __future__ import annotations

from collections import deque
from typing import Dict, List, Tuple

from aut2ltl.bls.definability.generators import extract_generators
from aut2ltl.bls.definability.oracle.residuals import state_classes
from tests.probes.dg_common import quotient_of_hoa

from ..alphabet import EMPTY, Alphabet, Word
from ..residuals import Residuals
from .builder import ReferenceError


def residuals_of_hoa(path: str) -> Residuals:
    """The canonical `Residuals` of the language of HOA file ``path``."""
    data = quotient_of_hoa(path)
    if data is None:
        raise ReferenceError(f"algebra closure exceeded cap for {path}")
    aut, mon = data.aut, data.mon

    alphabet = Alphabet.of(ap.ap_name() for ap in aut.ap())
    # sosl letter mask -> the monoid's own letter index li (same recovery as the
    # builder: valuations are in li order).
    _gens, _masks, valuations = extract_generators(aut)
    li_of_mask: List[int] = [0] * alphabet.size
    for li, val in enumerate(valuations):
        trues = [ap for ap, truth in val.items() if truth]
        li_of_mask[alphabet.letter_of(trues)] = li

    st_cls = state_classes(aut)               # automaton state -> residual id

    def step_state(state: int, mask: int) -> int:
        # element 0 of the closed monoid is the identity, so right-multiplying
        # it by letter li yields the letter element; its st-part at `state` is
        # the automaton successor delta(state, letter).
        li = li_of_mask[mask]
        return mon.elems[mon.right[0][li]][state][0]

    # BFS from the initial residual, letters in mask order => shortlex-least keys.
    canon: Dict[int, int] = {st_cls[data.init]: 0}
    keys: Dict[int, Word] = {0: EMPTY}
    rep_state: Dict[int, int] = {0: data.init}
    queue: deque = deque([0])
    nxt = 1
    while queue:
        r = queue.popleft()
        for mask in range(alphabet.size):
            rp = st_cls[step_state(rep_state[r], mask)]
            if rp not in canon:
                canon[rp] = nxt
                keys[nxt] = keys[r] + (mask,)
                rep_state[nxt] = step_state(rep_state[r], mask)
                queue.append(nxt)
                nxt += 1

    delta: List[Tuple[int, ...]] = [
        tuple(canon[st_cls[step_state(rep_state[r], mask)]]
              for mask in range(alphabet.size))
        for r in range(nxt)
    ]
    return Residuals(keys=tuple(keys[r] for r in range(nxt)), delta=tuple(delta))
