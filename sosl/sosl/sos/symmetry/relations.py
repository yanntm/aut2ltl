"""Relational read-offs: which factor rewritings ``u ↔ v`` a language tolerates.

One principle (the block-substitution theorem, symmetry paper Thm 4.2): ``L`` is
closed under replacing disjoint factor occurrences of ``u`` by ``v`` iff
``[u] = [v]`` in the syntactic algebra ``𝒞``. Every service here is a wrapper
around that single class equality — invisible letters (``[c] = 1``), the
``k``-block stutter ladder (``[v] = [vv]``), and the tolerated independence
relation ``Î_L`` (``[cd] = [dc]``, Thm 4.4). All product-free: folds and table
lookups only. Conventions and correctness facts: ``algorithm.md`` next to this
file; normative math: ``research_notes/sos_symmetry.md`` §4.
"""
from __future__ import annotations

from typing import FrozenSet, List, Optional, Tuple

from ..alphabet import Letter, Word
from ..invariant import Invariant

ClassId = int

# The k-block ladder is probed only for these window widths (spec §5).
LADDER_MAX_K = 3
# Skip a rung whose class-word enumeration |Σ_λ|^k exceeds this (budget guard);
# on the corpus (n ≤ 3, |Σ_λ| ≤ 8) it is never hit.
_RUNG_CAP = 200_000


def word_class(inv: Invariant, w: Word) -> ClassId:
    """The class of ``w``: the left-to-right fold of its letters' classes.
    Thin alias of `Invariant.fold` — the language-independent half of Thm 4.2."""
    return inv.fold(w)


def is_closed(inv: Invariant, u: Word, v: Word) -> bool:
    """Thm 4.2 as one function: ``L`` is ``(u ↔ v)``-closed iff ``[u] = [v]``.
    Every read-off below is a special case of this equality."""
    return inv.fold(u) == inv.fold(v)


def invisible_letters(inv: Invariant) -> FrozenSet[Letter]:
    """The letters ``m`` with ``λ(m) = [ε]`` (the unit) — padding letters ``L``
    tolerates arbitrary insertion and deletion of (Thm 4.2, ``u = c``, ``v = ε``).

    NOT `sigma.inert_aps`: an invisible letter is a class equality ``[c] = 1``;
    an inert AP is a fiber equality ``λ∘flip = λ``. Neither implies the other."""
    return frozenset(
        Letter(a)
        for a in inv.alphabet.letters()
        if inv.letter_class[a] == inv.identity
    )


def _lambda_classes(inv: Invariant) -> Tuple[ClassId, ...]:
    """``Σ_λ``: the distinct letter classes (the quotient alphabet), sorted.
    The ladder and ``Î_L`` are computed here, not over the ``2^n`` letters —
    ``[v]`` depends only on the letter classes of ``v`` (paper §4.2/§4.3)."""
    return tuple(sorted(set(inv.letter_class)))


def _class_word_class(inv: Invariant, cw: Tuple[ClassId, ...]) -> ClassId:
    """Fold a *class* word (a sequence of classes from ``Σ_λ``) under ``M``,
    starting from the unit — the class of the block ``v`` it stands for."""
    c = inv.identity
    mult = inv.mult
    for ci in cw:
        c = mult[c][ci]
    return c


def stutter_rung(inv: Invariant, k: int) -> bool:
    """The ``k``-block ladder rung (paper §4.2): ``[v] = [vv]`` for **every**
    class-word ``v`` over ``Σ_λ`` of length **exactly** ``k`` — ``|Σ_λ|^k``
    table equations, as the paper's per-rung count states. ``k = 1`` is exactly
    stutter invariance (`classify.is_stutter_invariant`, same equation).

    The rungs are **not** nested: a language can fail rung 1 (a non-idempotent
    letter) yet satisfy rung 2 (all length-2 blocks doubling-stable). That is
    what makes the *entry* rung (`ladder_entry`) a genuine parameter.

    ``k ∈ {1, 2, 3}`` only; a rung whose ``|Σ_λ|^k`` enumeration exceeds the
    budget raises (never silently passes).

    NOTE (spec §5 / paper §4.2 prose — see report To-theory F11): both write
    the rung as ``|v| ≤ k``, but that reading is nested, makes `ladder_entry`
    degenerate (only 1 or ``None``), and contradicts the paper's own
    "``|Σ_λ|^k`` equations per rung", the ``{1,2,3,None}`` F11 distribution, and
    the fixture gate ``ladder_entry(FIX_A) == 1``. The length-``= k`` reading
    here is the one every concrete assertion agrees on; the prose ``≤`` should
    read ``=``."""
    if not 1 <= k <= LADDER_MAX_K:
        raise ValueError(f"stutter_rung is defined for k in 1..{LADDER_MAX_K} (got {k})")
    sigma_l = _lambda_classes(inv)
    if len(sigma_l) ** k > _RUNG_CAP:
        raise ValueError(
            f"rung k={k} over |Σ_λ|={len(sigma_l)} exceeds budget {_RUNG_CAP}"
        )
    frontier: List[Tuple[ClassId, ...]] = [()]
    for _ in range(k):
        frontier = [w + (c,) for w in frontier for c in sigma_l]
    return all(
        _class_word_class(inv, cw) == _class_word_class(inv, cw + cw)
        for cw in frontier
    )


def ladder_entry(inv: Invariant) -> Optional[int]:
    """Where ``L`` *enters* the ``k``-block ladder: the least rung ``k ≤ 3`` with
    `stutter_rung`, or ``None`` if none of rungs 1–3 holds (paper §4.2, the new
    canonical parameter). Yields ``{1, 2, 3, None}`` because the rungs are not
    nested (see `stutter_rung`)."""
    for k in range(1, LADDER_MAX_K + 1):
        if stutter_rung(inv, k):
            return k
    return None


def independence(inv: Invariant) -> FrozenSet[Tuple[ClassId, ClassId]]:
    """``Î_L`` on the quotient alphabet (Def 4.3 / Thm 4.4): the distinct class
    pairs ``(c, d)`` with ``[cd] = [dc]`` — the largest irreflexive-symmetric
    relation whose adjacent-block swaps ``L`` tolerates. ``O(|Σ_λ|²)`` lookups.
    Symmetric and irreflexive; both orderings ``(c, d)`` and ``(d, c)`` present."""
    sigma_l = _lambda_classes(inv)
    mult = inv.mult
    return frozenset(
        (c, d)
        for c in sigma_l
        for d in sigma_l
        if c != d and mult[c][d] == mult[d][c]
    )


def independence_letters(inv: Invariant) -> FrozenSet[Tuple[Letter, Letter]]:
    """``Î_L`` lifted to minterm (letter) pairs through the ``λ``-fibers: the
    distinct letter pairs ``(a, b)`` with ``[ab] = [ba]``. A union of fiber
    rectangles over `independence` (paper §4.3)."""
    letters = inv.alphabet.letters()
    lc = inv.letter_class
    mult = inv.mult
    return frozenset(
        (Letter(a), Letter(b))
        for a in letters
        for b in letters
        if a != b and mult[lc[a]][lc[b]] == mult[lc[b]][lc[a]]
    )
