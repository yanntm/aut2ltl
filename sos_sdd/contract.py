"""Behavioral contract of the symbolic invariant object. The concrete
class lives in the C++ extension; this Protocol is the typed surface
Python callers program against. Words (for membership and witnesses) are
sequences of letter cubes over the input's APs.

Canonicity is explicit: operators never reduce behind the caller's back —
`reduce()` quotients on demand and `to_sos()` forces it, so deferred-reduce
pipelines are a caller's choice visible in their code."""

from typing import List, Optional, Protocol, Sequence, Tuple

Word = Sequence[str]  # one cube string per letter
Lasso = Tuple[Tuple[str, ...], Tuple[str, ...]]  # (stem, loop)


class SoS(Protocol):
    """The invariant 𝓘(L) held symbolically, partial or complete: objects
    built `until_phase < 6` expose the readings of the phases run and
    raise on the rest."""

    # -- readings -----------------------------------------------------
    def em1_count(self) -> int:
        """|EM¹| by model count on the closure (pre-quotient)."""
        ...

    @property
    def depth(self) -> int:
        """Closure depth — the length of the longest shortlex key."""
        ...

    @property
    def layers(self) -> List[Tuple[int, int, int]]:
        """Kept closure layers: (layer, cardinality, nodes) rows."""
        ...

    @property
    def nodes(self) -> Tuple[int, int]:
        """(final, peak) live diagram nodes over the object's history."""
        ...

    def to_sos(self) -> str:
        """The canonical `.sos` text (byte-level reference parity);
        forces `reduce()`."""
        ...

    # -- calculus -----------------------------------------------------
    def member(self, u: Word, v: Word) -> bool:
        """Lasso membership u·v^ω — closure-free by construction."""
        ...

    def reduce(self) -> "SoS":
        """Quotient to canonical form. The only place canonicity is paid."""
        ...

    def included(self, other: "SoS") -> bool: ...

    def equiv(self, other: "SoS") -> bool: ...

    def empty(self) -> bool: ...

    def witness(self, other: "SoS") -> Optional[Lasso]:
        """Least separating lasso in (stem length, loop length, lex) order,
        or None when included in `other`."""
        ...

    # Same-table Boolean algebra; on distinct tables the operation aligns
    # first and that closure is priced in the stats stream.
    def __invert__(self) -> "SoS": ...

    def __and__(self, other: "SoS") -> "SoS": ...

    def __or__(self, other: "SoS") -> "SoS": ...

    def __sub__(self, other: "SoS") -> "SoS": ...

    # Rootings / inverse substitutions (§6.5) join the contract when the
    # calculus milestone lands; their signatures are not pinned here yet.
