"""aut2ltl/verifier/check.py — the non-LTL witness checker (membership tier).

A non-LTL witness is a counting family `(u, v, x, p)`: finite words `u`, `v`, an
ultimately-periodic tail `x = x_prefix . (x_cycle)^w` (a lasso), and a claimed
period `p > 1`, such that membership of `u . v^n . x` toggles with `n mod p`.

This module checks such a family against an INPUT omega-automaton by MEMBERSHIP
only: it asks `u . v^n . x in L` for n = 0..2p via Spot, which decides membership
through automaton intersection and so handles every acceptance type (Buchi, parity,
Rabin, generic Emerson-Lei) uniformly. No internal state is ever referenced — the
check runs on the automaton the client supplied, which is the point: membership is
language-invariant, state indices are not.

SUGGESTIVE TIER. Finitely many membership samples witness phase *distinguishability*
(the tail separates two phases of the v-orbit) but not yet *periodicity*: an
aperiodic language could mimic the pattern up to any finite n. So `ok=True`
corroborates the witness without proving it; `ok=False` (a constant / wrong-period
pattern) is a genuine red flag — the printed certificate does not check out. The
residual-equivalence upgrade that would make this a proof is deferred.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import spot

from aut2ltl.witness import Witness


# --------------------------------------------------------------------------- #
# The single load-bearing primitive: membership of a lasso word in L(A).
# --------------------------------------------------------------------------- #
def member(aut: "spot.twa_graph", word: str) -> bool:
    """True iff the ultimately-periodic omega-word `word` is in L(aut).

    Spot decides this by intersecting `aut` with the one-lasso automaton of the
    word; it is correct for any acceptance condition and any (non)determinism.
    """
    w = spot.parse_word(word, aut.get_dict()).as_automaton()
    return aut.intersects(w)


# --------------------------------------------------------------------------- #
# Building the sampled words  u . v^n . x  in Spot's omega-word syntax.
# Words are lists of letter strings, e.g. ["a", "!a"]; x is (prefix, cycle).
# --------------------------------------------------------------------------- #
def _lasso(prefix: List[str], cycle: List[str]) -> str:
    """Render an ultimately-periodic word as Spot syntax: `l; l; cycle{l; l}`."""
    if not cycle:
        raise ValueError("an omega-word needs a non-empty cycle")
    return "; ".join(prefix + ["cycle{" + "; ".join(cycle) + "}"])


def _sample_word(u: List[str], v: List[str], n: int,
                 x_prefix: List[str], x_cycle: List[str]) -> str:
    """The word  u . v^n . x  as a lasso string."""
    return _lasso(u + v * n + x_prefix, x_cycle)


# --------------------------------------------------------------------------- #
# The membership-tier check.
# --------------------------------------------------------------------------- #
def verify_suggestive(
    aut: "spot.twa_graph",
    u: List[str],
    v: List[str],
    x_prefix: List[str],
    x_cycle: List[str],
    p: int,
) -> Tuple[bool, List[bool]]:
    """Sample membership of `u.v^n.x` for n = 0..2p and decide whether the pattern
    is non-constant and periodic with period exactly `p`.

    Returns `(ok, pattern)`. `ok` is True iff the membership pattern toggles (so x
    is phase-sensitive across the v-orbit) AND repeats with period exactly p over
    the sample (a smaller period q<p would make the claimed `p` wrong). This is the
    SUGGESTIVE verdict, not yet a periodicity proof.
    """
    pattern = [
        member(aut, _sample_word(u, v, n, x_prefix, x_cycle))
        for n in range(2 * p + 1)
    ]
    non_constant = len(set(pattern)) > 1
    periodic = all(pattern[i] == pattern[i + p] for i in range(len(pattern) - p))
    minimal = all(
        not all(pattern[i] == pattern[i + q] for i in range(len(pattern) - q))
        for q in range(1, p)
    )
    return (non_constant and periodic and minimal, pattern)


def verify(aut: "spot.twa_graph", w: Witness) -> Tuple[Optional[bool], List[bool]]:
    """Check a `Witness` against `aut` by membership. Returns `(ok, pattern)` as
    `verify_suggestive`; `(None, [])` when the family is incomplete (no `u`/`x` to
    replay), which the caller reads as "no checkable witness", not a failure."""
    if not w.complete:
        return (None, [])
    return verify_suggestive(
        aut, u=w.u or [], v=w.v,
        x_prefix=w.x_prefix or [], x_cycle=w.x_cycle or [], p=w.p,
    )


__all__ = ["member", "verify_suggestive", "verify"]
