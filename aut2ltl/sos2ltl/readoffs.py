"""Pure read-offs of an invariant `(𝒞, λ, M, P)` — no automaton, no oracle.

Each function is one scan of the tables of a `sosl.sos.Invariant`:

  - the λ-quotient of the alphabet (which letters the language distinguishes);
  - the residual (right-congruence) partition of the classes;
  - prefix-independence, as the loop-determinacy equation on `P`;
  - the absorbing classes (where a walk has committed);
  - the complement, by flipping `P` within the linked pairs.

The aperiodicity verdict is `sosl.sos.classify.aperiodic`, not here.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from sosl.sos import Invariant, Letter


def letter_quotient(inv: Invariant) -> Dict[int, Tuple[Letter, ...]]:
    """The λ-quotient blocks: each letter class that some letter maps to,
    with the letters mapping to it in ascending mask order. Two letters in
    one block are indistinguishable to the language in every context; an
    engine works over the blocks and restores concrete letters last."""
    blocks: Dict[int, List[Letter]] = {}
    for a, c in enumerate(inv.letter_class):
        blocks.setdefault(c, []).append(Letter(a))
    return {c: tuple(letters) for c, letters in blocks.items()}


def is_prefix_independent(inv: Invariant) -> bool:
    """Whether the language is prefix-independent: `P` is loop-determined —
    `(s, e) ∈ P ⟺ (e, e) ∈ P` for every linked pair `(s, e)`. Then no stem
    manipulation moves any verdict (every lasso's verdict is its loop's)."""
    return all(
        ((s, e) in inv.accept) == ((e, e) in inv.accept)
        for (s, e) in inv.linked_pairs()
    )


def residual_partition(inv: Invariant) -> Tuple[int, ...]:
    """The residual (right-congruence) class of every algebra class: index `c`
    holds the id of `c`'s block, ids numbered by ascending least member.

    Two classes have the same residual exactly when they have the same tail
    language, `T_c = T_d`. A tail `z·y^ω` read from `c` lands on the linked
    pair `(c·s, e)` with `(s, e) = ([z]·[y]^π, [y]^π)`, and every linked pair
    arises this way, so `T_c = T_d ⟺ ∀ (s,e) ∈ linked : (c·s, e) ∈ P ⟺
    (d·s, e) ∈ P`. The syntactic congruence refines the right congruence, so
    this is exactly the Myhill–Nerode residual of `c`'s words — read off `P`
    alone, with no dependence on the `.sos` residuals trailer (optional, and
    absent from a learner's export)."""
    pairs = sorted(inv.linked_pairs())
    accept = inv.accept
    signature: Dict[int, Tuple[bool, ...]] = {
        c: tuple((inv.mult[c][s], e) in accept for (s, e) in pairs)
        for c in range(inv.n)
    }
    ids: Dict[Tuple[bool, ...], int] = {}
    out: List[int] = []
    for c in range(inv.n):
        out.append(ids.setdefault(signature[c], len(ids)))
    return tuple(out)


def absorbing_classes(inv: Invariant) -> Tuple[int, ...]:
    """The classes fixed by every letter action: `c·λ(a) = c` for all letters
    `a` — hence by every non-empty word. A prefix-class walk that reaches one
    never leaves it; acceptance from there is entirely the tail's business."""
    letter_classes = set(inv.letter_class)
    return tuple(
        c for c in range(inv.n)
        if c != inv.identity
        and all(inv.mult[c][d] == c for d in letter_classes)
    )


def complemented(inv: Invariant) -> Invariant:
    """The invariant of the complement language: same classes and tables,
    `P` flipped within the linked pairs."""
    return Invariant(
        alphabet=inv.alphabet,
        keys=inv.keys,
        letter_class=inv.letter_class,
        mult=inv.mult,
        accept=frozenset(inv.linked_pairs() - inv.accept),
        identity=inv.identity,
    )
