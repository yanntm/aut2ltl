"""Independent measure oracle on a deterministic complete EL automaton.

Computes ``mu_p`` of the language of a `.hoa` automaton — deterministic,
complete, Emerson–Lei acceptance on transitions — under a full-support
rational Bernoulli ``p`` on the letter masks, sharing nothing with the
invariant-side measure but the linear solver (see algorithm.md §5).
The automaton's run under ``p`` is a finite Markov chain on its states;
a run absorbed in a bottom SCC a.s. traverses every edge of it
infinitely often, so each bottom SCC accepts iff the EL condition
evaluates true on its edges' acceptance marks, and ``mu`` is the
theta-weighted absorption vector of the same transient system.

Spot is used to parse the automaton and expose its acceptance
condition, nothing else. This module is deliberately NOT exported by
the package ``__init__``: importers of the measure path never load
Spot.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, List, Optional, Set, Tuple

import buddy
import spot

from ..sos.alphabet import Alphabet, Letter
from .kernel import _sccs
from .measure import _solve, _validate_p


@dataclass(frozen=True)
class RouteAResult:
    """The oracle's verdict on one automaton and one ``p``: the exact
    measure, the state count, and per bottom SCC (sorted by least state
    id) its acceptance bit and its absorption probability from the
    initial state."""

    value: Fraction
    n_states: int
    bits: Tuple[bool, ...]
    absorption: Tuple[Fraction, ...]


def _letter_bdds(aut: "spot.twa_graph", alphabet: Alphabet) -> List[object]:
    """One BDD minterm per letter mask, in mask order: the conjunction of
    every proposition or its negation per the mask's bits (``aps[i]`` on
    bit ``k-1-i``). Asserts the automaton's AP set equals the alphabet's."""
    hoa_aps = {str(f) for f in aut.ap()}
    assert hoa_aps == set(alphabet.aps), (sorted(hoa_aps), alphabet.aps)
    k = len(alphabet.aps)
    var = [buddy.bdd_ithvar(aut.register_ap(name)) for name in alphabet.aps]
    out: List[object] = []
    for a in alphabet.letters():
        b = buddy.bddtrue
        for i in range(k):
            lit = var[i] if (a >> (k - 1 - i)) & 1 else buddy.bdd_not(var[i])
            b = buddy.bdd_and(b, lit)
        out.append(b)
    return out


def route_a(
    hoa_path: str,
    alphabet: Alphabet,
    p: Optional[Dict[Letter, Fraction]] = None,
) -> RouteAResult:
    """The exact measure of the language of the deterministic complete
    EL automaton at ``hoa_path``, under the Bernoulli measure ``p``
    (default uniform) over ``alphabet``'s letter masks. Asserts
    determinism and completeness letterwise (exactly one successor per
    state and letter) and that the absorption vector sums to 1."""
    aut = spot.automaton(hoa_path)
    if p is None:
        p = {a: Fraction(1, alphabet.size) for a in alphabet.letters()}
    _validate_p(alphabet, p)
    letters = alphabet.letters()
    lbdds = _letter_bdds(aut, alphabet)
    n = int(aut.num_states())
    succ: List[List[int]] = [[-1] * len(letters) for _ in range(n)]
    state_marks: List[Set[int]] = [set() for _ in range(n)]
    for s in range(n):
        for e in aut.out(s):
            for i, lb in enumerate(lbdds):
                if buddy.bdd_and(e.cond, lb) != buddy.bddfalse:
                    assert succ[s][i] == -1, f"nondeterministic at state {s}"
                    succ[s][i] = int(e.dst)
            state_marks[s] |= set(e.acc.sets())
        assert -1 not in succ[s], f"incomplete at state {s}"

    comps = _sccs({s: sorted(set(succ[s])) for s in range(n)})
    comp_of: Dict[int, int] = {s: i for i, c in enumerate(comps) for s in c}
    bottoms = [
        sorted(c)
        for i, c in enumerate(comps)
        if all(comp_of[d] == i for s in c for d in succ[s])
    ]
    bottoms.sort(key=lambda c: c[0])
    acc = aut.acc()
    bits = tuple(
        bool(acc.accepting(spot.mark_t(sorted(set().union(*(state_marks[s] for s in scc))))))
        for scc in bottoms
    )

    where: Dict[int, int] = {s: j for j, scc in enumerate(bottoms) for s in scc}
    init = int(aut.get_init_state_number())
    zero = Fraction(0)
    if init in where:
        absorption = tuple(
            Fraction(1) if j == where[init] else zero for j in range(len(bottoms))
        )
    else:
        transient = [s for s in range(n) if s not in where]
        idx = {s: i for i, s in enumerate(transient)}
        a_mat = [[zero] * len(transient) for _ in transient]
        b_mat = [[zero] * len(bottoms) for _ in transient]
        for s in transient:
            i = idx[s]
            a_mat[i][i] += 1
            for li, a in enumerate(letters):
                d = succ[s][li]
                if d in idx:
                    a_mat[i][idx[d]] -= p[a]
                else:
                    b_mat[i][where[d]] += p[a]
        absorption = tuple(_solve(a_mat, b_mat)[idx[init]])
    assert sum(absorption, zero) == 1, absorption
    value = sum((absorption[j] for j, bit in enumerate(bits) if bit), zero)
    return RouteAResult(
        value=value, n_states=n, bits=bits, absorption=absorption
    )
