"""Local homomorphisms: filters and parallel constant assigns.

Both address frontier positions and recurse down the spine to reach them.
At a cut, a path starting 0 transforms the *primes* — which are diagrams
over the head, so the recursion is the same function one level in — and a
path starting 1 transforms the *subs*.

No cylinder is ever built. A filter is not materialised as data over the
whole shape, which is why no top is needed anywhere: the two faces of a
support are kept apart on purpose, and the bridge between them is exactly
the tier-B purchase this kernel declines to make.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .algebra import normalize
from .diagram import Diagram, Node, Rect
from .hom import Hom
from .shape import LeafShape, Pair, Path, Shape


def _restrict(shape: Shape, d: Diagram, path: Path, code: Any) -> Diagram:
    """Meet the leaf at `path` with `code`, leaving every other position alone."""
    if d is None:
        return None
    if not path:
        assert isinstance(shape, LeafShape)
        r = shape.leaf.meet(d, code)
        return None if shape.leaf.is_empty(r) else r
    assert isinstance(shape, Pair) and isinstance(d, Node)
    rects: List[Rect] = []
    if path[0] == 0:
        for p, s in d.pairs:
            q = _restrict(shape.head, p, path[1:], code)
            if q is not None:
                rects.append((q, s))
    else:
        for p, s in d.pairs:
            t = _restrict(shape.tail, s, path[1:], code)
            if t is not None:
                rects.append((p, t))
    return normalize(shape, rects)


def _write(shape: Shape, d: Diagram, path: Path, code: Any) -> Diagram:
    """Overwrite the leaf at `path` with the constant `code`.

    Memory-destructive: previously distinct primes may collide, and the
    collision is precisely what re-normalisation merges."""
    if d is None:
        return None
    if not path:
        assert isinstance(shape, LeafShape)
        return None if shape.leaf.is_empty(code) else code
    assert isinstance(shape, Pair) and isinstance(d, Node)
    rects: List[Rect] = []
    if path[0] == 0:
        for p, s in d.pairs:
            q = _write(shape.head, p, path[1:], code)
            if q is not None:
                rects.append((q, s))
    else:
        for p, s in d.pairs:
            t = _write(shape.tail, s, path[1:], code)
            if t is not None:
                rects.append((p, t))
    return normalize(shape, rects)


@dataclass(frozen=True)
class Filter(Hom):
    """Keep the words whose coordinate at `path` lies in `code`.

    A guard over one variable. Guards over several variables are written as
    a composition of these, one per variable; that is cheaper than their
    meet, which would have to travel."""

    path: Path
    code: Any

    def _apply(self, shape: Shape, d: Diagram) -> Diagram:
        return _restrict(shape, d, self.path, self.code)


@dataclass(frozen=True)
class Assign(Hom):
    """Parallel assign: write constants at several positions simultaneously.

    The vector form is the primitive; sequential writes cannot express a
    simultaneous exchange without temporaries. With constant right-hand
    sides the writes commute, so the order of `writes` is immaterial."""

    writes: Tuple[Tuple[Path, Any], ...]

    def _apply(self, shape: Shape, d: Diagram) -> Diagram:
        out = d
        for path, code in self.writes:
            out = _write(shape, out, path, code)
            if out is None:
                return None
        return out
