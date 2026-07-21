"""`split_equiv`: the partition primitive, and `theta` on top of it.

    split_equiv(shape, d, expr) -> {residual expression : piece of d}

Partition `d` into the pieces on which `expr` has each realised residual.
Zero pieces are absent, so the key set *is* the discovered alphabet: empty
classes are never represented, and pieces that agree are merged before any
client sees them. When a key is ground, that residual is a discovered
letter; when it is not, the caller is looking at a cut the expression has
not finished crossing.

The traversal is the curried residual transport. The invariant it maintains:
the travelling classifier is ground and mentions only coordinates not yet
consumed, because meeting a coordinate substitutes its value and
renormalises. Consequently a consumed coordinate can never be re-queried.

Three structural properties fall out of the code rather than being arranged:

- **locality is free.** If `expr` mentions nothing in the head, the head
  split returns the expression unchanged in one entry and no work is done
  there; a classifier supported in one subtree costs nothing outside it.
- **deduplication is cache sharing.** Expressions are interned, so grouping
  head-classes by residual code and keying the memo table on that code are
  the same act; every context whose classifier curries to the same code
  hits the same entry.
- **the equivariant collapse is not a code path.** Where residuals differ
  but the induced partitions agree, they meet again in the returned map,
  merged by the same (F)-compression that merges anything else.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .algebra import normalize
from .diagram import Diagram, Node, Rect, duid
from .expr import Expr
from .shape import LeafShape, Pair, Shape
from .stats import tick

_SPLIT: Dict[Tuple[int, int, int], Dict[Expr, Diagram]] = {}


def clear_cache() -> None:
    _SPLIT.clear()


def split_equiv(shape: Shape, d: Diagram, expr: Expr) -> Dict[Expr, Diagram]:
    if d is None:
        return {}
    if expr.is_ground():
        return {expr: d}
    if not (expr.vars & _names(shape)):
        return {expr: d}  # distance zero: the classifier does not live here

    tick("node.split_equiv")
    key = (shape.uid, duid(shape, d), expr.uid)
    got = _SPLIT.get(key)
    if got is not None:
        return got

    if isinstance(shape, LeafShape):
        out = shape.leaf.split_equiv(d, expr)
    else:
        assert isinstance(shape, Pair) and isinstance(d, Node)
        rects: Dict[Expr, List[Rect]] = {}
        for p, s in d.pairs:
            for residual, piece in split_equiv(shape.head, p, expr).items():
                for final, tail_piece in split_equiv(shape.tail, s, residual).items():
                    rects.setdefault(final, []).append((piece, tail_piece))
        out = {e: normalize(shape, rs) for e, rs in rects.items()}
        out = {e: v for e, v in out.items() if v is not None}

    _SPLIT[key] = out
    return out


_NAME_CACHE: Dict[int, frozenset] = {}


def _names(shape: Shape) -> frozenset:
    got = _NAME_CACHE.get(shape.uid)
    if got is None:
        got = _NAME_CACHE[shape.uid] = frozenset(lf.name for _, lf in shape.leaves())
    return got


def theta(shape: Shape, d: Diagram, expr: Expr) -> Dict[Any, Diagram]:
    """The quotient constructor: discovered letter -> the part it classifies.

    Every returned class is nonempty, and no two classify the same part, so
    the alphabet is the coarsest refinement compatible with `expr` on `d` —
    minimal and forced, inherited wholesale from the decomposition theorem
    rather than arranged here."""
    parts = split_equiv(shape, d, expr)
    out: Dict[Any, Diagram] = {}
    for residual, piece in parts.items():
        if not residual.is_ground():
            raise ValueError(
                f"classifier mentions coordinates outside the shape: {residual!r}"
            )
        out[residual.value] = piece  # type: ignore[attr-defined]
    return out
