"""EnumLeaf: an explicit finite carrier, coded by frozensets of its values.

Tier B trivially, though the kernel only ever exercises E, J and G. Its
purpose is to isolate kernel bugs from leaf bugs: everything it does is
obviously correct, so a failure is the kernel's.

Every method is call-counted; the counters are the invoice against which
cost claims are checked.
"""

from __future__ import annotations

from typing import Any, Dict, FrozenSet, Iterable, Tuple

from ..core.leaf import Leaf

Code = FrozenSet[Any]

COUNTERS: Dict[str, int] = {}


def _tick(name: str) -> None:
    COUNTERS[name] = COUNTERS.get(name, 0) + 1


def bill() -> Dict[str, int]:
    """Leaf-call counters since the last reset."""
    return dict(COUNTERS)


def reset_bill() -> None:
    COUNTERS.clear()


class EnumLeaf(Leaf):
    tier = "B"

    def __init__(self, name: str, values: Iterable[Any]) -> None:
        self.name = name
        self.values: Tuple[Any, ...] = tuple(values)
        self._top: Code = frozenset(self.values)

    # ---- tier E
    def empty(self) -> Code:
        return frozenset()

    def is_empty(self, a: Code) -> bool:
        _tick(f"{self.name}.is_empty")
        return not a

    # ---- tier J
    def join(self, a: Code, b: Code) -> Code:
        _tick(f"{self.name}.join")
        return a | b

    # ---- tier G
    def meet(self, a: Code, b: Code) -> Code:
        _tick(f"{self.name}.meet")
        return a & b

    def diff(self, a: Code, b: Code) -> Code:
        _tick(f"{self.name}.diff")
        return a - b

    # ---- tier B
    def top(self) -> Code:
        _tick(f"{self.name}.top")
        return self._top

    def complement(self, a: Code) -> Code:
        _tick(f"{self.name}.complement")
        return self._top - a

    # ---- shadow
    def elements(self, a: Code) -> Iterable[Any]:
        return sorted(a, key=repr)

    def code(self, *values: Any) -> Code:
        unknown = [v for v in values if v not in self._top]
        if unknown:
            raise ValueError(f"{self.name}: not carrier values: {unknown}")
        return frozenset(values)
