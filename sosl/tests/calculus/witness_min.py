"""Harness 8: witness minimality — the scan's answer against brute force.

    python3 -m tests.calculus.witness_min PATH.sos [OTHER.sos] [BOUND]

Proposition W says a cell scan in the discipline order returns the *globally*
minimal witness, not merely the least among lassos built from class keys. This
gate checks that claim the only way it can be checked: enumerate every lasso
with ``|stem|, |loop| <= BOUND`` in the very same order, take the first that
satisfies the predicate, and demand it equal the witness the scan produced.

Four predicates on one file: non-emptiness of ``P``, non-universality of ``P``,
a disagreement between ``P`` and its complement (`equivalent`), and a shared
word between ``P`` and itself (`intersecting_word`). Those all have short
witnesses; a second file adds the cross-language `equivalent` / `included` /
`intersecting_word` scans over the aligned product, where the minimal separator
is where the claim actually bites.

When the scan's witness is longer than ``BOUND`` the enumeration must come up
empty — the two statements are then still consistent, and the check says so.
"""
from __future__ import annotations

import sys
from itertools import product
from pathlib import Path
from typing import Callable, Iterator, List, Optional

from sosl.sos import Alphabet, Lasso, load_invariant
from sosl.sos.calculus import (
    PairSet,
    Table,
    align,
    complement,
    equivalent,
    included,
    intersecting_word,
    is_empty,
    is_universal,
    member,
)
from sosl.sos.calculus.witness import Witness

DEFAULT_BOUND = 3
"""Stem and loop length for the brute-force enumeration."""


def in_discipline_order(alphabet: Alphabet, bound: int) -> Iterator[Lasso]:
    """Every lasso up to ``bound``, ordered as the teacher orders
    counterexamples: shortest stem, then shortest loop, then stem lex, then loop
    lex. This is exactly the order `cells_in_order` induces on cells."""
    letters = alphabet.letters()
    for stem_len in range(bound + 1):
        for loop_len in range(1, bound + 1):
            for u in product(letters, repeat=stem_len):
                for v in product(letters, repeat=loop_len):
                    yield Lasso(u, v)


def brute_first(
    alphabet: Alphabet, bound: int, holds: Callable[[Lasso], bool]
) -> Optional[Lasso]:
    """The first lasso up to ``bound`` satisfying ``holds``, in discipline order."""
    return next((w for w in in_discipline_order(alphabet, bound) if holds(w)), None)


def compare(name: str, witness: Optional[Witness], brute: Optional[Lasso], bound: int) -> None:
    """The scan's witness and brute force must name the same lasso — or, when
    the witness lies beyond ``bound``, brute force must have found nothing."""
    if witness is None:
        assert brute is None, f"{name}: no witness, but brute force found {brute}"
        print(f"  {name}: no witness, none within bound {bound}")
        return
    if max(len(witness.stem), len(witness.loop)) > bound:
        assert brute is None, (
            f"{name}: witness beyond bound but brute force found {brute}"
        )
        print(f"  {name}: witness beyond bound {bound}, enumeration empty (consistent)")
        return
    assert brute is not None, f"{name}: witness {witness.render()} unseen by brute force"
    assert (witness.stem, witness.loop) == (brute.stem, brute.loop), (
        f"{name}: scan says {witness.render()}, brute force says {brute}"
    )
    print(f"  {name}: minimal — {witness.render()}")


def check_pair(
    left: Table, lp: PairSet, right: Table, rp: PairSet, bound: int
) -> None:
    """The cross-language scans, against brute force over the shared alphabet."""
    alphabet = left.alphabet
    product_ = align(left.language(lp), right.language(rp))

    _, w = equivalent(product_)
    compare("equivalent(A,B)", w, brute_first(
        alphabet, bound,
        lambda x: member(left, lp, x) != member(right, rp, x)), bound)

    _, w = included(product_)
    compare("included(A,B)", w, brute_first(
        alphabet, bound,
        lambda x: member(left, lp, x) and not member(right, rp, x)), bound)

    _, w = intersecting_word(product_)
    compare("intersecting(A,B)", w, brute_first(
        alphabet, bound,
        lambda x: member(left, lp, x) and member(right, rp, x)), bound)


def main(argv: List[str]) -> int:
    path = Path(argv[1])
    other = Path(argv[2]) if len(argv) > 2 and argv[2].endswith(".sos") else None
    tail = argv[3:] if other else argv[2:]
    bound = int(tail[0]) if tail else DEFAULT_BOUND
    inv = load_invariant(path.read_text())
    table = Table.of(inv)
    pairs = inv.accept
    comp = complement(table, pairs)
    print(f"{path.name}: |C| = {table.n}, brute-force bound {bound}")

    _, w = is_empty(table, pairs)
    compare("is_empty", w, brute_first(table.alphabet, bound,
                                       lambda x: member(table, pairs, x)), bound)

    _, w = is_universal(table, pairs)
    compare("is_universal", w, brute_first(table.alphabet, bound,
                                           lambda x: not member(table, pairs, x)), bound)

    _, w = equivalent(align(table.language(pairs), table.language(comp)))
    compare("equivalent", w, brute_first(
        table.alphabet, bound,
        lambda x: member(table, pairs, x) != member(table, comp, x)), bound)

    _, w = intersecting_word(align(table.language(pairs), table.language(pairs)))
    compare("intersecting_word", w, brute_first(table.alphabet, bound,
                                                lambda x: member(table, pairs, x)), bound)

    if other is not None:
        rhs = load_invariant(other.read_text())
        assert rhs.alphabet == inv.alphabet, "different alphabets: substitute first"
        print(f"  vs {other.name} (|C| = {rhs.n})")
        check_pair(table, pairs, Table.of(rhs), rhs.accept, bound)

    print("SUCCESS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
