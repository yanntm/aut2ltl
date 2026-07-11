"""Bottom SCCs of the right-Cayley graph of an invariant.

The right-Cayley graph has the classes as vertices and one edge
``c -> M(c, lambda(a))`` per letter. A bottom SCC is a strongly connected
component with no edge leaving it; the components are computed by the
calculus's Tarjan pass, reused. Bottom SCCs are returned in a canonical
order: sorted by the shortlex key of their least class.
"""
from __future__ import annotations

from typing import Dict, FrozenSet, Iterable, List

from ..sos.alphabet import shortlex_key
from ..sos.calculus.surgery import _right_cayley_sccs
from ..sos.calculus.table import Table
from ..sos.invariant import Invariant


def assert_letters_leave_identity(inv: Invariant) -> None:
    """Assert ``lambda(a) != [eps]`` for every letter: the identity is the
    *adjoined* unit, the class of the empty word only, so no single letter
    (hence no nonempty word) may fold to it. Raises AssertionError naming
    the offending letter mask."""
    for a, c in enumerate(inv.letter_class):
        assert c != inv.identity, (
            f"letter mask {a} folds to the adjoined identity "
            f"(n={inv.n}, ap={' '.join(inv.alphabet.aps) or '-'})"
        )


def least_key_class(inv: Invariant, classes: Iterable[int]) -> int:
    """The class of ``classes`` whose key is shortlex-least."""
    return min(classes, key=lambda c: shortlex_key(inv.keys[c]))


def right_cayley_edges(inv: Invariant) -> Dict[int, List[int]]:
    """The right-Cayley successor lists: ``c -> [M(c, lambda(a)) for a in
    Sigma]``, one entry per letter in mask order (duplicates kept, so the
    list index is the letter)."""
    return {
        c: [inv.mult[c][x] for x in inv.letter_class] for c in range(inv.n)
    }


def bottom_sccs(inv: Invariant) -> List[FrozenSet[int]]:
    """The bottom SCCs of the right-Cayley graph on all classes (the
    identity included as a vertex), sorted by the shortlex key of their
    least class. Asserts: no letter folds to the identity, the identity
    lies in no bottom SCC, and at least one bottom SCC exists."""
    assert_letters_leave_identity(inv)
    comp, ncomp = _right_cayley_sccs(Table.of(inv))
    members: List[List[int]] = [[] for _ in range(ncomp)]
    leaves: List[bool] = [False] * ncomp
    letters = set(inv.letter_class)
    for c in range(inv.n):
        members[comp[c]].append(c)
        for x in letters:
            if comp[inv.mult[c][x]] != comp[c]:
                leaves[comp[c]] = True
    bottoms = [frozenset(members[w]) for w in range(ncomp) if not leaves[w]]
    assert bottoms, "no bottom SCC (the right-Cayley graph is finite)"
    for scc in bottoms:
        assert inv.identity not in scc, (
            f"the identity lies in a bottom SCC (n={inv.n}, "
            f"ap={' '.join(inv.alphabet.aps) or '-'})"
        )
    bottoms.sort(key=lambda scc: shortlex_key(inv.keys[least_key_class(inv, scc)]))
    return bottoms
