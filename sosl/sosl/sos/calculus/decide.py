"""Decision procedures: cell scans that always carry a witness.

Every question about an omega-language reduces, through the factoring theorem,
to a predicate on cells ``(c, d)`` — no word is ever enumerated. Scanning the
cells in the normative order of `table.cells_in_order` yields **the globally
minimal witness**:

> *Proposition W.* If some lasso ``(u, v)`` satisfies a `Val`-definable
> predicate, then the least satisfying cell's canonical lasso is at most
> ``(u, v)`` in the discipline order. Indeed ``(u, v)`` satisfies iff its cell
> ``(fold(u), fold(v))`` does, and ``key(fold(u))`` is shortlex-below ``u`` (as
> is the loop), so that cell's canonical lasso is componentwise below
> ``(u, v)``; the least satisfying cell is below it in turn.

So a witness returned here is minimal over *all* lassos, not merely over the
key-built ones. Single-table questions take ``(table, pairs)``; questions
relating two languages take an `Aligned` — their generated product, where the
two verdict maps read the two sides on one node pair.

Each procedure returns ``(answer, witness)``. The witness is ``None`` exactly
when the answer admits no lasso certificate (the language *is* empty, the
inclusion *does* hold); otherwise it carries the lasso and the bit that settles
the question.
"""
from __future__ import annotations

from typing import Optional, Tuple, Union

from ..invariant import Invariant
from ..io.serialize import dump_invariant
from ..lasso import Lasso
from .align import Aligned
from .surgery import complement
from .table import Cell, PairSet, Table
from .witness import Witness

Decision = Tuple[bool, Optional[Witness]]
"""An answer and, when a lasso settles it, that lasso."""

Scanned = Union[Table, Aligned]
"""What a cell scan runs over: one table, or the product of two languages."""


def _witness(source: Scanned, cell: Cell, expected: bool, operation: str) -> Witness:
    """The witness for ``cell`` of ``source``, carrying that cell's canonical
    lasso and the bit ``expected`` that the scan established for it."""
    lasso = source.cell_lasso(cell)
    return Witness(
        alphabet=source.alphabet,
        stem=lasso.stem,
        loop=lasso.loop,
        expected=expected,
        operation=operation,
        cell=cell,
    )


# --- one table -------------------------------------------------------------


def member(table: Table, pairs: PairSet, lasso: Lasso) -> bool:
    """Is ``lasso`` in ``L(pairs)``? Fold both components, then one `Val`
    lookup: ``O(|stem| + |loop|)``."""
    return table.val(pairs, table.fold(lasso.stem), table.fold(lasso.loop))


def is_empty(table: Table, pairs: PairSet) -> Decision:
    """Is ``L(pairs)`` empty? The witness, when it is not, is the shortest lasso
    in the language.

    The scan runs over *cells*, not over ``pairs``: the least pair of ``pairs``
    need not be the least cell, since a short non-idempotent loop key can fold
    into a linked pair whose own keys are long."""
    if not pairs:
        return True, None
    for cell in table.cells():
        if table.val(pairs, *cell):
            return False, _witness(table, cell, True, "is_empty")
    raise AssertionError("non-empty pair set with no satisfying cell")


def is_universal(table: Table, pairs: PairSet) -> Decision:
    """Does ``L(pairs)`` contain every omega-word? Emptiness of the complement.
    The witness, when it is not universal, is the shortest lasso outside the
    language — its recorded bit is ``False``, the bit ``pairs`` gives it."""
    empty, cex = is_empty(table, complement(table, pairs))
    if empty:
        return True, None
    assert cex is not None
    return False, _witness(table, cex.cell, False, "is_universal")


# --- two languages, through their generated product -------------------------


def included(aligned: Aligned) -> Decision:
    """Is the ``a`` side of ``aligned`` included in the ``b`` side? The witness,
    when it is not, is the shortest lasso of ``a`` outside ``b``.
    ``O(|nodes|^2)`` verdict evaluations."""
    for cell in aligned.cells():
        if aligned.verdict_a(*cell) and not aligned.verdict_b(*cell):
            return False, _witness(aligned, cell, True, "included")
    return True, None


def equivalent(aligned: Aligned) -> Decision:
    """Do the two sides of ``aligned`` denote the same language? One scan finds
    both inclusion defects at once; the witness is the least disagreeing cell,
    and its bit is the ``a`` side's verdict (so a replay against ``a`` confirms
    it and a replay against ``b`` refutes it)."""
    for cell in aligned.cells():
        va = aligned.verdict_a(*cell)
        if va != aligned.verdict_b(*cell):
            return False, _witness(aligned, cell, va, "equivalent")
    return True, None


def intersecting_word(aligned: Aligned) -> Decision:
    """Do the two sides share an omega-word — the model-checking-shaped query?
    The witness, when they do, is the shortest word in both. This is the one
    procedure here whose certificate attends the ``True`` answer."""
    for cell in aligned.cells():
        if aligned.verdict_a(*cell) and aligned.verdict_b(*cell):
            return True, _witness(aligned, cell, True, "intersecting_word")
    return False, None


# --- the O(1)-scan alternative on reduced invariants ------------------------


def byte_equivalent(left: Invariant, right: Invariant) -> bool:
    """Language equality by byte-equality of the `.sos` serializations. Sound
    **only** on invariants that are reduced and canonically keyed (the normal
    form of `reduce`), where the serialization is a normal form of the language;
    on any two such invariants it must agree with `equivalent` over their
    `align`ment, which the harness checks."""
    return dump_invariant(left) == dump_invariant(right)
