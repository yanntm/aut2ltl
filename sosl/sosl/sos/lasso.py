"""Lassos: the ultimately-periodic words that are the only words this tool
exchanges.

``Lasso(stem, loop)`` denotes the infinite word ``stem . loop^omega`` — the
stem read once, then the (non-empty) loop repeated forever. Two omega-regular
languages are equal iff they agree on all lassos, so a lasso is the unit of
every membership and equivalence query.
"""
from __future__ import annotations

from dataclasses import dataclass

from .alphabet import Word


@dataclass(frozen=True)
class Lasso:
    """The word ``stem . loop^omega``; ``loop`` must be non-empty."""

    stem: Word
    loop: Word

    def __post_init__(self) -> None:
        if not self.loop:
            raise ValueError("a lasso loop must be non-empty")

    def raised_to(self, k: int) -> "Lasso":
        """The same infinite word rewritten with the loop at power ``k``:
        ``(u, v) -> (u . v^k, v^k)``. This is the counterexample-normalization
        move that aligns the loop to a stabilization power; it denotes the same
        word (``k >= 1``)."""
        if k < 1:
            raise ValueError("loop power must be >= 1")
        vk = self.loop * k
        return Lasso(self.stem + vk, vk)

    def canonical(self) -> "Lasso":
        """The unique normal form of the denoted infinite word: the loop
        reduced to its primitive root, then the stem shortened while its last
        letter matches the loop's last (``u.a . (x.a)^omega = u . (a.x)^omega``
        — the letter carried around the wrap). Minimal stem plus primitive
        loop pin the presentation completely, so two lassos denote the same
        infinite word iff their canonical forms are equal — the key of any
        by-word memoization."""
        v = self.loop
        m = len(v)
        for d in range(1, m):
            if m % d == 0 and v[:d] * (m // d) == v:
                v = v[:d]
                break
        u = self.stem
        while u and u[-1] == v[-1]:
            v = (u[-1],) + v[:-1]
            u = u[:-1]
        return Lasso(u, v)
