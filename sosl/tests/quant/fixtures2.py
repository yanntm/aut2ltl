"""Fixtures F-D through F-I: hand-computed ground truth for the measure
engine's kernel discipline and for distance / shadow / essential.

    python3 -m tests.quant.fixtures2

Alphabet: one AP ``a``; the spec's letter *b* is mask 0 (rendered ``!a``),
the spec's letter *a* is mask 1 (rendered ``a``). Positions are 0-indexed.

- F-D: "some a at infinitely many even positions" — 8 non-identity
  classes (p, E), kernel = Z/2, mu = 1 under every p; the non-kernel
  idempotent fold(ba) is a negative control (Val differs across stems).
- F-E: "b occurs and the first b is at an even position" — 5 classes,
  kernel spans two bottom SCCs, mu = p_b / (1 - p_a^2).
- F-F: shadow of F-A ("infinitely many a's") is byte-equal to the reduced
  invariant of "some a occurs".
- F-G (negative control, expected to hold as stated, never "fixed"):
  Sigma*.b.Sigma^omega vs Sigma^omega have distance 0 (all-zero xor
  profile) yet byte-DIFFERENT reduced shadows.
- F-H: their essential forms are byte-EQUAL (both Sigma^omega) — the
  repair of F-G.
- F-I: on F-E the value congruence merges [eps] with the neutral class
  only, the quotient retains Z/2, essential(F-E) is (reduced) F-E, and
  ltl_up_to_null(F-E) is False (True on F-A).

Plus the generic M3 laws on every fixture language: d(L, shadow(L)) = 0,
d(L, essential(L)) = 0, idempotence of both, and byte-equality of the
essential form across two p's (Prop 4.5). Exact equality throughout;
prints SUCCESS iff all pass.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Tuple

from sosl.sos import Alphabet, Invariant, Letter, dump_invariant
from sosl.sos.calculus import Table, reduce
from sosl.quant import (
    bottom_sccs,
    congruence_classes,
    distance,
    essential,
    kernel,
    kernel_idempotent,
    ltl_up_to_null,
    measure,
    shadow,
    theta_profile,
)

AB = Alphabet.of(["a"])
B_LETTER = Letter(0)  # rendered "!a" — the spec's letter b
A_LETTER = Letter(1)  # rendered "a"  — the spec's letter a
P13: Dict[Letter, Fraction] = {A_LETTER: Fraction(1, 3), B_LETTER: Fraction(2, 3)}

FdElem = Tuple[int, frozenset]


def build(keys: tuple, letter_class: tuple, mult: tuple, accept: frozenset) -> Invariant:
    """A validated invariant over the shared one-AP alphabet."""
    inv = Invariant(
        alphabet=AB,
        keys=keys,
        letter_class=letter_class,
        mult=mult,
        accept=accept,
        identity=0,
    )
    inv.validate()
    return inv


def build_fd() -> Invariant:
    """F-D from its (p, E) semantics: p = length parity, E = the set of
    position parities carrying an *a*; classes discovered by shortlex BFS
    so the numbering is canonical."""

    def mul(u: FdElem, v: FdElem) -> FdElem:
        return ((u[0] + v[0]) % 2, u[1] | frozenset((u[0] + q) % 2 for q in v[1]))

    gen: Dict[Letter, FdElem] = {
        B_LETTER: (1, frozenset()),
        A_LETTER: (1, frozenset({0})),
    }
    keys: List[tuple] = [()]
    elems: List[FdElem] = [(0, frozenset())]  # placeholder slot for [eps]
    ids: Dict[FdElem, int] = {}
    frontier: List[Tuple[tuple, FdElem]] = [((), None)]  # type: ignore[list-item]
    queue: List[Tuple[tuple, FdElem]] = []
    for word, elem in frontier:
        for a in (B_LETTER, A_LETTER):
            queue.append((word + (a,), gen[a]))
    while queue:
        word, elem = queue.pop(0)
        if elem in ids:
            continue
        ids[elem] = len(elems)
        keys.append(word)
        elems.append(elem)
        for a in (B_LETTER, A_LETTER):
            queue.append((word + (a,), mul(elem, gen[a])))
    n = len(elems)
    assert n == 9, f"F-D must have 8 non-identity classes, got {n - 1}"

    def cls(e: FdElem) -> int:
        return ids[e]

    mult = [[0] * n for _ in range(n)]
    for i in range(n):
        mult[0][i] = i
        mult[i][0] = i
    for e1, i in ids.items():
        for e2, j in ids.items():
            mult[i][j] = cls(mul(e1, e2))
    accept = frozenset(
        (s, e)
        for e_val, e in ids.items()
        if mul(e_val, e_val) == e_val
        for s_val, s in ids.items()
        if mul(s_val, e_val) == s_val and (s_val[0] % 2) in e_val[1]
    )
    return build(
        tuple(keys),
        tuple(ids[gen[a]] for a in (B_LETTER, A_LETTER)),
        tuple(tuple(row) for row in mult),
        accept,
    )


def check_fd() -> None:
    """F-D: kernel = Z/2 at full E, k = fold(aa), mu = 1 under both p's;
    the non-kernel idempotent fold(ba) is rejected as a theta reader."""
    fd = build_fd()
    full = fd.fold((A_LETTER, A_LETTER))
    odd_full = fd.fold((A_LETTER, A_LETTER, A_LETTER))
    assert kernel(fd) == frozenset({full, odd_full}), "kernel must be Z/2"
    assert kernel_idempotent(fd) == full, "k must be fold(aa)"
    assert len(theta_profile(fd).entries) == 1
    for p in (None, P13):
        assert measure(fd, p).value == Fraction(1)
    e_prime = fd.fold((B_LETTER, A_LETTER))
    assert fd.mult[e_prime][e_prime] == e_prime, "fold(ba) must be idempotent"
    assert e_prime not in kernel(fd), "fold(ba) must lie outside the kernel"
    table = Table.of(fd)
    v_b = table.val(fd.accept, fd.fold((B_LETTER,)), e_prime)
    v_bb = table.val(fd.accept, fd.fold((B_LETTER, B_LETTER)), e_prime)
    assert (v_b, v_bb) == (True, False), (
        "negative control: Val must differ across stems on fold(ba)"
    )
    print("F-D ok: 9 classes, kernel Z/2, k = fold(aa), mu = 1; "
          "non-kernel idempotent convicted")


def build_fe() -> Invariant:
    """F-E: classes [eps], B0 (first b even), O (odd all-a), B1 (first b
    odd), E (even nonempty all-a); B0/B1 absorb, E is neutral, O carries
    the parity flip."""
    return build(
        ((), (B_LETTER,), (A_LETTER,), (A_LETTER, B_LETTER), (A_LETTER, A_LETTER)),
        (1, 2),
        ((0, 1, 2, 3, 4),
         (1, 1, 1, 1, 1),
         (2, 3, 4, 1, 2),
         (3, 3, 3, 3, 3),
         (4, 1, 2, 3, 4)),
        frozenset({(1, 1), (1, 3), (1, 4)}),
    )


def check_fe() -> Invariant:
    """F-E: kernel {B0, B1} spans the two bottom SCCs; mu = p_b/(1-p_a^2)."""
    fe = build_fe()
    assert bottom_sccs(fe) == [frozenset({1}), frozenset({3})]
    assert kernel(fe) == frozenset({1, 3}), "kernel must span both bottom SCCs"
    assert theta_profile(fe).entries == (("!a", True), ("a;!a", False))
    assert measure(fe).value == Fraction(2, 3), measure(fe).value
    assert measure(fe, P13).value == Fraction(3, 4), measure(fe, P13).value
    print("F-E ok: 5 classes, kernel across two bottom SCCs, mu = 2/3 | 3/4")
    return fe


def check_ff(fa: Invariant) -> None:
    """F-F: shadow(F-A) byte-equal the reduced invariant of 'some a'."""
    some_a = build(
        ((), (B_LETTER,), (A_LETTER,)),
        (1, 2),
        ((0, 1, 2), (1, 1, 2), (2, 2, 2)),
        frozenset({(2, 2), (2, 1)}),
    )
    assert dump_invariant(shadow(fa)) == dump_invariant(
        reduce(Table.of(some_a), some_a.accept)
    ), "shadow(F-A) must be 'some a occurs'"
    print("F-F ok: shadow('infinitely many a') = 'some a', byte-equal")


def build_fg() -> Tuple[Invariant, Invariant]:
    """F-G's pair: L = Sigma*.b.Sigma^omega ('some b occurs') and
    Sigma^omega, over the shared alphabet."""
    some_b = build(
        ((), (B_LETTER,), (A_LETTER,)),
        (1, 2),
        ((0, 1, 2), (1, 1, 1), (2, 1, 2)),
        frozenset({(1, 1), (1, 2)}),
    )
    sigma = build(
        ((), (B_LETTER,)),
        (1, 1),
        ((0, 1), (1, 1)),
        frozenset({(1, 1)}),
    )
    return some_b, sigma


def check_fg_fh() -> None:
    """F-G: distance 0 with all-zero xor profile YET byte-different
    shadows (do NOT fix); F-H: the essential forms are byte-equal."""
    some_b, sigma = build_fg()
    for p in (None, P13):
        d = distance(some_b, sigma, p)
        assert d.value == 0 and d.null_disagreement, (p, d.value)
    sh_b, sh_s = shadow(some_b), shadow(sigma)
    assert dump_invariant(sh_b) != dump_invariant(sh_s), (
        "F-G control: the shadows must stay byte-DIFFERENT"
    )
    assert dump_invariant(sh_b) == dump_invariant(
        reduce(Table.of(some_b), some_b.accept)
    ), "shadow('some b') must be 'some b' itself"
    assert dump_invariant(sh_s) == dump_invariant(
        reduce(Table.of(sigma), sigma.accept)
    ), "shadow(Sigma^omega) must be Sigma^omega"
    es_b, es_s = essential(some_b), essential(sigma)
    assert dump_invariant(es_b) == dump_invariant(es_s), (
        "F-H: essential forms must agree where the shadows differ"
    )
    assert dump_invariant(es_s) == dump_invariant(
        reduce(Table.of(sigma), sigma.accept)
    ), "essential(Sigma^omega) must be Sigma^omega"
    print("F-G ok: d = 0, shadows byte-different (control held); "
          "F-H ok: essential forms byte-equal")


def check_fi(fa: Invariant, fe: Invariant) -> None:
    """F-I: the value congruence on F-E merges [eps] with the neutral E
    only; the quotient keeps Z/2; essential(F-E) is reduced F-E."""
    blocks = congruence_classes(fe)
    assert blocks == (frozenset({0, 4}), frozenset({1}), frozenset({2}),
                      frozenset({3})), blocks
    assert dump_invariant(essential(fe)) == dump_invariant(
        reduce(Table.of(fe), fe.accept)
    ), "essential(F-E) must be F-E itself, reduced"
    assert ltl_up_to_null(fe) is False, "F-E keeps its Z/2 up to null sets"
    assert ltl_up_to_null(fa) is True, "F-A is aperiodic already"
    print("F-I ok: congruence merges [eps]+E only, Z/2 retained, "
          "essential(F-E) = F-E, ltl_up_to_null False (F-A True)")


def check_laws(name: str, inv: Invariant) -> None:
    """The generic M3 laws on one language: zero distance to shadow and
    essential, idempotence of both, Prop 4.5 p-independence."""
    sh = shadow(inv)
    es = essential(inv)
    for other in (sh, es):
        d = distance(inv, other)
        assert d.value == 0 and d.null_disagreement, (name, d.value)
    assert dump_invariant(shadow(sh)) == dump_invariant(sh), name
    assert dump_invariant(essential(es)) == dump_invariant(es), name
    assert dump_invariant(essential(inv, P13)) == dump_invariant(es), (
        f"{name}: Prop 4.5 violated — essential form depends on p"
    )
    print(f"laws ok on {name}: d(L, shadow) = d(L, essential) = 0, "
          "idempotent, p-free")


def main() -> None:
    fa = build(
        ((), (B_LETTER,), (A_LETTER,)),
        (1, 2),
        ((0, 1, 2), (1, 1, 2), (2, 2, 2)),
        frozenset({(2, 2)}),
    )
    check_fd()
    fe = check_fe()
    check_ff(fa)
    check_fg_fh()
    check_fi(fa, fe)
    some_b, sigma = build_fg()
    for name, inv in (("F-A", fa), ("F-E", fe), ("some-b", some_b),
                      ("Sigma^omega", sigma)):
        check_laws(name, inv)
    print("SUCCESS")


if __name__ == "__main__":
    main()
