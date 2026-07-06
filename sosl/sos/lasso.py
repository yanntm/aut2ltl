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
