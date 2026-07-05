"""Checks for the invariant membership read-off (sosl.objects.invariant).

Self-contained. Run from the repo root:

    python3 -m tests.sosl.invariant_readoff

Builds two hand-verified algebras: the syntactic omega-semigroup of "infinitely
many a" (GF a) over AP={a}, and a synthetic 2-element group to exercise the
higher-power idempotent path. Prints OK lines, or raises on the first failure.
"""
from __future__ import annotations

from sosl.objects import EMPTY, Alphabet, Invariant, Lasso


def gfa_invariant() -> Invariant:
    # AP = {a}; letters: mask 0 = {} (no a), mask 1 = {a}.
    # Semigroup classes: 0 = identity (eps), 1 = "no a" (nonempty), 2 = "has a".
    ab = Alphabet.of(["a"])
    return Invariant(
        alphabet=ab,
        keys=(EMPTY, (0,), (1,)),        # id -> eps, class1 -> {}, class2 -> {a}
        letter_class=(1, 2),             # {} folds to class1, {a} to class2
        mult=(
            (0, 1, 2),                   # identity row
            (1, 1, 2),                   # noa . {id,noa,hasa}
            (2, 2, 2),                   # hasa absorbs
        ),
        accept=frozenset({(2, 2)}),      # loop with an a -> infinitely many a
        identity=0,
    )


def check_gfa() -> None:
    inv = gfa_invariant()
    inv.validate()
    a, noa = (1,), (0,)  # single-letter words
    # loop carries an a  -> accept, regardless of stem
    assert inv.member(Lasso(EMPTY, a)) is True
    assert inv.member(Lasso(noa, a)) is True
    # loop has no a -> reject (only finitely many a)
    assert inv.member(Lasso(EMPTY, noa)) is False
    assert inv.member(Lasso(a, noa)) is False
    # longer loop with an a somewhere still accepts
    assert inv.member(Lasso(EMPTY, (0, 1, 0))) is True
    print("OK GF(a) read-off")


def check_idempotent_higher_power() -> None:
    # Synthetic 2-element group {id=0, x=1}: x^2 = id, id idempotent, x is not.
    ab = Alphabet.of([])  # no APs needed; table exercised directly
    inv = Invariant(
        alphabet=ab,
        keys=(EMPTY, EMPTY),  # placeholder keys; only mult is exercised here
        letter_class=(),
        mult=((0, 1), (1, 0)),
        accept=frozenset(),
        identity=0,
    )
    # x is not idempotent (x^2=id); its idempotent power is id, reached at i=2.
    assert inv.idempotent_power(1) == 0, inv.idempotent_power(1)
    assert inv.idempotent_power(0) == 0
    print("OK idempotent power on a non-idempotent element")


def check_validate_rejects_bad_pair() -> None:
    inv = gfa_invariant()
    broken = Invariant(
        inv.alphabet, inv.keys, inv.letter_class, inv.mult,
        accept=frozenset({(1, 2)}),  # (s=1,e=2): mult[1][2]=2 != 1, not linked
        identity=inv.identity,
    )
    try:
        broken.validate()
        raise AssertionError("validate should reject a non-linked accept pair")
    except AssertionError as exc:
        if "should reject" in str(exc):
            raise
    print("OK validate rejects a non-linked accepting pair")


def main() -> int:
    check_gfa()
    check_idempotent_higher_power()
    check_validate_rejects_bad_pair()
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
