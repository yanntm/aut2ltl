"""Checks for the Cayley-form prediction (sosl.objects.cayley).

Self-contained. Run from the repo root:

    python3 -m tests.sosl.cayley_predict

Builds the GF(a) hypothesis (the step table of the "infinitely many a"
omega-semigroup) and checks that its normative prediction agrees with the
language, that loop stabilization picks the right pair, and that an uncached
pair predicts None. Prints OK lines, or raises on the first failure.
"""
from __future__ import annotations

from sosl.objects import EMPTY, Alphabet, Hypothesis, Lasso


def gfa_hypothesis() -> Hypothesis:
    # classes 0 = start/eps, 1 = "no a", 2 = "has a"; letters {} = 0, {a} = 1.
    ab = Alphabet.of(["a"])
    return Hypothesis(
        alphabet=ab,
        keys=(EMPTY, (0,), (1,)),
        step=(
            (1, 2),   # from eps: {} -> noa, {a} -> hasa
            (1, 2),   # from noa
            (2, 2),   # from hasa (absorbing)
        ),
        accept={(2, 2): True, (1, 1): False, (2, 1): False},
        start=0,
    )


def check_prediction_matches_language() -> None:
    h = gfa_hypothesis()
    a, noa = (1,), (0,)
    assert h.predict(Lasso(EMPTY, a)) is True
    assert h.predict(Lasso(noa, a)) is True
    assert h.predict(Lasso(EMPTY, noa)) is False
    assert h.predict(Lasso(a, noa)) is False
    # a longer loop that contains an a still stabilizes to the accepting pair
    assert h.predict(Lasso(EMPTY, (0, 1, 0))) is True
    print("OK prediction matches GF(a)")


def check_stabilized_pair() -> None:
    h = gfa_hypothesis()
    # loop {a}: folds to class 2, stabilizes at k=1, stem eps -> s=2, e=2.
    assert h.stabilized_pair(Lasso(EMPTY, (1,))) == (2, 2)
    # loop {}: folds to class 1, stem {a} -> s stays 2 under a no-a loop... s=2.
    assert h.stabilized_pair(Lasso((1,), (0,))) == (2, 1)
    print("OK stabilized pair")


def check_uncached_is_none() -> None:
    h = gfa_hypothesis()
    del h.accept[(2, 1)]  # drop a cached bit
    # stem {a}, loop {} reduces to (2,1), now uncached -> None
    assert h.predict(Lasso((1,), (0,))) is None
    print("OK uncached pair predicts None")


def main() -> int:
    check_prediction_matches_language()
    check_stabilized_pair()
    check_uncached_is_none()
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
