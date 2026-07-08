"""Canonicalize a `.sos` invariant up to **AP relabeling** — the signed
permutations of the atomic propositions (`B_k`, order `2^k·k!`).

The `.sos` format is already byte-canonical *given* a labeling of the APs: it
fixes the AP order to lexicographic-by-name and the letter order to
`absent < present` (`sos_format.md`). The one symmetry it does **not** quotient is
which physical proposition is named `a`/`b`/… (permutation) and which polarity is
"present" (sign) — exactly `B_k`. So `GF(a)` and `GF(!a)`, or an `a↔b` twin, are
distinct `.sos` bytes for the same language *up to relabeling*.

`canonical_invariant` folds that symmetry: over all `|B_k| ≤ 48` (for `k ≤ 3`)
signed permutations it re-keys the algebra (relabel the generators, recompute the
shortlex-least class keys, renumber) and returns the representative whose
**semigroup core** (`ap; classes; letters; mult`) is byte-least. Selection ignores
`accept`, so a language and its complement — which share every section but
`accept` — pick the **same** representative, preserving the byte relation
"complement = flip accept" the classifier's duality gate relies on.
"""
from __future__ import annotations

import itertools
from collections import deque
from typing import Iterator, List, Tuple

from .alphabet import EMPTY, Alphabet, Letter, Word, shortlex_key
from .invariant import Invariant
from .io.serialize import dump_invariant, load_invariant

# A signed permutation, identified by (permutation of AP slots, flip bitmask); its
# realization is `rho`, the induced permutation of letter masks (old → new).
Sigma = Tuple[Tuple[int, ...], int]


def mask_perms(k: int) -> Iterator[Tuple[Sigma, List[int]]]:
    """Yield every signed AP permutation of `B_k` as `((pi, flips), rho)`, where
    `rho[old_mask] = new_mask`. Identity is first. A mask's bit for `aps[i]` is
    bit `k-1-i` (letter rank), matching `alphabet.py`."""
    for pi in itertools.permutations(range(k)):
        for flips in range(1 << k):
            rho = [0] * (1 << k)
            for om in range(1 << k):
                nm = 0
                for j in range(k):
                    chi = (om >> (k - 1 - pi[j])) & 1        # value of old AP pi[j]
                    fj = (flips >> (k - 1 - j)) & 1           # flip for new slot j
                    nm |= (chi ^ fj) << (k - 1 - j)
                rho[om] = nm
            yield (pi, flips), rho


def relabel_invariant(inv: Invariant, rho: List[int]) -> Invariant:
    """Apply the letter-mask permutation `rho` to `inv`'s generators and return the
    re-canonicalized invariant: same abstract semigroup, but keys recomputed for the
    new letter order and classes renumbered by shortlex of those keys."""
    size, n = inv.alphabet.size, inv.n

    # The relabeled generator map: letter `rho[om]` now plays old letter `om`'s role.
    plc = [0] * size
    for om in range(size):
        plc[rho[om]] = inv.letter_class[om]

    # Shortlex-least key per class: BFS from the identity, letters in mask order.
    key: List[Word] = [None] * n            # type: ignore[list-item]
    key[inv.identity] = EMPTY
    dq = deque([inv.identity])
    while dq:
        c = dq.popleft()
        for m in range(size):
            c2 = inv.mult[c][plc[m]]
            if key[c2] is None:
                key[c2] = key[c] + (Letter(m),)
                dq.append(c2)

    # Renumber classes by shortlex of their new keys (identity, key ε, becomes 0).
    order = sorted(range(n), key=lambda c: shortlex_key(key[c]))
    newid = [0] * n
    for nid, oldc in enumerate(order):
        newid[oldc] = nid

    return Invariant(
        alphabet=inv.alphabet,
        keys=tuple(key[order[i]] for i in range(n)),
        letter_class=tuple(newid[plc[m]] for m in range(size)),
        mult=tuple(tuple(newid[inv.mult[order[i]][order[j]]] for j in range(n))
                   for i in range(n)),
        accept=frozenset((newid[s], newid[e]) for (s, e) in inv.accept),
        identity=newid[inv.identity],
    )


def _semigroup_core(dump: str) -> str:
    """The acceptance-independent prefix of a `.sos` dump — `ap` through `mult`,
    the sections shared by a language and its complement."""
    return dump.split("accept:", 1)[0]


def canonical_relabeling(inv: Invariant) -> Tuple[Sigma, Invariant]:
    """The `B_k` orbit representative of `inv` and the signed permutation that
    reaches it: the relabeling whose semigroup core is byte-least (ties broken by
    the signed permutation's own order, never by `accept`). The returned `Sigma`
    can be replayed on any presentation of the language (e.g. its det HOA) so the
    automaton and the `.sos` land in the same canonical labeling."""
    k = len(inv.alphabet.aps)
    best: Invariant = inv
    best_sigma: Sigma = ((), 0)
    best_key: Tuple[str, Sigma] = ("", ((), 0))
    first = True
    for sigma, rho in mask_perms(k):
        cand = relabel_invariant(inv, rho)
        candkey = (_semigroup_core(dump_invariant(cand)), sigma)
        if first or candkey < best_key:
            best, best_sigma, best_key, first = cand, sigma, candkey, False
    return best_sigma, best


def canonical_invariant(inv: Invariant) -> Invariant:
    """The `B_k` orbit representative of `inv` (see `canonical_relabeling`)."""
    return canonical_relabeling(inv)[1]


def canonical_sos(text: str) -> str:
    """Load a `.sos` dump, fold its AP-relabeling symmetry, and re-dump. Byte-equal
    outputs ⟺ equal languages **up to AP relabeling**. The residuals trailer, if
    any, is dropped (not part of the language identity)."""
    return dump_invariant(canonical_invariant(load_invariant(text)))
