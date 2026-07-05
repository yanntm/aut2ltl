"""Checks for observation-table column semantics (sosl.learn.columns).

Self-contained. Run from the repo root:

    python3 -m tests.sosl.learn_columns

Verifies each column shape builds the intended lasso and that its bit, taken
through an Invariant-backed member, matches the language on GF a. Prints OK
lines, or raises on the first failure.
"""
from __future__ import annotations

from sosl.learn.columns import LinCol, OmCol, is_omega, query
from sosl.objects import EMPTY, Alphabet, Invariant, Lasso


def gfa_member():
    ab = Alphabet.of(["a"])
    inv = Invariant(
        alphabet=ab,
        keys=(EMPTY, (0,), (1,)),
        letter_class=(1, 2),
        mult=((0, 1, 2), (1, 1, 2), (2, 2, 2)),
        accept=frozenset({(2, 2)}),
        identity=0,
    )
    return inv.member


A, NOA = (1,), (0,)


def check_lasso_shapes() -> None:
    lin = LinCol(x=NOA, y=A, t=A)
    assert lin.lasso(NOA) == Lasso(NOA + NOA + A, A)      # x+p+y, loop t
    om = OmCol(x=A, y=NOA)
    assert om.lasso(A) == Lasso(A, A + NOA)                # x, loop p+y
    assert is_omega(om) and not is_omega(lin)
    print("OK column lasso shapes")


def check_bits_against_gfa() -> None:
    member = gfa_member()
    # Omega column (eps, eps): bit of p is whether p^omega has infinitely many a.
    om = OmCol(x=EMPTY, y=EMPTY)
    assert query(om, member, A) is True       # (a)^omega -> inf many a
    assert query(om, member, NOA) is False    # ({})^omega -> none
    # Linear column (eps, eps, {a}): x.p.y.t^omega with t={a} -> always inf a.
    lin = LinCol(x=EMPTY, y=EMPTY, t=A)
    assert query(lin, member, NOA) is True     # tail loop {a} carries the a's
    assert query(lin, member, A) is True
    # Linear column with a no-a loop: never in GF a.
    lin0 = LinCol(x=EMPTY, y=EMPTY, t=NOA)
    assert query(lin0, member, A) is False
    print("OK column bits against GF a")


def main() -> int:
    check_lasso_shapes()
    check_bits_against_gfa()
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
