"""The syntactic algebra as a frozen value — `Alg`, the input of the synthesis.

Consumes the oracle's quotient data — the closed enriched monoid `EM¹(D)`, the
refined class list (`~ = ~lin ∩ ~ω`), the per-element acceptance profiles —
and produces the quotient `S(L)₊¹` in canonical form (`algorithm.md` layers
1 and 8): every class re-keyed by its shortlex-least representative word (the
letter order is the alphabet order the closure was built from), the letter
map, the class multiplication table, the idempotent flags, and the
accepting-pair table `P` defined exactly on the linked pairs
(`s·e = s`, `e·e = e`).

The re-keying is what makes `Alg` a language invariant: class ids no longer
depend on the closure's BFS over any particular automaton, only on the algebra
and the fixed letter order. Class 0 is always the identity (empty word).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from aut2ltl.bls.definability.oracle.closure import Monoid
from aut2ltl.bls.definability.oracle.profile import Profile

Word = Tuple[int, ...]
"""A finite word as 0-based letter indices into `Alg.letters`."""


@dataclass(frozen=True)
class Alg:
    """The quotient `S(L)₊¹`, canonically keyed, as pure tables.

    All fields are tuples, so the value is hashable — usable directly as a
    memoization key. `P[s][e]` is the acceptance of `u·z^ω` with `[u] = s`,
    `[z] = e` (from the initial state) when `(s, e)` is a linked pair, and
    `None` otherwise.
    """

    letters: Tuple[str, ...]                    # letter names, alphabet order
    letter_cls: Tuple[int, ...]                 # letter index -> class
    rep: Tuple[Word, ...]                       # class -> shortlex-least word
    mult: Tuple[Tuple[int, ...], ...]           # class × class -> class
    idem: Tuple[bool, ...]                      # class -> idempotent
    P: Tuple[Tuple[Optional[bool], ...], ...]   # linked pairs -> accepted

    def __len__(self) -> int:
        """The number of classes, identity included."""
        return len(self.rep)

    def key(self, i: int) -> str:
        """Class `i`'s canonical key: its representative word rendered as
        `letter;letter;...`, the empty word as `eps`."""
        return ";".join(self.letters[li] for li in self.rep[i]) or "eps"

    def word_cls(self, word: Iterable[int]) -> int:
        """The class of a finite word (letter indices), by table folding."""
        c: int = 0
        for li in word:
            c = self.mult[c][self.letter_cls[li]]
        return c

    def linked(self, s: int, e: int) -> bool:
        """Whether `(s, e)` is a linked pair: `s·e = s` and `e` idempotent."""
        return self.mult[s][e] == s and self.idem[e]

    def linked_pairs(self) -> List[Tuple[int, int]]:
        """All linked pairs, in lexicographic `(s, e)` order of the canonical
        class ids — the fixed enumeration order of the synthesis."""
        k: int = len(self.rep)
        return [(s, e) for s in range(k) for e in range(k) if self.linked(s, e)]

    def accepting_pairs(self) -> List[Tuple[int, int]]:
        """The linked pairs whose ω-words are in the language, same order."""
        return [(s, e) for (s, e) in self.linked_pairs() if self.P[s][e]]


def build(mon: Monoid, cls: Sequence[int], prof: Sequence[Profile],
          names: Sequence[str], init: int) -> Alg:
    """Freeze the oracle's quotient into an `Alg`.

    `cls[i]` is the congruence class of element `i` of `mon`; `prof[i]` its
    acceptance profile; `names` the letter names in the alphabet order the
    closure was generated from; `init` the initial state of the deterministic
    form the profiles were read on.

    Each class is keyed by the representative word of its first element in
    BFS order — the closure enumerates words shortest-first in letter order,
    so that word is the shortlex-least word of the whole class. Classes are
    then numbered in shortlex order of these keys, which puts the identity
    (empty word) at class 0. All tables are computed on class representatives;
    the congruence makes every entry representative-independent.
    """
    first_elem: Dict[int, int] = {}
    for ei in range(len(mon)):
        first_elem.setdefault(cls[ei], ei)
    k: int = len(first_elem)

    order: List[int] = sorted(
        first_elem,
        key=lambda c: (len(mon.rep[first_elem[c]]), mon.rep[first_elem[c]]))
    rep_elem: List[int] = [first_elem[c] for c in order]
    canon: Dict[int, int] = {c: i for i, c in enumerate(order)}

    rep: Tuple[Word, ...] = tuple(tuple(mon.rep[e]) for e in rep_elem)
    assert rep[0] == (), "the identity's class must key as the empty word"

    letter_cls: Tuple[int, ...] = tuple(
        canon[cls[mon.right[0][li]]] for li in range(len(names)))
    mult: Tuple[Tuple[int, ...], ...] = tuple(
        tuple(canon[cls[mon.mult(rep_elem[i], rep_elem[j])]] for j in range(k))
        for i in range(k))
    idem: Tuple[bool, ...] = tuple(mult[i][i] == i for i in range(k))

    # P(s, e) = Aprof(rep(e))[st_{rep(s)}(init)] at the linked pairs.
    st_at_init: List[int] = [mon.elems[e][init][0] for e in rep_elem]
    P: Tuple[Tuple[Optional[bool], ...], ...] = tuple(
        tuple(
            bool(prof[rep_elem[e]][st_at_init[s]])
            if (mult[s][e] == s and idem[e]) else None
            for e in range(k))
        for s in range(k))

    return Alg(letters=tuple(names), letter_cls=letter_cls, rep=rep,
               mult=mult, idem=idem, P=P)


__all__ = ["Word", "Alg", "build"]
