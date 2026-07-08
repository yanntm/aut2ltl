"""Harness 5: the alignment laws, and scan-equivalence versus byte-equality.

    python3 -m tests.calculus.align_gate PATH.sos [OTHER.sos]

- ``align(I, I')`` on two separately loaded copies of one invariant generates
  exactly the diagonal, and `equivalent` accepts it.
- ``reduce`` is the identity (byte for byte) on an already-reduced invariant,
  which every corpus `.sos` is; and ``align(reduce(I), I)`` is equivalent.
- With a second file: `equivalent` over the aligned product must agree with
  `byte_equivalent` of the two reduced sides — the ``O(1)``-scan alternative —
  and a disagreement witness must replay against **both** invariants (positive
  on the ``a`` side, negative on the ``b`` side).

The realized alignment ratio ``|nodes| / (n_A * n_B)`` is printed: it is the V1
ledger's datum, and the reason the generated product is affordable.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List

from sosl.sos import Invariant, Lasso, dump_invariant, load_invariant
from sosl.sos.calculus import (
    Table,
    align,
    byte_equivalent,
    equivalent,
    included,
    reduce,
)


def language(inv: Invariant):
    """The invariant as a `FoldedLanguage` over its own table."""
    return Table.of(inv).language(inv.accept)


def check_self(inv: Invariant, name: str) -> Invariant:
    """The self-alignment and reduce-idempotence laws."""
    reduced = reduce(Table.of(inv), inv.accept)
    assert dump_invariant(reduced) == dump_invariant(inv), (
        f"{name}: reduce moved an already-reduced invariant"
    )
    print(f"  reduce(I) == I byte for byte ({inv.n} classes)")

    twin = load_invariant(dump_invariant(inv))  # a distinct Table object
    product = align(language(inv), language(twin))
    assert product.nodes == tuple((c, c) for c in range(inv.n)), "not the diagonal"
    eq, w = equivalent(product)
    assert eq, f"I is not equivalent to itself: {w.render() if w else ''}"
    inc, _ = included(product)
    assert inc, "I is not included in itself"
    print(f"  align(I, I') = diagonal, equivalent, ratio {product.ratio:.4f}")
    return reduced


def check_pair(left: Invariant, right: Invariant, lname: str, rname: str) -> None:
    """Scan-equivalence must agree with byte-equality on reduced sides, and the
    witness of a disagreement must replay against both."""
    red_l = reduce(Table.of(left), left.accept)
    red_r = reduce(Table.of(right), right.accept)
    by_bytes = byte_equivalent(red_l, red_r)

    product = align(language(left), language(right))
    eq, w = equivalent(product)
    print(f"  align({lname}, {rname}): {product.n} nodes of "
          f"{left.n}x{right.n}, ratio {product.ratio:.4f}")
    assert eq == by_bytes, (
        f"scan says equivalent={eq}, .sos byte-equality says {by_bytes}"
    )
    if eq:
        print("  equivalent (scan and bytes agree)")
        return

    assert w is not None
    w.replay(lambda u, v: left.member(Lasso(u, v)))  # the recorded bit is a's
    assert right.member(w.lasso) != w.expected, "the witness does not separate"
    print(f"  distinct; witness replays on both sides: {w.render()}")


def main(argv: List[str]) -> int:
    left_path = Path(argv[1])
    left = load_invariant(left_path.read_text())
    print(f"{left_path.name}: |C| = {left.n}")
    check_self(left, left_path.name)

    if len(argv) > 2:
        right_path = Path(argv[2])
        right = load_invariant(right_path.read_text())
        assert left.alphabet == right.alphabet, "different alphabets: substitute first"
        check_pair(left, right, left_path.name, right_path.name)
    print("SUCCESS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
