"""Alphabet minimization of an invariant: drop the atomic propositions the
language does not depend on.

`spot`'s `remove_unused_ap` sheds only propositions no edge mentions. A language
can still be independent of a proposition whose literal survives in some edge
guard — a **free** AP. The invariant records this exactly, with no automaton:
`aps[i]` is free iff flipping its bit never changes `letter_class` — every minterm
`m` and its `i`-toggle `m ^ (1 << (k-1-i))` fold to the same semigroup element
(`aps[i]` sits on bit `k-1-i`, the `alphabet.py` convention). This module reads
that off and returns the invariant re-expressed over only the propositions that
matter.

Why an invariant needs it. The `.sos` canonical form must be alphabet-minimal for
language identity to be byte-exact up to renaming. A free AP inflates the
alphabet, so a language over `{a, b, c}` that ignores `a` gets a different key
than its `{b, c}` presentation, and — because `Invariant.complement` flips `P` on
the *same* algebra — its complement keeps the free AP, while a complement taken
through the automaton (`spot.dualize` then re-read) drops it. The two then
disagree. Removing free APs first makes the fold idempotent and makes
minimization **commute with complement**, so the "complement = flip `P`" byte
relation the classifier and `flatten --canon` rely on holds at the minimal
alphabet.
"""
from __future__ import annotations

from collections import deque
from typing import FrozenSet, List, Tuple

from .alphabet import EMPTY, Alphabet, Letter, Word, shortlex_key
from .invariant import Invariant


def free_aps(inv: Invariant) -> Tuple[int, ...]:
    """The indices `i` (into `inv.alphabet.aps`) of the propositions the language
    is independent of: toggling `aps[i]`'s bit leaves every letter's class
    unchanged. Empty when the alphabet is already minimal."""
    k = len(inv.alphabet.aps)
    lc = inv.letter_class
    size = inv.alphabet.size
    free: List[int] = []
    for i in range(k):
        bit = 1 << (k - 1 - i)
        if all(lc[m] == lc[m ^ bit] for m in range(size)):
            free.append(i)
    return tuple(free)


def remove_free_aps(inv: Invariant) -> Invariant:
    """`inv` re-expressed over only the propositions the language depends on.

    The semigroup (`classes`, `mult`, `accept`) is unchanged — a free AP never
    distinguishes two elements, so the set of letter images is identical — but the
    alphabet shrinks, `letter_class` re-maps onto the smaller letter set, and the
    shortlex `keys` (hence the class numbering) are recomputed over it. The result
    is the byte-canonical invariant of the same language at its minimal alphabet.
    Idempotent; returns `inv` itself when no AP is free."""
    free = set(free_aps(inv))
    if not free:
        return inv
    k = len(inv.alphabet.aps)
    kept = [i for i in range(k) if i not in free]
    new_alpha = Alphabet(tuple(inv.alphabet.aps[i] for i in kept))
    kp = len(kept)

    # Project each old mask onto the kept bits; a free bit never changes the class,
    # so `new_lc[proj(om)] = inv.letter_class[om]` is well-defined (every old mask
    # projecting to the same reduced mask carries the same class).
    new_lc = [0] * (1 << kp)
    for om in range(inv.alphabet.size):
        pm = 0
        for j, i in enumerate(kept):
            chi = (om >> (k - 1 - i)) & 1
            pm |= chi << (kp - 1 - j)
        new_lc[pm] = inv.letter_class[om]

    return _recanonicalize(new_alpha, new_lc, inv.mult, inv.accept, inv.identity)


def _recanonicalize(
    alphabet: Alphabet, letter_class: List[int],
    mult: Tuple[Tuple[int, ...], ...], accept: FrozenSet[Tuple[int, int]],
    identity: int,
) -> Invariant:
    """Rebuild a byte-canonical invariant from a semigroup (`mult`, `accept`,
    `identity`) and a letter action (`letter_class`) over `alphabet`: recompute
    each class's shortlex-least word by BFS from the identity over the letters,
    then renumber classes by shortlex of those keys (identity, key `ε`, becomes 0).
    The letters still generate the whole semigroup, so every class is reached."""
    n = len(mult)
    size = len(letter_class)
    key: List[Word] = [None] * n            # type: ignore[list-item]
    key[identity] = EMPTY
    dq = deque([identity])
    while dq:
        c = dq.popleft()
        for m in range(size):
            c2 = mult[c][letter_class[m]]
            if key[c2] is None:
                key[c2] = key[c] + (Letter(m),)
                dq.append(c2)

    order = sorted(range(n), key=lambda c: shortlex_key(key[c]))
    newid = [0] * n
    for nid, oldc in enumerate(order):
        newid[oldc] = nid

    return Invariant(
        alphabet=alphabet,
        keys=tuple(key[order[i]] for i in range(n)),
        letter_class=tuple(newid[letter_class[m]] for m in range(size)),
        mult=tuple(tuple(newid[mult[order[i]][order[j]]] for j in range(n))
                   for i in range(n)),
        accept=frozenset((newid[s], newid[e]) for (s, e) in accept),
        identity=newid[identity],
    )
