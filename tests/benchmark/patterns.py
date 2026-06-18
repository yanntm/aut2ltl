"""Structured pattern-family generators for the portfolio benchmark.

NOT a gate. These feed `tests/benchmark` with scalable, shaped inputs that the
random generator hits only rarely: nested **weak-until** chains `φ W ψ W …`,
**strong-until** chains, R/M chains, all over non-trivial boolean/temporal arms,
with optional `X`-insertions. Each family is parameterised by chain length, so a
bench can watch output size grow with shape — the point is portfolio A/B
(`default` vs `best`) on size, not soundness.

Run `python3 tests/benchmark/patterns.py` to print every (id, formula) it emits.
"""
from __future__ import annotations

from typing import Iterator, List, Tuple

# Non-trivial arms, cycled through a chain so successive operands differ. Kept to
# APs a..e for readability (canonicalisation, phase 3, will normalise anyway).
_ARMS: List[str] = [
    "a",
    "(a & b)",
    "(b | c)",
    "(a & X b)",
    "F(a & b)",
    "(a U b)",
    "(b R c)",
    "(c & X d)",
    "G(a | b)",
    "(d | X e)",
]


def _arm(i: int) -> str:
    """The i-th arm of a chain (cycles the palette)."""
    return _ARMS[i % len(_ARMS)]


def _rchain(op: str, terms: List[str]) -> str:
    """Right-associated binary-modal chain `t0 op (t1 op (… op tn))`."""
    f = terms[-1]
    for t in reversed(terms[:-1]):
        f = f"({t} {op} {f})"
    return f


def _xlace(terms: List[str]) -> List[str]:
    """Prefix every other arm with X — the requested 'some X thrown in'."""
    return [f"X {t}" if i % 2 else t for i, t in enumerate(terms)]


def chain(op: str, n: int, *, xlace: bool = False) -> str:
    """An n-arm `op`-chain over the arm palette (optionally X-laced)."""
    terms = [_arm(i) for i in range(n)]
    if xlace:
        terms = _xlace(terms)
    return _rchain(op, terms)


def mixed(ops: List[str], n: int) -> str:
    """An n-arm chain cycling through `ops` between successive arms — e.g.
    `["W","U"]` gives `t0 W (t1 U (t2 W …))`."""
    terms = [_arm(i) for i in range(n)]
    f = terms[-1]
    for k in range(n - 2, -1, -1):
        f = f"({terms[k]} {ops[k % len(ops)]} {f})"
    return f


def families(max_len: int = 6) -> Iterator[Tuple[str, str]]:
    """Yield (id, formula) over every pattern family for lengths 2..max_len."""
    for n in range(2, max_len + 1):
        yield (f"wchain{n}", chain("W", n))
        yield (f"uchain{n}", chain("U", n))          # strong until
        yield (f"rchain{n}", chain("R", n))
        yield (f"wchain_x{n}", chain("W", n, xlace=True))
        yield (f"uchain_x{n}", chain("U", n, xlace=True))
        yield (f"wu_mix{n}", mixed(["W", "U"], n))
        yield (f"ur_mix{n}", mixed(["U", "R"], n))


if __name__ == "__main__":
    for pid, f in families():
        print(f"{pid:12s} {f}")
