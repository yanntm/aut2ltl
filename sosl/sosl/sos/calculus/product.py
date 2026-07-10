"""product — the one move that pays for the product multiplication table.

`align` is decision-only: it exposes the reachable node set and the two component
verdicts, and never materializes the product's multiplication table (that is what
keeps `included` / `equivalent` / `intersecting_word` at ``O(|nodes|^2)`` verdict
lookups). But to turn a *combination* of two languages over different tables back
into a canonical `Invariant` — an intersection, a union, a difference — the
combined language must live over one omega-semigroup, which means the product
`M` must exist. This module builds it, once, over exactly the reachable nodes.

`materialize(aligned, a, b)` returns a `Product`: the product `Table` and each
side re-expressed as a pair set over it, so the free `surgery` catalog
(`intersection`, `union`, `difference`, `xor`, `complement`) then applies and
`reduce` canonicalizes the outcome. The reachable node set is the
letter-generated subsemigroup align already found — closed under the componentwise
product — so ``M((c_A,c_B), (d_A,d_B)) = (M_A(c_A,d_A), M_B(c_B,d_B))`` never
leaves it. Cost: ``O(|nodes|^2)`` product lookups plus one `of_raw` re-keying.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from .align import Aligned, align
from .table import Language, PairSet, Table


@dataclass(frozen=True)
class Product:
    """The product omega-semigroup of two aligned languages, with each side's
    language carried as a pair set over the one shared `Table`. Any `surgery`
    Boolean combinator of ``pairs_a`` and ``pairs_b`` denotes the corresponding
    combination of the two source languages; `reduce` then canonicalizes it."""

    table: Table
    pairs_a: PairSet
    pairs_b: PairSet


def materialize(aligned: Aligned, a: Language, b: Language) -> Product:
    """The `Product` of two languages given their already-built `aligned` product
    (align is priced separately — this is the materialization it defers). The
    node index space of ``aligned`` becomes the raw class space; `of_raw`
    restricts to the letter-reachable classes and re-keys them, reproducing the
    align order (same seed, same step), so the map is the identity in practice
    and is applied explicitly regardless."""
    ta, tb = a.table, b.table
    nodes = aligned.nodes
    index: Dict[Tuple[int, int], int] = {node: i for i, node in enumerate(nodes)}

    def prod_node(p: Tuple[int, int], q: Tuple[int, int]) -> int:
        node = (ta.mult[p[0]][q[0]], tb.mult[p[1]][q[1]])
        got = index.get(node)
        assert got is not None, "product left the letter-generated subsemigroup"
        return got

    mult = [[prod_node(p, q) for q in nodes] for p in nodes]
    letters = aligned.alphabet.letters()
    letter_class = [aligned.step_table[aligned.identity][x] for x in letters]

    table, remap = Table.of_raw(aligned.alphabet, aligned.identity, letter_class, mult)
    inv_remap: Dict[int, int] = {new: old for old, new in remap.items()}

    def side(verdict) -> PairSet:
        return frozenset(
            (s, e) for (s, e) in table.linked
            if verdict(inv_remap[s], inv_remap[e])
        )

    return Product(table=table, pairs_a=side(aligned.verdict_a),
                   pairs_b=side(aligned.verdict_b))


def product(a: Language, b: Language) -> Product:
    """The `Product` of two languages over (possibly) different tables: `align`
    them, then `materialize`. Convenience for callers that hold no `Aligned`;
    those that do — and want to price alignment apart from the product table —
    call `materialize` on their own `align` result."""
    return materialize(align(a, b), a, b)
