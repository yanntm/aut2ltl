"""Observation-table columns: the contexts that tell words apart.

A column is a fixed context into which a candidate word ``p`` is dropped, giving
one membership bit. There are two shapes, one per way a finite word sits inside
a lasso:

  - `LinCol` ``(x, y, t)`` — the *linear* context: the bit of ``p`` is whether
    ``x.p.y.t^omega`` is in L, i.e. ``member(Lasso(x + p + y, t))`` (``t`` is the
    non-empty loop, ``p`` sits in the finite prefix);
  - `OmCol` ``(x, y)`` — the *omega* context: the bit of ``p`` is whether
    ``x.(p.y)^omega`` is in L, i.e. ``member(Lasso(x, p + y))`` (``p`` sits in the
    period).

Omega columns are never evaluated on the empty word (it would give an empty
loop); the empty word is a permanent singleton class and skips them.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Union

from sosl.objects.alphabet import Word
from sosl.objects.lasso import Lasso

# The learner's one query primitive: decide a lasso.
Member = Callable[[Lasso], bool]


@dataclass(frozen=True)
class LinCol:
    """A linear context ``x.[]. y.t^omega`` with non-empty loop ``t``."""

    x: Word
    y: Word
    t: Word

    def lasso(self, p: Word) -> Lasso:
        """The lasso whose membership is this column's bit for ``p``."""
        return Lasso(self.x + p + self.y, self.t)


@dataclass(frozen=True)
class OmCol:
    """An omega context ``x.([].y)^omega`` — ``p`` rides in the period."""

    x: Word
    y: Word

    def lasso(self, p: Word) -> Lasso:
        """The lasso whose membership is this column's bit for ``p`` (``p`` must
        be non-empty, so ``p.y`` is a valid loop)."""
        return Lasso(self.x, p + self.y)


Column = Union[LinCol, OmCol]


def is_omega(col: Column) -> bool:
    """Whether ``col`` is an omega column (skipped for the empty word)."""
    return isinstance(col, OmCol)


def query(col: Column, member: Member, p: Word) -> bool:
    """The bit of word ``p`` under ``col``, via the teacher's ``member``."""
    return member(col.lasso(p))
