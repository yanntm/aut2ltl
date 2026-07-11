"""M1 fixtures: three hand-computed invariants, exact expected values.

    python3 -m tests.quant.fixtures

Alphabet: one AP ``a``, so Sigma = {!a, a}. The spec's letter *a* is mask
1 (rendered ``a``), the spec's letter *b* is mask 0 (rendered ``!a``);
mask order puts ``!a`` before ``a``, so where the spec lists profile
entries as (a, b) they appear here in shortlex order (!a, a).

- F-A: "infinitely many a's"  — theta [("a", 1)], mu = 1 for every p.
- F-B: "finitely many a's"    — theta [("a", 0)], mu = 0; byte-equal to
  the complement surgery applied to F-A, with equal MeasureResults.
- F-C: a·Sigma^omega          — two singleton bottom SCCs, kernel = all
  of S (both idempotents give the same profile: paper Lemma 3.3),
  theta [("!a", 0), ("a", 1)], mu = p(a); absorption (p(b), p(a)).

Exact equality throughout (fractions, not floats); any mismatch is a
finding against code or paper (spec §4). Prints SUCCESS iff all pass.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Dict

from sosl.sos import Alphabet, Invariant, Letter, dump_invariant
from sosl.sos.calculus import Table
from sosl.quant import (
    MeasureResult,
    bottom_sccs,
    kernel,
    kernel_idempotent,
    measure,
    theta_profile,
)

AB = Alphabet.of(["a"])
B_LETTER = Letter(0)  # rendered "!a" — the spec's letter b
A_LETTER = Letter(1)  # rendered "a"  — the spec's letter a

# Class ids in canonical shortlex-BFS order: 0 = [eps], 1 = key "!a", 2 = key "a".
KEYS = ((), (B_LETTER,), (A_LETTER,))
LETTER_CLASS = (1, 2)

# Shared semiautomaton of F-A / F-B: A absorbs (any product touching A is A),
# B idempotent. Class 1 = B ("nonempty all-b words"), class 2 = A ("has an a").
MULT_AB = ((0, 1, 2), (1, 1, 2), (2, 2, 2))

# F-C semiautomaton: the first letter decides — both classes left-absorb.
MULT_C = ((0, 1, 2), (1, 1, 1), (2, 2, 2))

P13: Dict[Letter, Fraction] = {A_LETTER: Fraction(1, 3), B_LETTER: Fraction(2, 3)}


def build(mult: tuple, accept: frozenset) -> Invariant:
    """A validated fixture invariant over the shared alphabet and keys."""
    inv = Invariant(
        alphabet=AB,
        keys=KEYS,
        letter_class=LETTER_CLASS,
        mult=mult,
        accept=accept,
        identity=0,
    )
    inv.validate()
    return inv


def check_fa() -> Invariant:
    """F-A: infinitely many a's; P = {(A, A)}."""
    fa = build(MULT_AB, frozenset({(2, 2)}))
    assert bottom_sccs(fa) == [frozenset({2})]
    assert kernel(fa) == frozenset({2})
    assert kernel_idempotent(fa) == 2
    assert theta_profile(fa).entries == (("a", True),)
    for p in (None, P13):
        r = measure(fa, p)
        assert r.value == Fraction(1), r.value
        assert r.absorption == (("a", Fraction(1)),), r.absorption
    print("F-A ok: theta [(a, 1)], mu = 1 (uniform and p(a)=1/3)")
    return fa


def check_fb(fa: Invariant) -> None:
    """F-B: finitely many a's; P = {(A, B), (B, B)}; also the complement
    surgery route from F-A, byte-equal and result-equal."""
    fb = build(MULT_AB, frozenset({(2, 1), (1, 1)}))
    assert theta_profile(fb).entries == (("a", False),)
    for p in (None, P13):
        r = measure(fb, p)
        assert r.value == Fraction(0), r.value
    flipped = fa.complement()
    assert dump_invariant(flipped) == dump_invariant(fb), "flip route differs"
    assert measure(flipped) == measure(fb)
    assert measure(flipped, P13) == measure(fb, P13)
    print("F-B ok: theta [(a, 0)], mu = 0; complement route byte-equal")


def check_fc() -> None:
    """F-C: first letter a; P = {(A, A), (A, B)}. Kernel = all of S, and
    the profile must not depend on which of its idempotents is used."""
    fc = build(MULT_C, frozenset({(2, 2), (2, 1)}))
    assert bottom_sccs(fc) == [frozenset({1}), frozenset({2})]
    assert kernel(fc) == frozenset({1, 2}), "kernel must be all of S"
    profile = theta_profile(fc)
    assert profile.entries == (("!a", False), ("a", True)), profile.entries
    table = Table.of(fc)
    for k in (1, 2):  # both classes are idempotent kernel elements
        assert fc.mult[k][k] == k
        bits = tuple(table.val(fc.accept, c, k) for c in (1, 2))
        assert bits == (False, True), (k, bits)
    r_uni: MeasureResult = measure(fc)
    assert r_uni.value == Fraction(1, 2), r_uni.value
    assert r_uni.absorption == (("!a", Fraction(1, 2)), ("a", Fraction(1, 2)))
    r_13 = measure(fc, P13)
    assert r_13.value == Fraction(1, 3), r_13.value
    assert r_13.absorption == (("!a", Fraction(2, 3)), ("a", Fraction(1, 3)))
    print("F-C ok: theta [(!a, 0), (a, 1)], both idempotents agree, "
          "mu = 1/2 | 1/3, absorption = (p(b), p(a))")


def main() -> None:
    fa = check_fa()
    check_fb(fa)
    check_fc()
    print("SUCCESS")


if __name__ == "__main__":
    main()
