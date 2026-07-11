"""The kernel of ``S`` and one kernel idempotent.

``S`` is the class set without the adjoined identity. The two-sided
Cayley graph on ``S`` — edges ``c -> M(lambda(a), c)`` and
``c -> M(c, lambda(a))`` — has the ``J``-classes as its SCCs; the
``J``-order has a unique minimum, the kernel ``K`` (the minimal two-sided
ideal), which is the graph's unique sink SCC. Two sinks convict the
multiplication table as corrupted and raise. The idempotent returned is
``idem(t)`` for the least-keyed ``t in K`` (``K`` is closed under powers,
so it stays in ``K``).
"""
from __future__ import annotations

from typing import Dict, FrozenSet, Iterator, List, Tuple

from ..sos.invariant import Invariant
from .chain import assert_letters_leave_identity, least_key_class


def _two_sided_succs(inv: Invariant) -> Dict[int, List[int]]:
    """Successor lists of the two-sided Cayley graph on ``S``: for each
    non-identity class ``c``, the classes ``M(lambda(a), c)`` and
    ``M(c, lambda(a))`` over all letters, deduplicated and sorted. Asserts
    no product of non-identity classes reaches the identity (it is
    adjoined, so none may)."""
    letters = set(inv.letter_class)
    succs: Dict[int, List[int]] = {}
    for c in range(inv.n):
        if c == inv.identity:
            continue
        out = set()
        for x in letters:
            out.add(inv.mult[x][c])
            out.add(inv.mult[c][x])
        assert inv.identity not in out, (
            f"a product of non-identity classes hit the adjoined identity "
            f"(class {c}, n={inv.n})"
        )
        succs[c] = sorted(out)
    return succs


def _sccs(succs: Dict[int, List[int]]) -> List[List[int]]:
    """Strongly connected components of a graph given by successor lists,
    iterative Tarjan. Returns the components as vertex lists, in reverse
    topological order (every edge goes toward an earlier component or
    stays inside)."""
    index: Dict[int, int] = {}
    low: Dict[int, int] = {}
    on_stack: Dict[int, bool] = {}
    stack: List[int] = []
    comps: List[List[int]] = []
    counter = 0
    for root in succs:
        if root in index:
            continue
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack[root] = True
        work: List[Tuple[int, Iterator[int]]] = [(root, iter(succs[root]))]
        while work:
            v, it = work[-1]
            descended = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = counter
                    counter += 1
                    stack.append(w)
                    on_stack[w] = True
                    work.append((w, iter(succs[w])))
                    descended = True
                    break
                if on_stack.get(w):
                    low[v] = min(low[v], index[w])
            if descended:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[v])
            if low[v] == index[v]:
                comp: List[int] = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    comp.append(w)
                    if w == v:
                        break
                comps.append(comp)
    return comps


def kernel(inv: Invariant) -> FrozenSet[int]:
    """The kernel ``K`` of ``S``: the unique sink SCC of the two-sided
    Cayley graph on the non-identity classes. Raises if the sink is not
    unique (a corrupted table)."""
    assert_letters_leave_identity(inv)
    succs = _two_sided_succs(inv)
    comps = _sccs(succs)
    comp_of: Dict[int, int] = {}
    for i, comp in enumerate(comps):
        for v in comp:
            comp_of[v] = i
    sinks = [
        comp
        for i, comp in enumerate(comps)
        if all(comp_of[w] == i for v in comp for w in succs[v])
    ]
    assert len(sinks) == 1, (
        f"the two-sided Cayley graph has {len(sinks)} sink SCCs, expected "
        f"exactly one (n={inv.n}, ap={' '.join(inv.alphabet.aps) or '-'})"
    )
    return frozenset(sinks[0])


def kernel_idempotent(inv: Invariant) -> int:
    """One idempotent of the kernel: ``idem(t)`` for the least-keyed
    ``t in K``. Asserts idempotence and membership in ``K``."""
    ker = kernel(inv)
    t = least_key_class(inv, ker)
    k = inv.idempotent_power(t)
    assert inv.mult[k][k] == k, k
    assert k in ker, (k, sorted(ker))
    return k
