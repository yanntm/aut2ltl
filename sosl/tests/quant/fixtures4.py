"""M5 fixtures F-M / F-N / F-O: hand-computed chains, exact probabilities.

    python3 -m tests.quant.fixtures4

Alphabet: one AP ``a``, so Sigma = {!a, a}. The spec's letter *a* is mask 1
(rendered ``a``), the spec's letter *b* is mask 0 (rendered ``!a``).

- F-M pins the word convention (spec §11.2): a chain that emits ``a`` from
  its initial state deterministically and then flips 1/3 : 2/3 forever.
  ``Pr(a.Sigma^omega) = 1`` — reading the word as ``l(q1) l(q2) ...``
  (dropping the initial state's letter) would give 1/3, so a red here
  convicts the convention. ``Pr(b.Sigma^omega) = 0``.
- F-N (deterministic, periodic): ``q_a -> q_b -> q_a``, both probability 1.
  ``Pr((ab)^omega) = 1``, ``Pr((ba)^omega) = 0``. One product bottom SCC
  spanning both chain states — the second-base-state paranoid check bites.
- F-O (real absorption split): ``q0`` (``a``) branches 1/3 to ``q1`` (``a``,
  absorbing) and 2/3 to ``q2`` (``b``, absorbing). ``Pr(finitely many b)
  = 1/3``, ``Pr(infinitely many b) = 2/3``. Two bottom SCCs, the linear
  system carries the answer.

Every chain is round-tripped through its ``.mc`` text. Exact equality
throughout (fractions, not floats); a mismatch is a finding against code or
paper (spec §11.4). Prints SUCCESS iff all pass.
"""
from __future__ import annotations

from fractions import Fraction
from typing import FrozenSet, Tuple

from sosl.sos import Alphabet, Invariant, Letter
from sosl.quant.mc import Chain, dump_mc, parse_mc
from sosl.quant.product import pr_chain

AB = Alphabet.of(["a"])
B = Letter(0)  # rendered "!a" — the spec's letter b
A = Letter(1)  # rendered "a"  — the spec's letter a

ONE = Fraction(1)
THIRD = Fraction(1, 3)
TWO_THIRDS = Fraction(2, 3)

# Class ids in canonical shortlex-BFS order: 0 = [eps], 1 = key "!a", 2 = key "a".
KEYS2 = ((), (B,), (A,))
LETTER_CLASS2 = (1, 2)

# "the first letter decides": both non-identity classes left-absorb.
MULT_FIRST = ((0, 1, 2), (1, 1, 1), (2, 2, 2))

# "does the word contain a b": class 1 (b) absorbs, class 2 = nonempty all-a.
MULT_HASB = ((0, 1, 2), (1, 1, 1), (2, 1, 2))

# F-N's monoid: the alternating words. 0 = [eps], 1 = b, 2 = a, 3 = zero,
# 4 = ba, 5 = ab (shortlex-BFS: eps, !a, a, !a!a = zero, !a a = ba, a !a = ab).
KEYS6 = ((), (B,), (A,), (B, B), (B, A), (A, B))
MULT_ALT = (
    (0, 1, 2, 3, 4, 5),
    (1, 3, 4, 3, 3, 1),
    (2, 5, 3, 3, 2, 3),
    (3, 3, 3, 3, 3, 3),
    (4, 1, 3, 3, 4, 3),
    (5, 3, 2, 3, 3, 5),
)


def build(
    keys: Tuple[Tuple[Letter, ...], ...],
    mult: Tuple[Tuple[int, ...], ...],
    accept: FrozenSet[Tuple[int, int]],
) -> Invariant:
    """A validated, associative fixture invariant over the one-AP alphabet."""
    inv = Invariant(
        alphabet=AB,
        keys=keys,
        letter_class=LETTER_CLASS2,
        mult=mult,
        accept=accept,
        identity=0,
    )
    inv.validate()
    assert inv.associativity_witness() is None, inv.associativity_witness()
    return inv


def chain(
    label: Tuple[Letter, ...],
    trans: Tuple[Tuple[Tuple[int, Fraction], ...], ...],
    init: int,
) -> Chain:
    """A validated chain, round-tripped through its ``.mc`` text (the reader
    is exercised on every fixture, not only in the gate)."""
    ch = Chain(alphabet=AB, label=label, trans=trans, init=init)
    ch.validate()
    back = parse_mc(dump_mc(ch), AB)
    assert back == ch, "the .mc round-trip changed the chain"
    return ch


def check_fm() -> None:
    """F-M: the discriminating fixture — the initial state's letter is the
    word's first letter."""
    first_a = build(KEYS2, MULT_FIRST, frozenset({(2, 2), (2, 1)}))
    first_b = build(KEYS2, MULT_FIRST, frozenset({(1, 1), (1, 2)}))
    # state 0 = q_a (label a), state 1 = q_b (label b); both flip 1/3 : 2/3.
    row = ((0, THIRD), (1, TWO_THIRDS))
    ch = chain(label=(A, B), trans=(row, row), init=0)

    ra = pr_chain(first_a, ch)
    assert ra.value == ONE, f"Pr(a.Sigma^omega) = {ra.value}, expected 1 " \
        "(1/3 would mean the initial state's letter was dropped)"
    rb = pr_chain(first_b, ch)
    assert rb.value == Fraction(0), rb.value
    assert ra.value + rb.value == 1, "the two are complementary languages"
    print(f"F-M ok: Pr(a.Sigma^w) = 1, Pr(b.Sigma^w) = 0 "
          f"(product {ra.n_product} states, theta {ra.bits})")


def check_fn() -> None:
    """F-N: the deterministic 2-cycle; only (ab)^omega is generated."""
    ab_omega = build(KEYS6, MULT_ALT, frozenset({(5, 5), (2, 4)}))
    ba_omega = build(KEYS6, MULT_ALT, frozenset({(4, 4), (1, 5)}))
    # state 0 = q_a (label a) -> state 1 = q_b (label b) -> state 0.
    ch = chain(label=(A, B), trans=(((1, ONE),), ((0, ONE),)), init=0)

    r1 = pr_chain(ab_omega, ch)
    assert r1.value == ONE, r1.value
    r2 = pr_chain(ba_omega, ch)
    assert r2.value == Fraction(0), r2.value
    assert len(r1.bits) == 1, r1.bits
    print(f"F-N ok: Pr((ab)^w) = 1, Pr((ba)^w) = 0 "
          f"(one bottom SCC over both chain states, base {r1.bases[0]})")


def check_fo() -> None:
    """F-O: the absorption split — two bottom SCCs, the linear system."""
    inf_b = build(KEYS2, MULT_HASB, frozenset({(1, 1)}))
    fin_b = build(KEYS2, MULT_HASB, frozenset({(1, 2), (2, 2)}))
    assert fin_b.accept == inf_b.complement().accept, "F-O's two languages "\
        "are complements on the shared table"
    # state 0 = q0 (a), state 1 = q1 (a, absorbing), state 2 = q2 (b, absorbing).
    ch = chain(
        label=(A, A, B),
        trans=(((1, THIRD), (2, TWO_THIRDS)), ((1, ONE),), ((2, ONE),)),
        init=0,
    )

    r_fin = pr_chain(fin_b, ch)
    assert r_fin.value == THIRD, r_fin.value
    r_inf = pr_chain(inf_b, ch)
    assert r_inf.value == TWO_THIRDS, r_inf.value
    assert len(r_inf.bits) == 2, r_inf.bits
    assert r_inf.absorption == (THIRD, TWO_THIRDS), r_inf.absorption
    assert r_inf.bits == (False, True), r_inf.bits
    print(f"F-O ok: Pr(finitely many b) = 1/3, Pr(infinitely many b) = 2/3 "
          f"(absorption {r_inf.absorption}, theta {r_inf.bits})")


def main() -> None:
    check_fm()
    check_fn()
    check_fo()
    print("SUCCESS")


if __name__ == "__main__":
    main()
