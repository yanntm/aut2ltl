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
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

import buddy
import spot

from ..sos.alphabet import Alphabet, Letter
from .kernel import _sccs
from .mc import Chain
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


def _read_det(
    aut: "spot.twa_graph", alphabet: Alphabet
) -> Tuple[List[List[int]], List[List[FrozenSet[int]]]]:
    """The letterwise transition function and edge marks of a deterministic
    complete automaton: ``succ[s][i]`` and ``marks[s][i]`` for letter mask
    ``i``. Asserts determinism and completeness (exactly one successor per
    state and letter)."""
    n = int(aut.num_states())
    size = alphabet.size
    lbdds = _letter_bdds(aut, alphabet)
    succ: List[List[int]] = [[-1] * size for _ in range(n)]
    marks: List[List[FrozenSet[int]]] = [
        [frozenset()] * size for _ in range(n)
    ]
    for s in range(n):
        for e in aut.out(s):
            acc = frozenset(e.acc.sets())
            for i, lb in enumerate(lbdds):
                if buddy.bdd_and(e.cond, lb) != buddy.bddfalse:
                    assert succ[s][i] == -1, f"nondeterministic at state {s}"
                    succ[s][i] = int(e.dst)
                    marks[s][i] = acc
        assert -1 not in succ[s], f"incomplete at state {s}"
    return succ, marks


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
    n = int(aut.num_states())
    succ, marks = _read_det(aut, alphabet)
    state_marks: List[Set[int]] = [
        set().union(*marks[s]) if marks[s] else set() for s in range(n)
    ]

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


def route_a_chain(hoa_path: str, ch: Chain) -> RouteAResult:
    """The exact ``Pr_M(L)`` of the chain ``ch`` against the deterministic
    complete EL automaton at ``hoa_path`` — the product-side oracle. The
    product ``states(M) x states(A)`` starts at ``(q0, delta(a0, l(q0)))``
    (the initial state's letter is consumed at once, the word semantics of
    `mc`) and steps ``(q, s) -> (q', delta(s, l(q')))`` with the chain's
    probability. In a bottom SCC every product edge recurs infinitely often
    a.s., so the run's limit mark set is the union of the marks of the SCC's
    edges and the EL condition on it is the SCC's verdict; the absorption
    probabilities are the same exact transient system as `route_a`."""
    aut = spot.automaton(hoa_path)
    ch.validate()
    succ, marks = _read_det(aut, ch.alphabet)
    init = (ch.init, succ[int(aut.get_init_state_number())][ch.label[ch.init]])

    edges: Dict[Tuple[int, int], List[Tuple[Tuple[int, int], Fraction, FrozenSet[int]]]] = {}
    stack = [init]
    while stack:
        st = stack.pop()
        if st in edges:
            continue
        q, s = st
        out = []
        for q2, pr in ch.trans[q]:
            a = ch.label[q2]
            d = (q2, succ[s][a])
            out.append((d, pr, marks[s][a]))
            if d not in edges:
                stack.append(d)
        edges[st] = out

    states = sorted(edges)
    idx = {st: i for i, st in enumerate(states)}
    adj = {i: sorted({idx[d] for d, _, _ in edges[st]}) for i, st in enumerate(states)}
    comps = _sccs(adj)
    comp_of: Dict[int, int] = {v: i for i, c in enumerate(comps) for v in c}
    bottoms = [
        sorted(c)
        for i, c in enumerate(comps)
        if all(comp_of[w] == i for v in c for w in adj[v])
    ]
    bottoms.sort(key=lambda c: states[c[0]])
    acc = aut.acc()
    bits = tuple(
        bool(
            acc.accepting(
                spot.mark_t(
                    sorted(
                        set().union(
                            *(
                                m
                                for v in scc
                                for _, _, m in edges[states[v]]
                            )
                        )
                    )
                )
            )
        )
        for scc in bottoms
    )

    where: Dict[int, int] = {v: j for j, scc in enumerate(bottoms) for v in scc}
    zero = Fraction(0)
    i0 = idx[init]
    if i0 in where:
        absorption = tuple(
            Fraction(1) if j == where[i0] else zero for j in range(len(bottoms))
        )
    else:
        transient = [i for i in range(len(states)) if i not in where]
        row_of = {v: r for r, v in enumerate(transient)}
        a_mat = [[zero] * len(transient) for _ in transient]
        b_mat = [[zero] * len(bottoms) for _ in transient]
        for v in transient:
            r = row_of[v]
            a_mat[r][r] += 1
            for d, pr, _ in edges[states[v]]:
                j = idx[d]
                if j in row_of:
                    a_mat[r][row_of[j]] -= pr
                else:
                    b_mat[r][where[j]] += pr
        absorption = tuple(_solve(a_mat, b_mat)[row_of[i0]])
    assert sum(absorption, zero) == 1, absorption
    value = sum((absorption[j] for j, bit in enumerate(bits) if bit), zero)
    return RouteAResult(
        value=value, n_states=len(states), bits=bits, absorption=absorption
    )
