"""Homomorphisms: terms with a code action.

A hom is a frozen, hashable Python object with an `_apply(shape, diagram)`.
Application is cached on `(hom, shape.uid, diagram uid)` — the (term, data)
cache. Terms themselves are *not* canonicalised: the behaviour-layer normal
form is an open obligation of the calculus document, and nothing here needs
it, since only applications are shared.

Every `_apply` rebuilds bottom-up through `normalize`, so canonicity is
restored after each action rather than assumed to be preserved by it.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

from .diagram import Diagram, duid
from .shape import Shape

_APPLY: Dict[Tuple[int, int, int], Diagram] = {}


def clear_cache() -> None:
    _APPLY.clear()


class Hom:
    """Base class. Subclasses are frozen dataclasses implementing `_apply`."""

    def __call__(self, shape: Shape, d: Diagram) -> Diagram:
        if d is None:
            return None  # composition is 0-strict
        key = (id(type(self)) ^ hash(self), shape.uid, duid(shape, d))
        got = _APPLY.get(key)
        if got is not None or key in _APPLY:
            return got
        out = self._apply(shape, d)
        _APPLY[key] = out
        return out

    def _apply(self, shape: Shape, d: Diagram) -> Diagram:
        raise NotImplementedError

    def __mul__(self, other: "Hom") -> "Hom":
        """`f * g` is composition: g first, then f — the document's `f o g`."""
        from .combinators import compose

        return compose(self, other)

    def __add__(self, other: "Hom") -> "Hom":
        from .combinators import sum_of

        return sum_of(self, other)
