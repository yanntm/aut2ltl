"""The theta-profile: one canonical bit per bottom SCC.

For a bottom SCC ``C`` of the right-Cayley graph, the generic verdict is

    theta_C := Val(c, k) = ((M(c, k), k) in P)

for any ``c in C`` and any kernel idempotent ``k`` — the value depends on
neither choice (see algorithm.md §3), which `PARANOID` re-checks on every
call from a second representative and a second kernel element. Entries
are keyed by the rendered shortlex key of the SCC's least class, in the
canonical bottom-SCC order of `chain.bottom_sccs`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, List, Tuple

from ..sos.alphabet import shortlex_key
from ..sos.calculus.table import Table
from ..sos.invariant import Invariant
from ..sos.io.serialize import render_word
from .chain import bottom_sccs, least_key_class
from .kernel import kernel

PARANOID: bool = True
"""Re-derive every theta bit from alternate choices and assert agreement."""


@dataclass(frozen=True)
class ThetaProfile:
    """The theta bits of a language, one per bottom SCC: ``(rendered least
    class key of the SCC, theta)`` in the canonical bottom-SCC order."""

    entries: Tuple[Tuple[str, bool], ...]


def _ident(inv: Invariant) -> str:
    """A short identifying tag for assertion messages."""
    return f"n={inv.n}, ap={' '.join(inv.alphabet.aps) or '-'}"


def theta_profile(inv: Invariant) -> ThetaProfile:
    """The theta-profile of ``inv``'s language: for each bottom SCC of the
    right-Cayley graph (canonical order), the generic verdict
    ``Val(c, k)`` of its least-keyed class ``c`` against one kernel
    idempotent ``k``."""
    table = Table.of(inv)
    bottoms: List[FrozenSet[int]] = bottom_sccs(inv)
    ker = kernel(inv)
    t = least_key_class(inv, ker)
    k = inv.idempotent_power(t)
    reps = [least_key_class(inv, scc) for scc in bottoms]
    entries = tuple(
        (render_word(inv.alphabet, inv.keys[c]), table.val(inv.accept, c, k))
        for c in reps
    )
    if PARANOID:
        _paranoid(inv, table, bottoms, reps, entries, ker, k)
    return ThetaProfile(entries)


def _paranoid(
    inv: Invariant,
    table: Table,
    bottoms: List[FrozenSet[int]],
    reps: List[int],
    entries: Tuple[Tuple[str, bool], ...],
    ker: FrozenSet[int],
    k: int,
) -> None:
    """The Lemma 3.3 invariances, asserted numerically: theta from another
    class of the same bottom SCC, and theta under another kernel
    idempotent, agree with ``entries``; the profile has one entry per
    bottom SCC."""
    assert len(entries) == len(bottoms), _ident(inv)
    for scc, rep, (key_str, bit) in zip(bottoms, reps, entries):
        if len(scc) > 1:
            other = max(scc, key=lambda c: shortlex_key(inv.keys[c]))
            assert other != rep
            got = table.val(inv.accept, other, k)
            assert got == bit, (
                f"theta differs across the bottom SCC of key '{key_str}': "
                f"{bit} at class {rep}, {got} at class {other} ({_ident(inv)})"
            )
    if len(ker) > 1:
        t2 = max(ker, key=lambda c: shortlex_key(inv.keys[c]))
        k2 = inv.idempotent_power(t2)
        for rep, (key_str, bit) in zip(reps, entries):
            got = table.val(inv.accept, rep, k2)
            assert got == bit, (
                f"theta differs across kernel idempotents at SCC key "
                f"'{key_str}': {bit} under k={k}, {got} under k'={k2} "
                f"({_ident(inv)})"
            )
