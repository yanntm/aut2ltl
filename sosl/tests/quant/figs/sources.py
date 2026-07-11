"""Build the two figure source invariants F-D and F-E, canonically.

    python3 -m tests.quant.figs.sources DEST_DIR   # write fd.sos, fe.sos
    python3 -m tests.quant.figs.sources            # verify only, print report

Both languages are the paper's own worked examples (`sos_measure.md` §3.4
and §4.1); neither is aperiodic, so neither is reachable from an LTL
formula — each is coded here as a raw finite algebra and put through the
shared `canonicalize` normal form (the same one every producer emits), so
the resulting `.sos` is language-canonical and byte-comparable.

- **F-E** (§4.1, "``b`` occurs and the first ``b`` is at an even
  position"): five classes; the kernel spans two bottom SCCs; measure
  ``p_b / (1 - p_a^2)`` — exactly ``2/3`` at uniform, ``3/4`` at
  ``p_a = 1/3``.
- **F-D** (§3.4, "some ``a`` at infinitely many even positions"): eight
  non-identity classes coded ``(r, E)`` with ``r`` a length parity and
  ``E`` a set of ``a``-offset parities; kernel ``H(k) = ℤ/2``,
  ``k = fold(aa)``; ``theta_K = 1`` so ``mu = 1`` for every full-support
  ``p``.

Run without arguments to replay every value the paper states (a
disagreement is a finding against the paper, not something to normalize).
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Tuple

from sosl.sos import Alphabet, Invariant, Letter, canonicalize, dump_invariant
from sosl.sos.calculus import Table
from sosl.quant import kernel_idempotent, measure, theta_profile

AB = Alphabet.of(["a"])                 # one AP; mask 0 renders "!a" = spec's b
B = Letter(0)                            # the spec's letter b
A = Letter(1)                            # the spec's letter a


# ------------------------------------------------------------------ #
# F-E — "b occurs and first b at even position" (paper §4.1)
# ------------------------------------------------------------------ #
def build_fe() -> Invariant:
    """The five-class invariant of §4.1.

    Raw ids: 0 = [eps]; 1 = A1 = fold(a) (odd-length b-free); 2 = A0 =
    fold(aa) (even-length b-free); 3 = F0 = fold(b) (first b even, an
    absorbing sink); 4 = F1 = fold(ab) (first b odd, absorbing). A b-free
    stem tracks length parity; once a b lands, the first-b parity freezes,
    shifted by any prefix's length parity."""
    eps, A1, A0, F0, F1 = 0, 1, 2, 3, 4
    letter_class = [0, 0]
    letter_class[B] = F0            # fold(b)
    letter_class[A] = A1            # fold(a)

    mult = [[0] * 5 for _ in range(5)]
    # identity row/column
    for d in range(5):
        mult[eps][d] = d
        mult[d][eps] = d
    # F0, F1 absorbing
    for f in (F0, F1):
        for d in range(5):
            mult[f][d] = f
    # b-free stems A1 (odd), A0 (even) times each class
    #   x b-free: length parity adds; x has a b: first-b parity shifts by len(stem)
    mult[A1][A1] = A0               # odd + odd = even
    mult[A1][A0] = A1               # odd + even = odd
    mult[A1][F0] = F1               # odd shift flips even->odd
    mult[A1][F1] = F0
    mult[A0][A1] = A1               # even + odd = odd
    mult[A0][A0] = A0               # even + even = even
    mult[A0][F0] = F0               # even shift keeps parity
    mult[A0][F1] = F1

    accept = {(F0, A0), (F0, F0), (F0, F1)}   # stem F0, any idempotent loop
    return canonicalize(AB, eps, letter_class, mult, accept)


# ------------------------------------------------------------------ #
# F-D — "some a at infinitely many even positions" (paper §3.4)
# ------------------------------------------------------------------ #
Coord = Tuple[int, frozenset]           # (r in Z/2, E subset of Z/2)


def _fd_classes() -> List[Coord]:
    subsets = [frozenset(), frozenset({0}), frozenset({1}), frozenset({0, 1})]
    return [(r, E) for r in (0, 1) for E in subsets]


def _fd_prod(x: Coord, y: Coord) -> Coord:
    (r, E), (rp, F) = x, y
    shifted = frozenset((f + r) % 2 for f in F)
    return ((r + rp) % 2, E | shifted)


def build_fd() -> Invariant:
    """The nine-class invariant of §3.4.

    Raw id 0 = [eps]; ids 1..8 = the pairs ``(r, E)`` in a fixed order.
    Product ``(r, E)*(r', F) = (r+r', E | (F+r))``; ``lambda(a) = (1,{0})``,
    ``lambda(b) = (1, {})``. A linked pair ``((r,E),(0,F))`` accepts iff
    ``r in F``; the kernel is ``{(0,{0,1}),(1,{0,1})} = Z/2`` and its
    verdict is constant 1."""
    coords = _fd_classes()
    idx: Dict[Coord, int] = {c: i + 1 for i, c in enumerate(coords)}
    eps = 0
    n = len(coords) + 1

    letter_class = [0, 0]
    letter_class[A] = idx[(1, frozenset({0}))]
    letter_class[B] = idx[(1, frozenset())]

    mult = [[0] * n for _ in range(n)]
    for d in range(n):
        mult[eps][d] = d
        mult[d][eps] = d
    for x in coords:
        for y in coords:
            mult[idx[x]][idx[y]] = idx[_fd_prod(x, y)]

    # accepting linked pairs: e = (0, F) idempotent, s*e = s, and r in F
    accept = set()
    for s in coords:
        si = idx[s]
        for e in coords:
            ei = idx[e]
            if e[0] != 0:                       # idempotents are the (0, F)
                continue
            if mult[si][ei] != si:              # linked: s*e = s
                continue
            if s[0] in e[1]:                    # r in F
                accept.add((si, ei))
    return canonicalize(AB, eps, letter_class, mult, accept)


# ------------------------------------------------------------------ #
# Verification against the paper's stated numbers
# ------------------------------------------------------------------ #
P13: Dict[Letter, Fraction] = {A: Fraction(1, 3), B: Fraction(2, 3)}


def _check_fe(fe: Invariant) -> None:
    prof = theta_profile(fe)
    assert len(prof.entries) == 2, prof.entries
    mu_u = measure(fe).value
    mu_13 = measure(fe, P13).value
    assert mu_u == Fraction(2, 3), mu_u
    assert mu_13 == Fraction(3, 4), mu_13
    print(f"F-E ok: {fe.n} classes, theta {prof.entries}, "
          f"mu = {mu_u} (uniform), {mu_13} (p_a=1/3)")


def _check_fd(fd: Invariant) -> None:
    assert fd.n == 9, fd.n
    prof = theta_profile(fd)
    assert prof.entries == (("a;a", True),), prof.entries   # single bottom SCC, theta=1
    for p in (None, P13, {A: Fraction(1, 4), B: Fraction(3, 4)}):
        assert measure(fd, p).value == Fraction(1), p
    # negative control: the non-kernel idempotent e' = fold(ba) splits
    # R-equivalent stems, so the engine must not read theta there.
    tab = Table.of(fd)
    e_prime = tab.fold((B, A))               # (0, {1})
    k = kernel_idempotent(fd)                # (0, {0,1}) = fold(aa)
    assert tab.fold((A, A)) == k, "kernel idempotent is fold(aa)"
    b, bb = tab.fold((B,)), tab.fold((B, B))
    assert tab.idem(e_prime) == e_prime, "fold(ba) is idempotent"
    assert tab.val(fd.accept, b, e_prime) is True
    assert tab.val(fd.accept, bb, e_prime) is False    # split verdict, e' non-kernel
    assert tab.val(fd.accept, b, k) is True
    assert tab.val(fd.accept, bb, k) is True           # kernel forgets the phase
    print(f"F-D ok: {fd.n} classes, theta {prof.entries}, mu = 1 for every p; "
          f"e'=fold(ba) splits (1/0), kernel k=fold(aa) merges (1/1)")


def main() -> None:
    fe, fd = build_fe(), build_fd()
    _check_fe(fe)
    _check_fd(fd)
    if len(sys.argv) > 1:
        dest = Path(sys.argv[1])
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "fe.sos").write_text(dump_invariant(fe))
        (dest / "fd.sos").write_text(dump_invariant(fd))
        print(f"wrote {dest / 'fe.sos'} and {dest / 'fd.sos'}")
    print("SUCCESS")


if __name__ == "__main__":
    main()
