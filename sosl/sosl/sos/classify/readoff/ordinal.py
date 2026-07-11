"""Ordinals below ``omega^omega`` in Cantor normal form.

The Wagner degree ``gamma`` is an ordinal ``< omega^omega`` [CP99 section 3]:
a finite descending sum of terms ``omega^e * c`` with natural exponent ``e`` and
positive natural coefficient ``c``. Represented as the tuple of ``(e, c)`` terms
in strictly descending exponent order (empty tuple = ordinal ``0``). Addition is
Cantor-normal-form ordinal addition — used by the degree recursion when ``gamma``
sums ``mu`` with the derivative's degree. Rendering follows the companion's
notation, spaceless so a rendered ordinal is one `.cat` field token
(``"omega^2*3"``, ``"omega*2+1"``, plain ``"1"``).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Ordinal:
    """An ordinal ``< omega^omega`` as descending ``(exponent, coefficient)``
    terms; ``coefficient > 0`` and exponents strictly decrease."""

    terms: Tuple[Tuple[int, int], ...]

    @classmethod
    def zero(cls) -> "Ordinal":
        return cls(())

    @classmethod
    def finite(cls, k: int) -> "Ordinal":
        """The finite ordinal ``k`` (``= omega^0 * k`` for ``k > 0``)."""
        if k < 0:
            raise ValueError("ordinal cannot be negative")
        return cls(((0, k),) if k > 0 else ())

    @classmethod
    def term(cls, exponent: int, coefficient: int) -> "Ordinal":
        """The single term ``omega^exponent * coefficient``."""
        if coefficient <= 0:
            return cls.zero()
        return cls(((exponent, coefficient),))

    def __add__(self, other: "Ordinal") -> "Ordinal":
        """Ordinal (left-to-right) addition in Cantor normal form: terms of
        ``self`` with exponent strictly greater than ``other``'s leading exponent
        survive, the equal-leading exponent (if any) has coefficients added, and
        the rest of ``other`` follows."""
        if not other.terms:
            return self
        lead_exp = other.terms[0][0]
        kept = [(e, c) for (e, c) in self.terms if e > lead_exp]
        merged = list(other.terms)
        for e, c in self.terms:
            if e == lead_exp:
                merged[0] = (e, c + merged[0][1])
        return Ordinal(tuple(kept) + tuple(merged))

    def __str__(self) -> str:
        if not self.terms:
            return "0"
        parts = []
        for e, c in self.terms:
            if e == 0:
                parts.append(str(c))
            elif e == 1:
                parts.append("omega" if c == 1 else f"omega*{c}")
            else:
                parts.append(f"omega^{e}" if c == 1 else f"omega^{e}*{c}")
        return "+".join(parts)
