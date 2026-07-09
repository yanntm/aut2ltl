"""One multiplication table `(C, lambda, M)`, its derived notions, and `Val`.

A `Table` is an `Invariant` with its accepting set held apart: the classes,
their shortlex keys, the letter map and the class product. Accepting sets ("pair
sets") are *values* over a table — plain immutable sets of linked pairs — so one
table hosts many languages and nothing here is ever mutated. The algebra itself
is not reimplemented: a `Table` carries an accept-free `Invariant` and memoizes
its `fold`, `idempotent_power` and `linked_pairs`.

The one notion this module adds is the membership oracle

    Val_P(c, d) = (M(c, idem(d)), idem(d)) in P

which decides ``key(c).key(d)^omega in L(P)`` and, by the factoring theorem, the
membership of *every* lasso whose stem folds to ``c`` and whose loop folds to
``d``. Every decision procedure over a table is therefore a scan of `val` over
the **cells** ``(c, d)`` with ``d`` non-identity — never over words. The scan
order (`cells`) is the counterexample discipline ``(len stem, len loop, stem,
loop)`` applied to the cells' canonical lassos; scanning in it makes the first
satisfying cell's lasso minimal over all lassos, since ``key`` is shortlex-least
in its class.

Classes are numbered in shortlex-BFS discovery order from the identity, so a
class's id, its key and its scan position agree, and every class is reachable by
letters — `of_raw` enforces this by restricting a raw algebra to its reachable
part.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict, FrozenSet, Iterator, List, Optional, Protocol, Sequence, Tuple

from ..alphabet import EMPTY, Alphabet, Letter, Word
from ..core.canonical import shortlex_bfs
from ..invariant import Invariant
from ..lasso import Lasso

PairSet = FrozenSet[Tuple[int, int]]
"""A language over a table: an immutable set of its linked pairs."""

Cell = Tuple[int, int]
"""A stem class and a (non-identity) loop class; denotes ``key(c).key(d)^omega``."""


class FoldedLanguage(Protocol):
    """What a decision procedure needs from one side of a comparison: a class
    set with an identity, a letter action, and a verdict on (stem, loop) class
    pairs under *that side's own* discipline.

    An `Invariant` implements it through `Language` (verdict = `Table.val`); a
    mid-learning Cayley hypothesis implements it with its step table and its
    P-cache read-off, and must only ever be asked through `verdict` — no linked
    pair law holds of it. The alphabet is part of the interface: the aligned
    product needs it and cannot recover it from the class set."""

    alphabet: Alphabet
    classes: Sequence[int]
    identity: int

    def step(self, c: int, a: Letter) -> int: ...

    def verdict(self, stem: int, loop: int) -> bool: ...


def cells_in_order(keys: Sequence[Word], identity: int) -> Iterator[Cell]:
    """Every cell ``(c, d)`` with ``d != identity``, in the counterexample
    discipline of its canonical lasso: shortest stem, then shortest loop, then
    stem lex, then loop lex. Lazy — a scan that stops at the first hit pays only
    for the prefix it consumed."""
    assert keys[identity] == EMPTY, "the identity's key must be the empty word"
    by_len: Dict[int, List[int]] = {}
    for c, w in enumerate(keys):
        by_len.setdefault(len(w), []).append(c)
    for group in by_len.values():
        group.sort(key=lambda c: keys[c])
    lengths = sorted(by_len)
    loop_lengths = [n for n in lengths if n >= 1]  # a length-0 key is the identity
    for stem_len in lengths:
        for loop_len in loop_lengths:
            for c in by_len[stem_len]:
                for d in by_len[loop_len]:
                    yield (c, d)


class Table:
    """One ``(C, lambda, M)`` with the identity adjoined; see the module
    docstring. Immutable — the memo fields are pure caches over ``algebra``, an
    `Invariant` whose accepting set is empty and never consulted."""

    __slots__ = ("algebra", "_idem", "_linked", "_factorizations")

    def __init__(self, algebra: Invariant) -> None:
        self.algebra = replace(algebra, accept=frozenset())
        self._idem: List[Optional[int]] = [None] * algebra.n
        self._linked: Optional[PairSet] = None
        self._factorizations: Optional[Tuple[Tuple[Tuple[int, int], ...], ...]] = None

    # --- construction ------------------------------------------------------

    @classmethod
    def of(cls, inv: Invariant) -> "Table":
        """The table of an invariant; its ``accept`` field is then an ordinary
        pair set over that table. Asserts the invariant's class numbering is the
        canonical shortlex-BFS one, which the scan order relies on."""
        table = cls(inv)
        order, keys = shortlex_bfs(inv.identity, inv.alphabet.letters(), table.step)
        assert order == list(range(inv.n)), "invariant is not canonically numbered"
        assert keys == list(inv.keys), "invariant keys are not the shortlex ones"
        return table

    @classmethod
    def of_raw(
        cls,
        alphabet: Alphabet,
        identity: int,
        letter_class: Sequence[int],
        mult: Sequence[Sequence[int]],
    ) -> Tuple["Table", Dict[int, int]]:
        """A table from a raw algebra in any class numbering: restrict to the
        classes reachable from ``identity`` by letters, renumber them in
        shortlex-BFS discovery order, key them by their first word. Returns the
        table and the ``old -> new`` map, defined on the reachable classes only
        — an unreachable class is named by no word and denotes nothing, so it is
        dropped rather than kept unkeyed (`canonicalize`, which rejects such an
        algebra outright, is the strict variant for producers of invariants)."""
        letters = alphabet.letters()
        order, keys = shortlex_bfs(
            identity, letters, lambda c, a: mult[c][letter_class[a]]
        )
        remap = {c: i for i, c in enumerate(order)}
        algebra = Invariant(
            alphabet=alphabet,
            keys=tuple(keys),
            letter_class=tuple(remap[letter_class[a]] for a in letters),
            mult=tuple(tuple(remap[mult[c][d]] for d in order) for c in order),
            accept=frozenset(),
            identity=remap[identity],
        )
        algebra.validate()
        return cls(algebra), remap

    def invariant(self, pairs: PairSet) -> Invariant:
        """The (validated) `Invariant` this table carries for the language
        ``pairs``. Canonically numbered by construction; byte-canonical only if
        the table is also reduced (see `sosl.sos.calculus.reduce`)."""
        inv = replace(self.algebra, accept=pairs)
        inv.validate()
        return inv

    # --- the algebra (delegated) -------------------------------------------

    @property
    def alphabet(self) -> Alphabet:
        return self.algebra.alphabet

    @property
    def keys(self) -> Tuple[Word, ...]:
        return self.algebra.keys

    @property
    def letter_class(self) -> Tuple[int, ...]:
        return self.algebra.letter_class

    @property
    def mult(self) -> Tuple[Tuple[int, ...], ...]:
        return self.algebra.mult

    @property
    def identity(self) -> int:
        return self.algebra.identity

    @property
    def n(self) -> int:
        """The number of classes (the adjoined identity included)."""
        return self.algebra.n

    def loops(self) -> List[int]:
        """The classes usable as a loop: every class but the identity (an empty
        loop is not a lasso)."""
        return [c for c in range(self.n) if c != self.identity]

    def step(self, c: int, a: Letter) -> int:
        """``M(c, lambda(a))`` — the class of ``key(c).a``."""
        return self.mult[c][self.letter_class[a]]

    def fold(self, word: Word) -> int:
        """The class of ``word``; the empty word folds to the identity."""
        return self.algebra.fold(word)

    def idem(self, d: int) -> int:
        """The unique idempotent of ``{d, d^2, d^3, ...}`` (memoized). Its
        uniqueness is what lets `val` be evaluated on a component of a product
        rather than on the product's own idempotent power."""
        assert d != self.identity, "the identity is not a loop class"
        cached = self._idem[d]
        if cached is None:
            cached = self.algebra.idempotent_power(d)
            self._idem[d] = cached
        return cached

    @property
    def linked(self) -> PairSet:
        """The linked pairs ``(s, e)``: ``e`` a non-identity idempotent and
        ``M(s, e) = s``. The universal language of this table."""
        if self._linked is None:
            self._linked = self.algebra.linked_pairs()
        return self._linked

    @property
    def factorizations(self) -> Tuple[Tuple[Tuple[int, int], ...], ...]:
        """For each class ``e``, the pairs ``(x, y)`` with ``M(x, y) = e``. One
        ``O(n^2)`` pass over the table, cached: `surgery.saturate` walks it once
        per pair it processes and must not rebuild it."""
        if self._factorizations is None:
            buckets: List[List[Tuple[int, int]]] = [[] for _ in range(self.n)]
            for x in range(self.n):
                row = self.mult[x]
                for y in range(self.n):
                    buckets[row[y]].append((x, y))
            self._factorizations = tuple(tuple(b) for b in buckets)
        return self._factorizations

    def val(self, pairs: PairSet, c: int, d: int) -> bool:
        """The membership oracle: is ``u.v^omega`` in ``L(pairs)`` for any (all)
        ``u`` folding to ``c`` and ``v`` folding to ``d``? Absorb one idempotent
        loop into the stem, then look the linked pair up. ``(M(c, e), e)`` is
        linked for any ``c``, so this is total on ``d != identity``."""
        e = self.idem(d)
        return (self.mult[c][e], e) in pairs

    # --- the scan ----------------------------------------------------------

    def cells(self) -> Iterator[Cell]:
        """Every cell in the normative scan order (see `cells_in_order`)."""
        return cells_in_order(self.keys, self.identity)

    def cell_lasso(self, cell: Cell) -> Lasso:
        """The canonical lasso of a cell: ``key(c).key(d)^omega``."""
        c, d = cell
        return Lasso(self.keys[c], self.keys[d])

    def language(self, pairs: PairSet) -> "Language":
        """This table's ``pairs`` seen as a `FoldedLanguage`."""
        return Language(self, pairs)


@dataclass(frozen=True)
class Language:
    """A `FoldedLanguage` view of one pair set over one table — the adapter that
    lets an invariant enter `align` beside a foreign object (a learner's Cayley
    hypothesis) without either side importing the other."""

    table: Table
    pairs: PairSet

    @property
    def alphabet(self) -> Alphabet:
        return self.table.alphabet

    @property
    def classes(self) -> Sequence[int]:
        return range(self.table.n)

    @property
    def identity(self) -> int:
        return self.table.identity

    def step(self, c: int, a: Letter) -> int:
        return self.table.step(c, a)

    def verdict(self, stem: int, loop: int) -> bool:
        return self.table.val(self.pairs, stem, loop)
