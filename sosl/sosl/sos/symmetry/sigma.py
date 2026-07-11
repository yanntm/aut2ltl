"""Signed permutations of the atomic propositions and the single-candidate
symmetry checks on a canonical invariant.

Conventions (AP-index/mask-bit correspondence, action and composition
equations) and the check algorithms with their correctness facts are stated in
`algorithm.md` next to this file; the checks are product-free by design — one
letter-map rewire, one keying-only reduce, one byte comparison.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import FrozenSet, Iterator, Tuple

from ..alphabet import Letter, Word
from ..invariant import Invariant
from ..io.serialize import dump_invariant
from ..calculus.reduce import reduce
from ..calculus.surgery import inverse_substitution
from ..calculus.table import Table


@dataclass(frozen=True)
class SignedPerm:
    """An element of the signed permutation group B_n = (Z/2)^n ⋊ S_n.

    ``perm[i]`` is the image *position* of AP index ``i``; ``flip[i]`` is the
    polarity flip applied to source AP ``i``. Components are indexed by AP
    index in the invariant's stored order; the mask-bit conversion (AP ``i``
    on bit ``n-1-i``) happens only inside `__call__`.
    """

    perm: Tuple[int, ...]
    flip: Tuple[bool, ...]

    def __post_init__(self) -> None:
        n = len(self.perm)
        if len(self.flip) != n or sorted(self.perm) != list(range(n)):
            raise ValueError(f"malformed SignedPerm {self.perm}/{self.flip}")

    @property
    def n(self) -> int:
        """The number of atomic propositions acted on."""
        return len(self.perm)

    @classmethod
    def identity(cls, n: int) -> "SignedPerm":
        return cls(tuple(range(n)), (False,) * n)

    @classmethod
    def transposition(cls, n: int, i: int, j: int) -> "SignedPerm":
        """Exchange AP positions ``i`` and ``j``, no flips."""
        p = list(range(n))
        p[i], p[j] = p[j], p[i]
        return cls(tuple(p), (False,) * n)

    @classmethod
    def polarity_flip(cls, n: int, i: int) -> "SignedPerm":
        """Negate AP ``i``, identity on positions."""
        return cls(tuple(range(n)), tuple(k == i for k in range(n)))

    def __call__(self, m: Letter) -> Letter:
        """The action on a minterm: ``(σ·m)[perm[i]] = m[i] XOR flip[i]``."""
        n = self.n
        out = 0
        for i in range(n):
            bit = (m >> (n - 1 - i)) & 1
            if self.flip[i]:
                bit ^= 1
            if bit:
                out |= 1 << (n - 1 - self.perm[i])
        return Letter(out)

    def act_word(self, w: Word) -> Word:
        """Letterwise action on a word."""
        return tuple(self(a) for a in w)

    def compose(self, other: "SignedPerm") -> "SignedPerm":
        """``self ∘ other`` — apply ``other`` first."""
        perm = tuple(self.perm[other.perm[i]] for i in range(self.n))
        flip = tuple(
            other.flip[i] ^ self.flip[other.perm[i]] for i in range(self.n)
        )
        return SignedPerm(perm, flip)

    def inverse(self) -> "SignedPerm":
        """The group inverse: ``perm⁻¹[perm[i]] = i``,
        ``flip⁻¹[perm[i]] = flip[i]``."""
        n = self.n
        q = [0] * n
        f = [False] * n
        for i in range(n):
            q[self.perm[i]] = i
            f[self.perm[i]] = self.flip[i]
        return SignedPerm(tuple(q), tuple(f))


def apply_perm(inv: Invariant, sigma: SignedPerm) -> Invariant:
    """The canonical invariant of ``σ⁻¹L``: rewire ``λ' = λ∘σ`` (the free
    inverse substitution along ``σ``), then a keying-only reduce. The class
    count must survive — ``σ`` permutes ``Σ``, so the generator set and hence
    the congruence are unchanged; a merge convicts the input or `reduce`."""
    if len(sigma.perm) != len(inv.alphabet.aps):
        raise ValueError(
            f"arity mismatch: |σ| = {len(sigma.perm)}, "
            f"|AP| = {len(inv.alphabet.aps)}"
        )
    table = Table.of(inv)
    rewired, moved = inverse_substitution(table, inv.accept, inv.alphabet, sigma)
    red = reduce(rewired, moved)
    if red.n != inv.n:
        raise AssertionError(
            f"apply_perm merged classes ({inv.n} -> {red.n}): input not "
            "syntactic, or reduce is broken — report, do not continue"
        )
    return red


def is_symmetry(inv: Invariant, sigma: SignedPerm) -> bool:
    """``σ(L) = L``: canonical keys of ``apply_perm(inv, σ)`` byte-equal to
    ``inv``'s. Requires ``inv`` canonical."""
    return dump_invariant(apply_perm(inv, sigma)) == dump_invariant(inv)


def is_antisymmetry(inv: Invariant, sigma: SignedPerm) -> bool:
    """``σ(L) = L^c``: canonical keys byte-equal to the free complement's
    (a ``P``-flip on the same algebra — keying is unaffected)."""
    return dump_invariant(apply_perm(inv, sigma)) == dump_invariant(
        inv.complement()
    )


def in_kernel(inv: Invariant, sigma: SignedPerm) -> bool:
    """The fiber read-off ``∀m: λ(σ(m)) = λ(m)`` — sufficient for
    `is_symmetry` (the kernel law), never necessary."""
    lc = inv.letter_class
    return all(lc[sigma(a)] == lc[a] for a in inv.alphabet.letters())


def inert_aps(inv: Invariant) -> FrozenSet[int]:
    """AP indices whose polarity flip is in the kernel — propositions the
    language is semantically blind to."""
    n = len(inv.alphabet.aps)
    return frozenset(
        i for i in range(n) if in_kernel(inv, SignedPerm.polarity_flip(n, i))
    )


def anti_possible(inv: Invariant) -> bool:
    """The pair-count obstruction: an anti-symmetry bijects ``P`` onto
    ``linked ∖ P``, so ``2·|P| ≠ |linked|`` refutes every anti-candidate.
    The only sanctioned fast path: when False, anti checks may be skipped."""
    return 2 * len(inv.accept) == len(inv.linked_pairs())


def generators_b_ap(n: int) -> Tuple[SignedPerm, ...]:
    """The standard generators of B_n: all transpositions ``(i j)``, ``i < j``,
    then all polarity flips, in deterministic order."""
    gens = [
        SignedPerm.transposition(n, i, j)
        for i in range(n)
        for j in range(i + 1, n)
    ]
    gens += [SignedPerm.polarity_flip(n, i) for i in range(n)]
    return tuple(gens)


def all_b_ap(n: int) -> Iterator[SignedPerm]:
    """Every element of B_n (``2^n · n!`` of them), deterministic order.
    Guarded to ``n ≤ 3`` — the larger-``n`` policy belongs to the group
    milestone; do not lift."""
    if n > 3:
        raise ValueError(f"all_b_ap is guarded to n <= 3 (got n = {n})")
    for perm in itertools.permutations(range(n)):
        for flips in itertools.product((False, True), repeat=n):
            yield SignedPerm(tuple(perm), tuple(flips))
