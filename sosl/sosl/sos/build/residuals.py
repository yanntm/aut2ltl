"""Read the residual (right-congruence) automaton off a known automaton.

The right congruence ``u ~ v  <=>  u^{-1}L = v^{-1}L`` collapses the states of a
deterministic automaton onto its residual classes; this reads that quotient and
keys it canonically — residuals numbered by shortlex-least reaching word in the
alphabet's mask order (so the numbering is presentation-independent, like an
invariant's), ``id 0`` = ``eps``.

Automaton-side and core-backed, like `builder`; the learner never calls it.
Its output is the optional trailer of a `.sos` figure export (see
`sos.io.serialize.dump_invariant`'s ``residuals`` parameter).
"""
from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Tuple

from ..alphabet import EMPTY, Alphabet, Word
from ..core.closure import Monoid, close
from ..core.congruence import Profile, profile, residual_classes
from ..core.enriched import Elem, letter_elems
from ..residuals import Residuals
from .importer import import_hoa


def residuals_of_hoa(path: str, cap: int = 20000) -> Residuals:
    """The canonical `Residuals` of the language of HOA file ``path``.

    The state partition is the core's (`residual_classes` off the closed
    monoid's loop verdicts), so this raises ``ValueError`` when the monoid
    closure blows ``cap`` — callers only ask for residuals of languages whose
    invariant was constructible."""
    aut = import_hoa(path)
    alphabet = Alphabet.of(ap.ap_name() for ap in aut.ap())
    letters: List[Elem] = letter_elems(aut, alphabet)
    mon: Optional[Monoid] = close(letters, aut.num_states(), cap)
    if mon is None:
        raise ValueError(f"{path}: monoid closure blew the cap ({cap})")
    prof: List[Profile] = [profile(aut.acc(), el) for el in mon.elems]
    st_cls: List[int] = residual_classes(mon, prof)   # state -> residual id
    init: int = aut.get_init_state_number()

    def step_state(state: int, mask: int) -> int:
        return letters[mask][state][0]            # delta(state, letter)

    # BFS from the initial residual, letters in mask order => shortlex-least keys.
    canon: Dict[int, int] = {st_cls[init]: 0}
    keys: Dict[int, Word] = {0: EMPTY}
    rep_state: Dict[int, int] = {0: init}
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
