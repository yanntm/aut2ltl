"""Input digests passed across the binding: a Büchi automaton as a guarded
transition relation with mark sets, and the structured product form for
composed families. Plain data on purpose — no diagram types, no parsing
beyond guard cubes; the C++ core receives these as-is."""

from dataclasses import dataclass
from typing import FrozenSet, Iterable, Literal, Tuple, Union


@dataclass(frozen=True)
class Transition:
    """One guarded edge: `cube` is a conjunction of AP literals ("a&!b",
    or "1" for true); a guard spanning several cubes is several entries.
    `marks` are acceptance-mark indices carried by the edge."""

    src: int
    cube: str
    dst: int
    marks: FrozenSet[int] = frozenset()


TransLike = Union[Transition, Tuple[int, str, int, Iterable[int]]]


@dataclass(frozen=True)
class Automaton:
    """A digested automaton: states are `0..states-1`, marks are
    `0..marks-1`, `acceptance` is an HOA acceptance formula over the mark
    indices (kept as text — the core interprets it). `ap` order is
    significant: the letter α ranges over valuations of exactly these
    APs and is carried symbolically, never enumerated."""

    name: str
    ap: Tuple[str, ...]
    states: int
    init: int
    marks: int
    acceptance: str
    trans: Tuple[Transition, ...]

    def __post_init__(self) -> None:
        coerced: Tuple[Transition, ...] = tuple(
            t if isinstance(t, Transition) else Transition(t[0], t[1], t[2], frozenset(t[3]))
            for t in self.trans
        )
        object.__setattr__(self, "trans", coerced)
        object.__setattr__(self, "ap", tuple(self.ap))

    def validate(self) -> None:
        """Index-range and cube-syntax checks; raises ValueError. Cheap —
        callers run it once per build, not per operation."""
        if not (0 <= self.init < self.states):
            raise ValueError(f"{self.name}: init {self.init} out of range")
        names = set(self.ap)
        if len(names) != len(self.ap):
            raise ValueError(f"{self.name}: duplicate AP names")
        for t in self.trans:
            if not (0 <= t.src < self.states and 0 <= t.dst < self.states):
                raise ValueError(f"{self.name}: transition {t} state out of range")
            if bad := {m for m in t.marks if not (0 <= m < self.marks)}:
                raise ValueError(f"{self.name}: transition {t} marks {bad} out of range")
            if t.cube != "1":
                for lit in t.cube.split("&"):
                    if lit.lstrip("!") not in names:
                        raise ValueError(f"{self.name}: unknown AP in cube {t.cube!r}")


@dataclass(frozen=True)
class Product:
    """A composed family instance, kept structured — the global automaton
    is never expanded on this side of the binding (its flat form is an
    engine-side encoding choice). `async_`: disjoint AP and mark
    namespaces, global acceptance the conjunction of the components'.
    `sync`: APs shared by name."""

    name: str
    components: Tuple[Automaton, ...]
    mode: Literal["async", "sync"]

    def __post_init__(self) -> None:
        object.__setattr__(self, "components", tuple(self.components))

    def validate(self) -> None:
        if self.mode not in ("async", "sync"):
            raise ValueError(f"{self.name}: unknown mode {self.mode!r}")
        if not self.components:
            raise ValueError(f"{self.name}: empty product")
        for c in self.components:
            c.validate()
        if self.mode == "async":
            seen: set = set()
            for c in self.components:
                if overlap := seen & set(c.ap):
                    raise ValueError(f"{self.name}: async product shares APs {overlap}")
                seen |= set(c.ap)


Input = Union[Automaton, Product]
