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


def extract_family(inv: Invariant) -> Optional[Family]:
    """The canonical counting family of a non-aperiodic invariant, or None
    when the invariant is aperiodic (the language is LTL-definable)."""
    g: Optional[Orbit] = first_group(inv)
    if g is None:
        return None
    m, p = g.index, g.period
    cycle: Tuple[int, ...] = g.cycle
    v = inv.keys[g.cls]

    # Linear contexts (x, y, t), shortlex order: phase i ↦ Val(x·gᵐ⁺ⁱ·y, t).
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

    # ω-power contexts (x, y), shortlex order: phase i ↦ Val(x, gᵐ⁺ⁱ·y).
    for x in range(inv.n):
        for y in range(inv.n):
            pat = tuple(
                val(inv, x, inv.mult[cycle[i]][y]) for i in range(p))
            if len(set(pat)) > 1:
                pp = _min_cyclic_period(pat)
                return Family(
                    period=pp, pattern=pat[:pp],
                    u=inv.keys[x], v=v, y=v * m + inv.keys[y])

    raise AssertionError(
        "separation scan exhausted on a non-aperiodic invariant "
        "(malformed tables: the syntactic congruence must separate "
        "distinct cycle classes)")
