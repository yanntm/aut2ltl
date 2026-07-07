"""Certificate extraction — three scans of the invariant's tables.

On a non-aperiodic invariant, assemble a counting `Family` by pure table
computation (`algorithm.md`; paper §4.2): find the group carrier (the first
power orbit of period > 1, shortlex order), scan the class contexts of the
two shapes for a non-constant membership pattern around the carrier's
cycle, and emit the family with the orbit index absorbed so the toggle is
exact from `n = 0`. The scan cannot exhaust on a non-aperiodic invariant:
the syntactic congruence separates distinct cycle classes through some
context of one of the two shapes.

Everything is a computation on `(𝒞, λ, M, P)`: no automaton, no group
oracle, no sampling. With the fixed scan orders (ascending canonical class
ids = shortlex key order), the emitted family is a function of the language
alone.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from sosl.sos import Invariant
from sosl.sos.classify.aperiodic import Orbit, first_group

from .family import Family


def val(inv: Invariant, c: int, d: int) -> bool:
    """The membership verdict of any lasso `w·z^ω` with `[w] = c, [z] = d`:
    `(c·d^π, d^π) ∈ P`, `d^π` the idempotent power of `d`."""
    e = inv.idempotent_power(d)
    return (inv.mult[c][e], e) in inv.accept


def _min_cyclic_period(pattern: Tuple[bool, ...]) -> int:
    """The least `d` dividing `len(pattern)` with `pattern` invariant under
    rotation by `d` (the rotation-invariance periods form a subgroup)."""
    p = len(pattern)
    for d in range(1, p + 1):
        if p % d == 0 and all(pattern[i] == pattern[(i + d) % p] for i in range(p)):
            return d
    raise AssertionError("unreachable: p is always a cyclic period")


def _scan_linear(inv: Invariant, g: Orbit) -> Optional[Family]:
    """The first separating linear context `(x, y, t)` in shortlex order —
    phase `i ↦ Val(x·gᵐ⁺ⁱ·y, t)` — as a linear-shape `Family`, or None when
    every linear context is constant around the carrier's cycle."""
    m, p = g.index, g.period
    cycle: Tuple[int, ...] = g.cycle
    v = inv.keys[g.cls]
    for x in range(inv.n):
        for y in range(inv.n):
            for t in range(inv.n):
                if t == inv.identity:
                    continue
                pat = tuple(
                    val(inv, inv.mult[inv.mult[x][cycle[i]]][y], t)
                    for i in range(p))
                if len(set(pat)) > 1:
                    pp = _min_cyclic_period(pat)
                    return Family(
                        period=pp, pattern=pat[:pp],
                        u=inv.keys[x] + v * m, v=v,
                        x_prefix=inv.keys[y], x_loop=inv.keys[t])
    return None


def _scan_omega(inv: Invariant, g: Orbit) -> Optional[Family]:
    """The first separating ω-power context `(x, y)` in shortlex order —
    phase `i ↦ Val(x, gᵐ⁺ⁱ·y)` — as an ω-power-shape `Family`, or None when
    every ω-power context is constant around the carrier's cycle."""
    m, p = g.index, g.period
    cycle: Tuple[int, ...] = g.cycle
    v = inv.keys[g.cls]
    for x in range(inv.n):
        for y in range(inv.n):
            pat = tuple(
                val(inv, x, inv.mult[cycle[i]][y]) for i in range(p))
            if len(set(pat)) > 1:
                pp = _min_cyclic_period(pat)
                return Family(
                    period=pp, pattern=pat[:pp],
                    u=inv.keys[x], v=v, y=v * m + inv.keys[y])
    return None


@dataclass(frozen=True)
class DualScan:
    """Both context scans of one non-aperiodic invariant, run to completion.
    Each field is the first separating `Family` of its shape, or None when
    that shape is *all-constant* (no separating context around the cycle). At
    least one field is non-None (the congruence must separate distinct cycle
    classes through one of the two shapes)."""

    linear: Optional[Family]
    omega: Optional[Family]

    @property
    def h5_hit(self) -> bool:
        """The H5 read-off: the ω-power shape is all-constant, so the only
        certificate is linear (the dual of Proposition 4.2 blindness)."""
        return self.omega is None and self.linear is not None


def dual_scan(inv: Invariant) -> Optional[DualScan]:
    """Both shape scans of a non-aperiodic invariant to completion (the E7
    dual-scan datum: which shapes *can* separate, not merely which fires
    first), or None when the invariant is aperiodic (LTL-definable)."""
    g: Optional[Orbit] = first_group(inv)
    if g is None:
        return None
    lin = _scan_linear(inv, g)
    om = _scan_omega(inv, g)
    if lin is None and om is None:
        raise AssertionError(
            "separation scan exhausted on a non-aperiodic invariant "
            "(malformed tables: the syntactic congruence must separate "
            "distinct cycle classes)")
    return DualScan(linear=lin, omega=om)


def extract_family(inv: Invariant) -> Optional[Family]:
    """The canonical counting family of a non-aperiodic invariant, or None
    when the invariant is aperiodic (the language is LTL-definable). The
    linear shape is preferred: the first separating linear context, else the
    first separating ω-power context (the historical scan order)."""
    g: Optional[Orbit] = first_group(inv)
    if g is None:
        return None
    lin = _scan_linear(inv, g)
    if lin is not None:
        return lin
    om = _scan_omega(inv, g)
    if om is not None:
        return om
    raise AssertionError(
        "separation scan exhausted on a non-aperiodic invariant "
        "(malformed tables: the syntactic congruence must separate "
        "distinct cycle classes)")
