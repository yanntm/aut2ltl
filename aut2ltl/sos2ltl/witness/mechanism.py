"""The ω-blindness mechanism test — paper Proposition 4.5, the right-ideal
sufficient condition for a linear-only (H5) certificate.

A period-`> 1` power-orbit cycle `C` (a nontrivial group of the algebra) is a
**right ideal** when `C · λ(Σ) ⊆ C`: once the orbit is entered, no letter
leaves it. Prop 4.5(i): a right-ideal cycle has every ω-power pattern through
it constant. Prop 4.5(ii): if *every* period-`> 1` cycle is a right ideal the
language is ω-blind — no ω-power (F₂) certificate exists, only linear (F₁).

Pure table computation on `(𝒞, λ, M)`: the letters generate `𝒞`, so closure
under the letter classes `λ(Σ)` is closure under all of `𝒞`. The distinct
cycles are collected once (many classes share one orbit's group).
"""
from __future__ import annotations

from typing import FrozenSet, List

from sosl.sos import Invariant
from sosl.sos.classify.aperiodic import orbit


def period_cycles(inv: Invariant) -> List[FrozenSet[int]]:
    """The distinct period-`> 1` power-orbit cycles of `inv` (the nontrivial
    groups), each as a frozenset of class ids."""
    seen: set = set()
    out: List[FrozenSet[int]] = []
    for c in range(inv.n):
        o = orbit(inv, c)
        if o.period > 1:
            cyc = frozenset(o.cycle)
            if cyc not in seen:
                seen.add(cyc)
                out.append(cyc)
    return out


def is_right_ideal(inv: Invariant, cyc: FrozenSet[int]) -> bool:
    """Whether `cyc` is closed under right-multiplication by every letter
    class — `cyc · λ(Σ) ⊆ cyc`, i.e. a right ideal (letters generate `𝒞`)."""
    letters = set(inv.letter_class)
    return all(inv.mult[c][lc] in cyc for c in cyc for lc in letters)


def omega_blind_by_right_ideal(inv: Invariant) -> bool:
    """True iff every period-`> 1` cycle is a right ideal — Prop 4.5(ii)'s
    sufficient condition for ω-blindness (every certificate linear). Vacuously
    true on an aperiodic invariant (no period-`> 1` cycle), where it is moot."""
    return all(is_right_ideal(inv, cyc) for cyc in period_cycles(inv))


def is_phase_collapse(inv: Invariant, cyc: FrozenSet[int]) -> bool:
    """Whether `cyc` *phase-collapses*: for every suffix class `y`, the
    idempotent power `(c·y)^π` is one class independent of `c ∈ cyc`. Then
    `Val(x, c·y)` is phase-free, so the cycle carries no ω-power certificate.
    Weaker than a right ideal (which forces `c·y ∈ cyc`, a single idempotent):
    here `c·y` may leave `cyc` as long as it leaves into a region of uniform
    idempotent power (paper F7's second mechanism)."""
    for y in range(inv.n):
        if len({inv.idempotent_power(inv.mult[c][y]) for c in cyc}) > 1:
            return False
    return True


def omega_blind_by_phase_collapse(inv: Invariant) -> bool:
    """True iff every period-`> 1` cycle phase-collapses — the candidate exact
    (idempotent-level) condition for ω-blindness (F7). Implies, and is implied
    by a right ideal in one direction (`right ideal ⟹ phase-collapse`); whether
    it coincides with ω-blindness is the census question."""
    return all(is_phase_collapse(inv, cyc) for cyc in period_cycles(inv))


__all__ = ["period_cycles", "is_right_ideal", "omega_blind_by_right_ideal",
           "is_phase_collapse", "omega_blind_by_phase_collapse"]
