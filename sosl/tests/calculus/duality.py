"""Harness 6: the duality gate — surgery's complement against the stored one.

    python3 -m tests.calculus.duality PATH.sos [COMPLEMENT.sos]

The corpus (`genaut/corpus/flat_canon/`) is closed under complement and stores
one file per language, so every case carries its own answer key: the complement
computed here — one set difference against the linked pairs, then `reduce` —
must be **byte-identical** to the committed `.sos` of the complement language.
That is the strongest single statement the calculus can make about itself: the
free operation lands exactly on the canonical form an independent construction
produced from an automaton.

Without a second argument the companion file is derived from the corpus naming
(``X.sos`` <-> ``X_c.sos``); if it is absent, only the involution law
``reduce(complement(complement(P))) == reduce(P)`` is checked, which needs no
answer key.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

from sosl.sos import dump_invariant, load_invariant
from sosl.sos.calculus import Table, complement, reduce


def companion(path: Path) -> Optional[Path]:
    """The corpus file holding the complement language: ``X_c.sos`` for
    ``X.sos``, and ``X.sos`` for ``X_c.sos``. ``None`` if it is not there."""
    stem = path.stem
    other = stem[:-2] if stem.endswith("_c") else stem + "_c"
    candidate = path.with_name(other + path.suffix)
    return candidate if candidate.exists() else None


def main(argv: List[str]) -> int:
    path = Path(argv[1])
    inv = load_invariant(path.read_text())
    table = Table.of(inv)

    comp = complement(table, inv.accept)
    assert comp == table.linked - inv.accept
    assert complement(table, comp) == inv.accept, "complement is not an involution"

    reduced = reduce(table, comp)
    back = reduce(Table.of(reduced), complement(Table.of(reduced), reduced.accept))
    assert dump_invariant(back) == dump_invariant(reduce(table, inv.accept)), (
        "reduce(complement(complement(P))) != reduce(P)"
    )
    print(f"{path.name}: |C| = {table.n} -> complement |C| = {reduced.n}; "
          f"involution holds")

    other = Path(argv[2]) if len(argv) > 2 else companion(path)
    if other is None:
        print("  no stored complement; involution only")
        print("SUCCESS")
        return 0

    stored = load_invariant(other.read_text())
    ours = dump_invariant(reduced)
    theirs = dump_invariant(stored)
    assert ours == theirs, (
        f"computed complement differs from {other.name}\n"
        f"--- computed\n{ours}--- stored\n{theirs}"
    )
    print(f"  reduce(complement(P)) byte-equals {other.name}")
    print("SUCCESS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
