"""Fixtures F-J through F-L: hand-computed ground truth for the entropy
enclosure (spec section 10). Assertions are exact — no float enters any
check; the float `h` bracket is only asserted to contain the exact value.

    python3 -m tests.quant.fixtures3

Alphabet: one AP ``a``; the spec's letter *b* is mask 0 (rendered ``!a``),
the spec's letter *a* is mask 1 (rendered ``a``).

- F-J: ``Sigma^omega``, |Sigma| = 2 — one live self-loop class with both
  letters: ``rho_lo = rho_hi = 2`` exactly, ``h = 1`` in the bracket.
- F-K: ``a^omega`` — every live class has exactly one live successor:
  ``rho = 1`` exactly, ``h = 0`` in the bracket.
- F-L (golden mean, the irrational case certified rationally): "no
  factor bb" — two nontrivial live blocks, both ``[[1,1],[1,0]]``-shaped,
  ``rho = phi``: the sign test ``lo^2 <= lo + 1`` and ``hi^2 >= hi + 1``
  holds in fractions and the bracket is under ``1e-9`` wide, so the
  enclosure provably straddles ``phi`` with no float in the check.

Prints SUCCESS iff all pass.
"""
from __future__ import annotations

from fractions import Fraction

from sosl.quant import entropy
from tests.quant.fixtures2 import A_LETTER, B_LETTER, build


def check_fj() -> None:
    """F-J: the universal language over two letters, rho = 2 exactly."""
    sigma = build(
        ((), (B_LETTER,)),
        (1, 1),
        ((0, 1), (1, 1)),
        frozenset({(1, 1)}),
    )
    r = entropy(sigma)
    assert r.live == frozenset({0, 1}), r.live
    assert r.rho_lo == r.rho_hi == Fraction(2), (r.rho_lo, r.rho_hi)
    assert r.converged and all(b.iterations == 0 for b in r.blocks)
    assert r.h_lo <= 1 <= r.h_hi, (r.h_lo, r.h_hi)
    print("F-J ok: Sigma^omega has rho = 2 exactly, h = 1 in the bracket")


def check_fk() -> None:
    """F-K: L = a^omega over {a, b}; classes [eps], D = 'contains b'
    (absorbing off the live part), A = a+; rho = 1 exactly."""
    a_omega = build(
        ((), (B_LETTER,), (A_LETTER,)),
        (1, 2),
        ((0, 1, 2), (1, 1, 1), (2, 1, 2)),
        frozenset({(2, 2)}),
    )
    r = entropy(a_omega)
    assert r.live == frozenset({0, 2}), r.live
    assert r.rho_lo == r.rho_hi == Fraction(1), (r.rho_lo, r.rho_hi)
    assert r.converged
    assert r.h_lo <= 0 <= r.h_hi, (r.h_lo, r.h_hi)
    print("F-K ok: a^omega has one live successor per live class, "
          "rho = 1 exactly, h = 0 in the bracket")


def check_fl() -> None:
    """F-L: 'no factor bb'. Syntactic classes by (starts-with-b,
    ends-with-b) plus the zero Z = 'contains bb'; shortlex ids:
    [eps]=0, b=(1,1)=1, a=(0,0)=2, bb=Z=3, ba=(1,0)=4, ab=(0,1)=5.
    Every linked pair off Z is accepted (linkage forbids the bb
    junctions outright). rho = phi, certified by the sign test on
    rho^2 = rho + 1 in fractions."""
    no_bb = build(
        ((), (B_LETTER,), (A_LETTER,), (B_LETTER, B_LETTER),
         (B_LETTER, A_LETTER), (A_LETTER, B_LETTER)),
        (1, 2),
        ((0, 1, 2, 3, 4, 5),
         (1, 3, 4, 3, 3, 1),
         (2, 5, 2, 3, 2, 5),
         (3, 3, 3, 3, 3, 3),
         (4, 1, 4, 3, 4, 1),
         (5, 3, 2, 3, 3, 5)),
        frozenset({(2, 2), (4, 2), (2, 4), (4, 4), (1, 5), (5, 5)}),
    )
    r = entropy(no_bb)
    assert r.live == frozenset({0, 1, 2, 4, 5}), r.live
    nontrivial = [b for b in r.blocks if len(b.classes) == 2]
    assert sorted(b.classes for b in nontrivial) == [(1, 4), (2, 5)], r.blocks
    assert r.converged, r.blocks
    lo, hi = r.rho_lo, r.rho_hi
    assert hi - lo < Fraction(1, 10**9), (lo, hi)
    assert lo * lo <= lo + 1 and hi * hi >= hi + 1, (lo, hi)
    print(f"F-L ok: golden mean, two [[1,1],[1,0]] live blocks, "
          f"rho bracket straddles phi (width {float(hi - lo):.2e})")


def main() -> None:
    check_fj()
    check_fk()
    check_fl()
    print("SUCCESS")


if __name__ == "__main__":
    main()
