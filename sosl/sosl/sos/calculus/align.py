"""The generated product of two folded languages — the only product-priced move.

To compare two languages presented over *different* algebras, one needs a common
place to name words. `align` builds it: a BFS over pair nodes
``(c_A, c_B)``, seeded with ``(id_A, id_B)`` and extended by ``step`` on both
sides at once. The reachable node set is exactly

    { (fold_A(w), fold_B(w)) : w in Sigma* }

— the letter-generated subsemigroup of the product, plus the identity. Its size
is bounded by ``n_A * n_B`` and in practice far below it (`Aligned.ratio` is the
measured datum).

**No product multiplication table is ever materialized.** An `Aligned` exposes
the node set with its shortlex keys, the componentwise ``step``, and the two
verdict maps — each side evaluated on *its own* component under *its own*
discipline. That is sound for an invariant side because the idempotent of a
cyclic subsemigroup is unique, so projecting a product's idempotent power onto a
component gives that component's idempotent; the hypothesis side has no such
notion and is only ever asked through its `verdict`.

Cost: ``O(n_A * n_B * |Sigma|)`` step calls and ``O(n_A * n_B)`` memory. When
both sides are pair sets over one and the same table, the product is the
diagonal and no BFS is run.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterator, Tuple

from ..alphabet import Alphabet, Letter, Word
from ..core.canonical import shortlex_bfs
from ..lasso import Lasso
from .table import Cell, FoldedLanguage, Language, cells_in_order

Verdict = Callable[[int, int], bool]
"""A verdict map over *aligned node ids*: ``(stem node, loop node) -> bool``."""


@dataclass(frozen=True)
class Aligned:
    """The generated product of two folded languages. Nodes are numbered in
    shortlex-BFS discovery order (node ``identity`` is the seed, keyed ``eps``);
    ``verdict_a`` / ``verdict_b`` answer for the two sides on the same node
    pair, so a cell scan reads both languages at once."""

    alphabet: Alphabet
    nodes: Tuple[Tuple[int, int], ...]
    keys: Tuple[Word, ...]
    identity: int
    step_table: Tuple[Tuple[int, ...], ...]
    verdict_a: Verdict
    verdict_b: Verdict
    size_a: int
    size_b: int

    @property
    def n(self) -> int:
        """The number of reachable nodes."""
        return len(self.nodes)

    @property
    def ratio(self) -> float:
        """``|nodes| / (n_A * n_B)`` — how much of the full product the letters
        actually generate. The V1 ledger measures this."""
        return self.n / (self.size_a * self.size_b)

    def step(self, node: int, a: Letter) -> int:
        """The node reached from ``node`` on letter ``a`` (componentwise)."""
        return self.step_table[node][a]

    def cells(self) -> Iterator[Cell]:
        """Every cell of the product, in the normative scan order."""
        return cells_in_order(self.keys, self.identity)

    def cell_lasso(self, cell: Cell) -> Lasso:
        """The canonical lasso of a cell: ``key(c).key(d)^omega``."""
        c, d = cell
        return Lasso(self.keys[c], self.keys[d])


def align(a: FoldedLanguage, b: FoldedLanguage) -> Aligned:
    """The generated product of ``a`` and ``b``. Both sides must be over the
    same alphabet — assert, do not adapt: `surgery.inverse_substitution` is the
    adapter that moves a language to another alphabet."""
    assert a.alphabet == b.alphabet, "align: alphabets differ (substitute first)"
    letters = a.alphabet.letters()

    if isinstance(a, Language) and isinstance(b, Language) and a.table is b.table:
        return _diagonal(a, b)

    def step(node: Tuple[int, int], x: Letter) -> Tuple[int, int]:
        return (a.step(node[0], x), b.step(node[1], x))

    order, keys = shortlex_bfs((a.identity, b.identity), letters, step)
    index = {node: i for i, node in enumerate(order)}
    step_table = tuple(tuple(index[step(node, x)] for x in letters) for node in order)
    return Aligned(
        alphabet=a.alphabet,
        nodes=tuple(order),
        keys=tuple(keys),
        identity=0,
        step_table=step_table,
        verdict_a=lambda c, d: a.verdict(order[c][0], order[d][0]),
        verdict_b=lambda c, d: b.verdict(order[c][1], order[d][1]),
        size_a=len(a.classes),
        size_b=len(b.classes),
    )


def _diagonal(a: Language, b: Language) -> Aligned:
    """The product of two languages over one table: the diagonal, already
    generated and already keyed — no BFS, no renumbering."""
    table = a.table
    letters = table.alphabet.letters()
    return Aligned(
        alphabet=table.alphabet,
        nodes=tuple((c, c) for c in range(table.n)),
        keys=table.keys,
        identity=table.identity,
        step_table=tuple(
            tuple(table.step(c, x) for x in letters) for c in range(table.n)
        ),
        verdict_a=lambda c, d: table.val(a.pairs, c, d),
        verdict_b=lambda c, d: table.val(b.pairs, c, d),
        size_a=table.n,
        size_b=table.n,
    )
