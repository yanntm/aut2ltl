"""Smoke: exercise every calculus entry point on one `.sos` file.

    python3 -m tests.calculus.smoke PATH.sos

Prints the table shape, the residual count, the Boolean laws' outcome, the
witnesses of emptiness / universality on the language and its complement, the
self-alignment ratio, and the reduced form's class count. Single input,
self-bound; a failure raises.
"""
from __future__ import annotations

import sys
from pathlib import Path

from sosl.sos import load_invariant
from sosl.sos.calculus import (
    Table,
    align,
    complement,
    equivalent,
    included,
    intersecting_word,
    is_empty,
    is_saturated,
    is_universal,
    reduce,
    residual_count,
    rooting,
)


def main(path: str) -> int:
    inv = load_invariant(Path(path).read_text())
    table = Table.of(inv)
    pairs = inv.accept
    comp = complement(table, pairs)

    print(f"{Path(path).name}: |C| = {table.n}, |linked| = {len(table.linked)}, "
          f"|P| = {len(pairs)}")
    print(f"  saturated: P {is_saturated(table, pairs)}, "
          f"Pc {is_saturated(table, comp)}")
    print(f"  residuals: {residual_count(table, pairs)}")
    print(f"  rooting[eps] == P: {rooting(table, pairs, table.identity) == pairs}")

    for name, p in (("P", pairs), ("Pc", comp)):
        empty, w = is_empty(table, p)
        univ, wu = is_universal(table, p)
        print(f"  {name}: empty={empty} {w.render() if w else ''}")
        print(f"  {name}: universal={univ} {wu.render() if wu else ''}")

    diag = align(table.language(pairs), table.language(comp))
    eq, w = equivalent(diag)
    inter, wi = intersecting_word(diag)
    inc, _ = included(diag)
    print(f"  P vs Pc: equivalent={eq} ({w.render() if w else ''})")
    print(f"  P vs Pc: intersect={inter}, included={inc}")

    red = reduce(table, pairs)
    red_c = reduce(table, comp)
    print(f"  reduce: |C| {table.n} -> {red.n} (complement -> {red_c.n})")

    cross = align(Table.of(red).language(red.accept), table.language(pairs))
    eq2, w2 = equivalent(cross)
    print(f"  reduced vs original: equivalent={eq2}, ratio={cross.ratio:.3f}")
    assert eq2, w2.render() if w2 else "?"
    print("SUCCESS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
