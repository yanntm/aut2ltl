"""The normal form: re-quotient a table by the syntactic congruence of one of
its languages.

Surgery keeps the table fixed, so the pair set it returns usually lives on an
algebra finer than the language needs — the complement of a language over a
50-class table is a language over that same 50-class table, whatever its own
syntactic algebra is. `reduce` collapses that: it computes the coarsest
congruence under which the language is still well defined, and returns the
canonical `Invariant` of ``L(pairs)``. Only after `reduce` is byte-equality of
`.sos` dumps a language test.

**The congruence.** ``c ~ c'`` iff they are interchangeable in both context
shapes an omega-word offers — as a stem against every loop, and as a loop
against every stem, under every left/right multiplication. Partition refinement
computes it:

1. *Base partition* by the signature ``sig(c) = (Val(c, d))_d ++ (Val(x, c))_x``
   — the class as a stem against every loop, then as a loop against every stem.
2. *Refine to a two-sided congruence*: split until, for every letter ``a``,
   ``c ~ c'`` implies ``M(c, lambda(a)) ~ M(c', lambda(a))`` and
   ``M(lambda(a), c) ~ M(lambda(a), c')``. Letters suffice — every class is a
   product of letters, so single-letter two-sided stability propagates to all
   contexts by induction; enumerating context triples is unnecessary.
3. *Quotient*: blocks become classes, ``M`` and ``lambda`` are induced, ``P``
   is the image of the pairs, and the shortlex BFS re-keys.

**The identity convention.** ``[eps]`` is held out of the refinement and
re-adjoined as a fresh singleton, never merged into a block — even one that acts
neutrally. This is the `.sos` canonicity requirement (`sos/algorithm.md`); drop
it and byte-equality stops meaning language equality.

Cost: ``O(n^2)`` `Val` calls for the signatures, then ``O(n^2 |Sigma|)``
refinement. The result is verified before it is returned (see `reduce`).
"""
from __future__ import annotations

from typing import Dict, Hashable, List, Sequence

from ..invariant import Invariant
from ..io.serialize import dump_invariant, load_invariant
from .table import PairSet, Table


def _dense(labels: Sequence[Hashable]) -> List[int]:
    """Dense block ids, numbered in order of first appearance."""
    seen: Dict[Hashable, int] = {}
    return [seen.setdefault(k, len(seen)) for k in labels]


def _blocks(table: Table, pairs: PairSet) -> Dict[int, int]:
    """The syntactic congruence of ``L(pairs)`` on the non-identity classes, as
    a ``class -> block id`` map. Steps 1 and 2 of the module docstring."""
    word_classes = table.loops()  # every class but the adjoined identity
    stems = range(table.n)

    signature = [
        (
            tuple(table.val(pairs, c, d) for d in word_classes),
            tuple(table.val(pairs, x, c) for x in stems),
        )
        for c in word_classes
    ]
    block = dict(zip(word_classes, _dense(signature)))

    letters = [table.letter_class[a] for a in table.alphabet.letters()]
    mult = table.mult
    while True:
        refined = [
            (
                block[c],
                tuple(block[mult[c][g]] for g in letters),
                tuple(block[mult[g][c]] for g in letters),
            )
            for c in word_classes
        ]
        new = dict(zip(word_classes, _dense(refined)))
        if len(set(new.values())) == len(set(block.values())):
            return block
        block = new


def syntactic_blocks(table: Table, pairs: PairSet) -> Dict[int, int]:
    """The syntactic congruence of ``L(pairs)`` on ``table``'s non-identity
    classes, as a ``class -> block id`` map (blocks numbered by first
    appearance). The public face of the partition refinement `reduce` runs; the
    two-sided-congruence coarsest partition under which ``L(pairs)`` is still
    well defined, hence paper Prop 4.1's `pi_L`. The identity is held out (it is
    re-adjoined as its own class by any quotient builder). ``O(n^2)`` signatures
    then ``O(n^2 |Sigma|)`` refinement."""
    return _blocks(table, pairs)


def reduce(table: Table, pairs: PairSet, check: bool = True) -> Invariant:
    """The canonical `Invariant` of ``L(pairs)``: the re-quotient of ``table`` by
    the syntactic congruence of that language, re-keyed by the shortlex BFS.

    With ``check`` (the default), three properties are asserted before the
    result leaves — each an ``O(n^2)`` or cheaper pass, each a hard error rather
    than a downgraded emission:

    - *pullback*: the result's membership read-off agrees with ``Val`` on every
      cell of the input, so no word changed sides;
    - *idempotence*: reducing the result reproduces it byte for byte;
    - *round trip*: the result survives `.sos` serialization and parsing.

    ``check=False`` is for the interior of those checks and for scans over large
    aligned products, where the quadratic pullback would dominate."""
    block = _blocks(table, pairs)
    reps: Dict[int, int] = {}
    for c, b in block.items():
        reps.setdefault(b, c)
    count = len(reps)

    # Class 0 is the fresh identity; block b becomes class b + 1.
    def cls(c: int) -> int:
        return 0 if c == table.identity else block[c] + 1

    mult: List[List[int]] = [[0] * (count + 1) for _ in range(count + 1)]
    for i in range(count + 1):
        mult[0][i] = i
        mult[i][0] = i
    for b, c in reps.items():
        for b2, c2 in reps.items():
            mult[b + 1][b2 + 1] = cls(table.mult[c][c2])

    letter_class = [cls(table.letter_class[a]) for a in table.alphabet.letters()]
    accept = frozenset((cls(s), cls(e)) for (s, e) in pairs)

    if check:
        for c in table.loops():
            for d in table.loops():
                assert cls(table.mult[c][d]) == mult[cls(c)][cls(d)], (c, d)

    quotient, remap = Table.of_raw(table.alphabet, 0, letter_class, mult)
    result = quotient.invariant(
        frozenset((remap[s], remap[e]) for (s, e) in accept)
    )
    if check:
        _verify(table, pairs, result)
    return result


def _verify(table: Table, pairs: PairSet, result: Invariant) -> None:
    """Assert the pullback, idempotence and round-trip laws of `reduce`."""
    for cell in table.cells():
        lasso = table.cell_lasso(cell)
        assert result.member(lasso) == table.val(pairs, *cell), (
            f"reduce changed the language at cell {cell} "
            f"({lasso.stem!r}.{lasso.loop!r}^omega)"
        )
    text = dump_invariant(result)
    again = reduce(Table.of(result), result.accept, check=False)
    assert dump_invariant(again) == text, "reduce is not idempotent"
    assert dump_invariant(load_invariant(text)) == text, ".sos round trip broke"


def reduced_invariant(inv: Invariant) -> Invariant:
    """`reduce` applied to an invariant's own table and accepting set — the
    normal form of the language ``inv`` presents, however coarse or fine the
    presentation was."""
    return reduce(Table.of(inv), inv.accept)
