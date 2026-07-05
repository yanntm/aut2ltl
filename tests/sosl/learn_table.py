"""Checks for the observation table + partition (sosl.learn.table/partition).

Self-contained (uses the white-box teacher). Run from the repo root:

    python3 -m tests.sosl.learn_table

Seeds a table for GF a, fills it, and checks that the derived partition already
has the three expected classes (eps / no-a / has-a), is closed and consistent,
and folds coherently. Prints OK lines, or raises on the first failure.
"""
from __future__ import annotations

from sosl.learn.partition import Partition
from sosl.learn.table import Table
from sosl.objects.alphabet import EMPTY
from sosl.teacher import HoaTeacher


def check_gfa_partition() -> None:
    t = HoaTeacher.of_ltl("GF a")
    table = Table(t.alphabet, t.member)
    table.fill()
    p = Partition(table)

    # eps + {no-a} + {has-a} = 3 classes; the seed omega column already splits.
    assert p.n == 3, p.n
    assert p.is_closed(), p.unclosed()
    assert p.inconsistency() is None, p.inconsistency()

    A, NOA = (1,), (0,)
    # eps is its own class (the start); the two letters land in different classes.
    assert p.class_of[EMPTY] == p.start
    assert p.class_of[A] != p.class_of[NOA]
    assert p.class_of[A] != p.start and p.class_of[NOA] != p.start

    # fold coherence on the domain: psi(w) == class(w).
    for w in table.domain():
        if w == EMPTY:
            continue
        assert p.fold(w) == p.class_of[w], (w, p.fold(w), p.class_of[w])
    print(f"OK GF a table: {p.n} classes, closed, consistent, folds coherent")


def check_query_counting() -> None:
    t = HoaTeacher.of_ltl("GF a")
    table = Table(t.alphabet, t.member)
    assert table.n_member == 0
    table.fill()
    assert table.n_member > 0
    before = table.n_member
    table.fill()  # idempotent: no new queries
    assert table.n_member == before, (before, table.n_member)
    print(f"OK fill counts {before} queries and is idempotent")


def main() -> int:
    check_gfa_partition()
    check_query_counting()
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
