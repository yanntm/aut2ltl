"""Put a raw finite algebra into the canonical `Invariant` normal form.

A *raw algebra* is a finite monoid over the alphabet, given by any class
numbering:

  - ``identity`` — the class of the empty word;
  - ``letter_class[a]`` — the class of the single letter ``a`` (indexed by mask);
  - ``mult[c][d]`` — the class product (class of ``key(c).key(d)``);
  - ``accept`` — the accepting linked pairs, as ``(s, e)`` in the raw numbering.

`canonicalize` re-keys it by BFS over ``step(c, a) = mult[c][letter_class[a]]``
from the identity, letters in mask order (the first word reaching a class is its
canonical shortlex key), renumbers classes in that discovery order, remaps the
tables and accepting set, and returns a validated `Invariant`.

This is the single normal form shared by every producer of an invariant — the
learner's export and the reference construction (`quotient`) — so that two
invariants over the same alphabet are byte-equal iff they denote the same
language. It is the format definition, not an algorithm of either producer.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple

from ..alphabet import EMPTY, Alphabet, Word
from ..invariant import Invariant


def canonicalize(
    alphabet: Alphabet,
    identity: int,
    letter_class: Sequence[int],
    mult: Sequence[Sequence[int]],
    accept: Iterable[Tuple[int, int]],
) -> Invariant:
    """The canonical `Invariant` of the raw algebra (see module docstring)."""
    letters = alphabet.letters()

    key: Dict[int, Word] = {identity: EMPTY}
    order: List[int] = [identity]
    queue: List[int] = [identity]
    while queue:
        c = queue.pop(0)
        for a in letters:
            d = mult[c][letter_class[a]]
            if d not in key:
                key[d] = key[c] + (a,)
                order.append(d)
                queue.append(d)
    assert len(order) == len(mult), "raw algebra has classes unreachable from eps"

    new_id = {c: i for i, c in enumerate(order)}
    nn = len(order)

    keys: List[Word] = [EMPTY] * nn
    for c in order:
        keys[new_id[c]] = key[c]

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
