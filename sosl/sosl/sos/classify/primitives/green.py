"""Green's preorders on the word classes of an `Invariant`.

The right (resp. left) principal ideal of a class ``t`` is ``t.S1`` (resp.
``S1.t``), with ``S1`` the semigroup plus an external unit — realised here by
the identity class, a two-sided unit of the table. One level of multiplication
suffices: ``t.S = {mult[t][x]}`` is already right-ideal-closed (``S.S <= S``),
and ``t.S1 = {t} union t.S`` is covered by letting ``x`` range over every
class including the identity. From the ideals come the preorders

    s <=_R t  <=>  s in t.S1        (s in the right ideal of t)
    s <=_L t  <=>  s in S1.t        (s in the left ideal of t)
    s <=_H t  <=>  s <=_R t and s <=_L t

their strict parts, their induced equivalences, and the R-class partition the
superchain search descends. Normative math: `research_notes/sos_classification.md`
section 2.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Tuple

from ...invariant import Invariant


@dataclass(frozen=True)
class Green:
    """Precomputed right/left principal ideals of every class of an invariant,
    exposing the R/L/H preorders as membership tests. ``rideal[t]`` is ``t.S1``
    and ``lideal[t]`` is ``S1.t`` (the identity class supplies the external
    unit, so both contain ``t``)."""

    n: int
    identity: int
    rideal: Tuple[FrozenSet[int], ...]
    lideal: Tuple[FrozenSet[int], ...]

    @classmethod
    def of(cls, inv: Invariant) -> "Green":
        n = inv.n
        mult = inv.mult
        rideal: List[FrozenSet[int]] = []
        lideal: List[FrozenSet[int]] = []
        for t in range(n):
            rideal.append(frozenset(mult[t][x] for x in range(n)))
            lideal.append(frozenset(mult[x][t] for x in range(n)))
        return cls(n=n, identity=inv.identity,
                   rideal=tuple(rideal), lideal=tuple(lideal))

    def leq_r(self, s: int, t: int) -> bool:
        """``s <=_R t``: ``s`` lies in the right ideal of ``t``."""
        return s in self.rideal[t]

    def leq_l(self, s: int, t: int) -> bool:
        """``s <=_L t``: ``s`` lies in the left ideal of ``t``."""
        return s in self.lideal[t]

    def leq_h(self, s: int, t: int) -> bool:
        """``s <=_H t``: ``s <=_R t`` and ``s <=_L t``."""
        return self.leq_r(s, t) and self.leq_l(s, t)

    def lt_r(self, s: int, t: int) -> bool:
        """Strict ``s <_R t``: ``s <=_R t`` and not ``t <=_R s``."""
        return self.leq_r(s, t) and not self.leq_r(t, s)

    def lt_h(self, s: int, t: int) -> bool:
        """Strict ``s <_H t``: ``s <=_H t`` and not ``t <=_H s``."""
        return self.leq_h(s, t) and not self.leq_h(t, s)

    def eq_r(self, s: int, t: int) -> bool:
        """R-equivalence: ``s <=_R t`` and ``t <=_R s``."""
        return self.leq_r(s, t) and self.leq_r(t, s)

    def r_classes(self, elems: Tuple[int, ...]) -> Tuple[Tuple[int, ...], ...]:
        """Partition ``elems`` into R-classes, each class returned sorted by id
        and the classes ordered by their least id. ``elems`` is any subset of
        the word classes (the identity is normally excluded by the caller)."""
        rep: Dict[int, List[int]] = {}
        for c in sorted(elems):
            for r, members in rep.items():
                if self.eq_r(c, r):
                    members.append(c)
                    break
            else:
                rep[c] = [c]
        return tuple(tuple(m) for m in rep.values())
