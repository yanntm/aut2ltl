"""The free fragment of the calculus: operations that keep the table fixed and
only move the pair set.

Everything here is `O(|linked|)` (a set operation or one scan) unless stated,
because `Val` factors through the pair set pointwise:

    Val_P(c, d) = (M(c, idem(d)), idem(d)) in P

so any Boolean combination of pair sets is the same Boolean combination of the
languages. This is the "pay canonicity once" half of the calculus: once an
invariant exists, complement and the Boolean operations cost nothing.

Two operations move outside that pattern. `rooting` shifts the stem by a class,
realizing the left quotient ``key(c)^{-1}.L``; `inverse_substitution` rewrites
the letter map, realizing relabeling / letter merging / alphabet extension, and
is the only one that returns a new table.

**The internal law.** Two linked pairs denote the same set of omega-words iff
they are conjugate, so a pair set that is a *language* is closed under
conjugation — `saturate`d. Every operation here maps saturated sets to saturated
sets; the harness asserts it on every output, and a violation convicts the
operation (never `saturate` an output silently to hide it).
"""
from __future__ import annotations

from typing import Callable, Iterable, List, Sequence, Set, Tuple

from ..alphabet import Alphabet, Letter
from .table import PairSet, Table

# --- the Boolean fragment --------------------------------------------------


def empty(table: Table) -> PairSet:
    """The empty language over ``table``."""
    return frozenset()


def universal(table: Table) -> PairSet:
    """The language of all omega-words: every linked pair."""
    return table.linked


def complement(table: Table, pairs: PairSet) -> PairSet:
    """``linked \\ pairs``. Correct because ``Val`` reads membership of the same
    looked-up pair, so flipping the set flips the verdict pointwise."""
    return table.linked - pairs


def union(table: Table, left: PairSet, right: PairSet) -> PairSet:
    """``left | right``; ``Val`` distributes over union pointwise."""
    return left | right


def intersection(table: Table, left: PairSet, right: PairSet) -> PairSet:
    """``left & right``; ``Val`` distributes over intersection pointwise."""
    return left & right


def difference(table: Table, left: PairSet, right: PairSet) -> PairSet:
    """``left - right``, i.e. ``left & complement(right)``."""
    return left - right


def xor(table: Table, left: PairSet, right: PairSet) -> PairSet:
    """``left ^ right`` — the symmetric difference, the disagreement language."""
    return left ^ right


# --- rooting (the left quotient) -------------------------------------------


def rooting(table: Table, pairs: PairSet, c: int) -> PairSet:
    """``P_c = {(s, e) in linked : (M(c, s), e) in pairs}``, the pair set of the
    left quotient ``key(c)^{-1}.L(pairs)``.

    Well defined: ``(M(c, s), e)`` is linked whenever ``(s, e)`` is. Correct:
    ``Val_{P_c}(x, d) = Val_P(M(c, x), d)``, which is membership of
    ``key(c).key(x).key(d)^omega``. The action law ``P_{M(c,d)} = (P_c)_d``
    holds, with ``P_identity = pairs``."""
    mult = table.mult
    return frozenset((s, e) for (s, e) in table.linked if (mult[c][s], e) in pairs)


def residual_count(table: Table, pairs: PairSet) -> int:
    """The number of distinct left quotients ``{P_c : c in C}`` — the size of
    the residual (right-congruence) automaton of ``L(pairs)``, read off the
    algebra with no automaton."""
    return len({rooting(table, pairs, c) for c in range(table.n)})


# --- saturation and the legality check --------------------------------------


def linked_pair_of(table: Table, stem: int, loop: int) -> Tuple[int, int]:
    """The linked pair that decides the cell ``(stem, loop)``: absorb one
    idempotent loop into the stem. This is the pair `Table.val` looks up, so a
    cell and its linked pair always carry the same verdict."""
    e = table.idem(loop)
    return (table.mult[stem][e], e)


def saturate(table: Table, pairs: PairSet) -> PairSet:
    """The conjugation closure of ``pairs``: the least superset closed under

        (s, e) in Q,  M(x, y) = e  ==>  linked_pair_of(M(s, x), M(y, x)) in Q

    The rule is the word identity ``u.(xy)^omega = (ux).(yx)^omega``: the cell
    ``(sx, yx)`` denotes the same omega-words as ``(s, e)``, so the two must get
    the same verdict, and a pair set denotes a language iff it equals its
    closure. Conjugacy is symmetric (swap ``x`` and ``y`` to travel back), so
    the closure is a union of conjugacy classes.

    Note ``M(y, x)`` need **not** be idempotent even though ``M(x, y) = e`` is,
    which is why the conjugate cell is normalized through `linked_pair_of`
    rather than inserted as it stands. ``O(|linked| * n^2)`` worst case; run
    rarely (legality checks, harness)."""
    mult = table.mult
    factor = table.factorizations
    out: Set[Tuple[int, int]] = set(pairs)
    work: List[Tuple[int, int]] = list(out)
    while work:
        s, e = work.pop()
        for x, y in factor[e]:
            conjugate = linked_pair_of(table, mult[s][x], mult[y][x])
            if conjugate not in out:
                out.add(conjugate)
                work.append(conjugate)
    return frozenset(out)


def is_saturated(table: Table, pairs: PairSet) -> bool:
    """Is ``pairs`` closed under conjugation — i.e. does it denote a language?"""
    return saturate(table, pairs) == pairs


def pair_language(table: Table, pairs: Iterable[Tuple[int, int]]) -> PairSet:
    """An arbitrary set of linked pairs promoted to a language, after checking
    that it is legal: every pair linked, and the set saturated. Raises
    `AssertionError` otherwise — the entry point for hand-written pair sets."""
    frozen = frozenset(pairs)
    illegal = frozen - table.linked
    assert not illegal, f"not linked pairs: {sorted(illegal)}"
    assert is_saturated(table, frozen), "pair set is not conjugation-closed"
    return frozen


# --- inverse substitution (the alphabet move) -------------------------------


def inverse_substitution(
    table: Table,
    pairs: PairSet,
    alphabet: Alphabet,
    pi: Callable[[Letter], Letter],
) -> Tuple[Table, PairSet]:
    """Reinterpret ``L(pairs)`` over a new alphabet through ``pi : Sigma' ->
    Sigma``: same classes and same product, letter map ``lambda . pi``. The
    result recognizes ``pi^{-1}(L)`` — a word over ``Sigma'`` is accepted iff its
    letterwise image is.

    Covers relabeling, letter merging (``pi`` non-injective) and alphabet
    extension by duplication (``pi`` non-surjective). The reachable part may
    shrink, so the returned table is restricted to it and the pair set filtered
    to the surviving classes (a dropped class is named by no word and denotes
    nothing). The result is *not* reduced — the letter map may have collapsed
    distinctions — so `reduce` it before any byte-level use."""
    letter_class: Sequence[int] = [table.letter_class[pi(a)] for a in alphabet.letters()]
    new_table, remap = Table.of_raw(alphabet, table.identity, letter_class, table.mult)
    moved = frozenset(
        (remap[s], remap[e]) for (s, e) in pairs if s in remap and e in remap
    )
    return new_table, moved
