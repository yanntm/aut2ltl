"""Modelling sugar: declare named leaves, build a shape, address it by name.

Nothing here is part of the calculus. Positions are paths; names are a
decoration, consulted by exactly the constructs that address positions.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

from .core.algebra import count, join, size
from .core.combinators import ID, compose, star, sum_of
from .core.diagram import Diagram, Node
from .core.hom import Hom
from .core.local import Assign, Filter
from .core.shape import LeafShape, Pair, Path, Shape, leaf_shape, pair, paths_of
from .leaves.enum import EnumLeaf

Spec = Union[str, Tuple["Spec", "Spec"], List["Spec"]]


class Model:
    """A shape plus its name table plus the leaf modules behind it."""

    def __init__(self, spec: Spec, leaves: Dict[str, EnumLeaf]) -> None:
        self.leaves = leaves
        self.shape: Shape = self._build(spec)
        self.paths: Dict[str, Path] = paths_of(self.shape)

    def _build(self, spec: Spec) -> Shape:
        if isinstance(spec, str):
            return leaf_shape(spec, self.leaves[spec])
        head, tail = spec
        return pair(self._build(head), self._build(tail))

    # ---- data ---------------------------------------------------------
    def word(self, **values: Any) -> Diagram:
        """The singleton diagram at the given assignment of every leaf."""
        return self.cube(**{k: (v,) for k, v in values.items()})

    def cube(self, **sets: Any) -> Diagram:
        """A rectangle: independently, each named leaf ranges over its set."""
        missing = set(self.paths) - set(sets)
        if missing:
            raise ValueError(f"cube needs every leaf; missing {sorted(missing)}")
        return self._cube(self.shape, sets)

    def _cube(self, shape: Shape, sets: Dict[str, Any]) -> Diagram:
        if isinstance(shape, LeafShape):
            code = frozenset(sets[shape.name])
            return None if not code else code
        assert isinstance(shape, Pair)
        h = self._cube(shape.head, sets)
        t = self._cube(shape.tail, sets)
        if h is None or t is None:
            return None
        from .core.diagram import mk

        return mk(shape, ((h, t),))

    # ---- homs ---------------------------------------------------------
    def keep(self, name: str, *values: Any) -> Hom:
        """`filter(name in values)` — a guard over one variable."""
        return Filter(self.paths[name], self.leaves[name].code(*values))

    def set(self, **writes: Any) -> Hom:
        """Parallel constant assign: `assign(x := v, y := w)` simultaneously."""
        return Assign(
            tuple(
                (self.paths[n], self.leaves[n].code(v)) for n, v in sorted(writes.items())
            )
        )

    def apply(self, h: Hom, d: Diagram) -> Diagram:
        return h(self.shape, d)

    # ---- measurement --------------------------------------------------
    def size(self, d: Diagram) -> Dict[int, int]:
        return size(self.shape, d)

    def count(self, d: Diagram) -> int:
        return count(self.shape, d)

    def words(self, d: Diagram) -> List[Dict[str, Any]]:
        """Brute-force expansion. The extensional shadow, for small carriers."""
        return [dict(w) for w in self._words(self.shape, d)]

    def _words(self, shape: Shape, d: Diagram) -> Iterable[Tuple[Tuple[str, Any], ...]]:
        if d is None:
            return
        if isinstance(shape, LeafShape):
            for v in shape.leaf.elements(d):
                yield ((shape.name, v),)
            return
        assert isinstance(shape, Pair) and isinstance(d, Node)
        for p, s in d.pairs:
            for wh in self._words(shape.head, p):
                for wt in self._words(shape.tail, s):
                    yield wh + wt

    def root_primes(self, d: Diagram) -> int:
        """Section rank at the top cut: the number of primes there."""
        return 0 if d is None else len(d.pairs)


def enum(name: str, *values: Any) -> EnumLeaf:
    return EnumLeaf(name, values)
