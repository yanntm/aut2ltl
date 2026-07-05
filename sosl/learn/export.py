"""Build the canonical invariant from a closed, consistent partition.

At a fixpoint the partition is a finite congruence; this turns it into the
`Invariant` normal form:

  - re-key every class by BFS over ``step`` from the start, letters in mask
    order — the first word reaching a class is its canonical shortlex key — and
    renumber classes in that discovery order (start becomes the identity);
  - the multiplication ``M[c][c'] = fold(c, key(c'))``;
  - the letter map ``lambda(a) = step(start, a)``;
  - the accepting linked pairs P: for every linked ``(s, e)`` (``e`` a non-empty
    idempotent, ``M[s][e] = s``) one membership query on ``key(s).key(e)^omega``.

The result is validated before return.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from sosl.learn.columns import Member
from sosl.learn.partition import Partition
from sosl.objects.alphabet import EMPTY, Word
from sosl.objects.invariant import Invariant
from sosl.objects.lasso import Lasso


def _canonical_order(p: Partition) -> Tuple[List[int], Dict[int, Word]]:
    """BFS from the start over ``step`` (letters in mask order): the discovery
    order of classes and each class's canonical key."""
    letters = p.table.alphabet.letters()
    key: Dict[int, Word] = {p.start: EMPTY}
    order: List[int] = [p.start]
    queue: List[int] = [p.start]
    while queue:
        c = queue.pop(0)
        for a in letters:
            d = p.step(c, a)
            if d not in key:
                key[d] = key[c] + (a,)
                order.append(d)
                queue.append(d)
    return order, key


def export(p: Partition, member: Member) -> Invariant:
    """The canonical `Invariant` for a closed, consistent partition ``p``."""
    ab = p.table.alphabet
    order, key = _canonical_order(p)
    new_id = {c: i for i, c in enumerate(order)}
    nn = len(order)

    keys: List[Word] = [EMPTY] * nn
    for c in order:
        keys[new_id[c]] = key[c]

    letter_class = [0] * ab.size
    for a in ab.letters():
        letter_class[a] = new_id[p.step(p.start, a)]

    mult = [[0] * nn for _ in range(nn)]
    for c in order:
        for d in order:
            mult[new_id[c]][new_id[d]] = new_id[p.fold_from(c, key[d])]

    identity = new_id[p.start]
    accept = set()
    for e in range(nn):
        if keys[e] == EMPTY or mult[e][e] != e:  # identity is never a loop
            continue
        for s in range(nn):
            if mult[s][e] == s and member(Lasso(keys[s], keys[e])):
                accept.add((s, e))

    inv = Invariant(
        alphabet=ab,
        keys=tuple(keys),
        letter_class=tuple(letter_class),
        mult=tuple(tuple(row) for row in mult),
        accept=frozenset(accept),
        identity=identity,
    )
    inv.validate()
    return inv
