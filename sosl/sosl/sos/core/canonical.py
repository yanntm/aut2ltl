"""Put a raw finite algebra into the canonical `Invariant` normal form.

A *raw algebra* is a finite monoid over the alphabet, given by any class
numbering:

  - ``identity`` — the class of the empty word;
  - ``letter_class[a]`` — the class of the single letter ``a`` (indexed by mask);
  - ``mult[c][d]`` — the class product (class of ``key(c).key(d)``);
  - ``accept`` — the accepting linked pairs, as ``(s, e)`` in the raw numbering.

`canonicalize` re-keys it by BFS over ``step(c, a) = mult[c][letter_class[a]]``
from the identity, letters in mask order (the first word reaching a class is its
canonical shortlex key — `shortlex_bfs`), renumbers classes in that discovery
order, remaps the tables and accepting set, and returns a validated `Invariant`.

This is the single normal form shared by every producer of an invariant — the
learner's export and the reference construction (`quotient`) — so that two
invariants over the same alphabet are byte-equal iff they denote the same
language. It is the format definition, not an algorithm of either producer.
"""
from __future__ import annotations

from typing import Callable, Dict, Iterable, List, Sequence, Tuple, TypeVar

from ..alphabet import EMPTY, Alphabet, Letter, Word
from ..invariant import Invariant

_Node = TypeVar("_Node")


def shortlex_bfs(
    start: _Node,
    letters: Sequence[Letter],
    step: Callable[[_Node, Letter], _Node],
) -> Tuple[List[_Node], List[Word]]:
    """Discover the nodes reachable from ``start`` under ``step``, breadth first
    with ``letters`` taken in order, and name each node by the first word that
    reaches it — its shortlex-least word. Returns the discovery order and the
    parallel key list (``keys[i]`` names ``order[i]``; ``keys[0] = eps``).

    Discovery order *is* shortlex order on the keys, so it doubles as a
    canonical numbering. The node type is any hashable: class ids when re-keying
    an algebra, class *pairs* when generating a product of two algebras."""
    keys: Dict[_Node, Word] = {start: EMPTY}
    order: List[_Node] = [start]
    i = 0
    while i < len(order):
        c = order[i]
        i += 1
        w = keys[c]
        for a in letters:
            d = step(c, a)
            if d not in keys:
                keys[d] = w + (a,)
                order.append(d)
    return order, [keys[c] for c in order]


def canonicalize(
    alphabet: Alphabet,
    identity: int,
    letter_class: Sequence[int],
    mult: Sequence[Sequence[int]],
    accept: Iterable[Tuple[int, int]],
) -> Invariant:
    """The canonical `Invariant` of the raw algebra (see module docstring)."""
    letters = alphabet.letters()

    order, key_list = shortlex_bfs(
        identity, letters, lambda c, a: mult[c][letter_class[a]]
    )
    assert len(order) == len(mult), "raw algebra has classes unreachable from eps"

    new_id = {c: i for i, c in enumerate(order)}
    nn = len(order)

    keys: List[Word] = [EMPTY] * nn
    for c, k in zip(order, key_list):
        keys[new_id[c]] = k

    lc = [0] * alphabet.size
    for a in letters:
        lc[a] = new_id[letter_class[a]]

    m = [[0] * nn for _ in range(nn)]
    for c in order:
        for d in order:
            m[new_id[c]][new_id[d]] = new_id[mult[c][d]]

    acc = frozenset((new_id[s], new_id[e]) for (s, e) in accept)

    inv = Invariant(
        alphabet=alphabet,
        keys=tuple(keys),
        letter_class=tuple(lc),
        mult=tuple(tuple(row) for row in m),
        accept=acc,
        identity=new_id[identity],
    )
    inv.validate()
    return inv
