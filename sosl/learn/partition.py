"""The congruence view derived from an observation table.

Groups the table's words into classes by their column signature (`Table.bit_row`)
and exposes the semigroup skeleton the learner reasons over:

  - every word joins the class of words with its exact bit-row; the empty word
    is classified like any other, so it merges with a letter congruent to it;
  - ``start`` is the class containing the empty word — the identity and the
    fold start;
  - ``rep[c]`` is the shortlex-least *row* of class ``c`` (``None`` if the class
    holds only frontier words — an *unclosed* class);
  - ``step(c, a)`` is the class of ``rep[c].a`` (defined once closed);
  - ``fold(w)`` is the letterwise ``step`` from the start (the ``psi`` of the
    algorithm notes), which on a closed & consistent table agrees with the
    word's own class.

Also reports the two obstructions the learner must clear: `unclosed` frontier
witnesses and an `inconsistency` witness.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from sosl.learn.table import Table
from sosl.objects.alphabet import EMPTY, Letter, Word, shortlex_key


class Partition:
    """A snapshot of the classes induced by a table's current columns."""

    def __init__(self, table: Table) -> None:
        self.table = table
        self.members: List[List[Word]] = []
        self.class_of: Dict[Word, int] = {}
        groups: Dict[Tuple[bool, ...], int] = {}
        for w in table.domain():
            br = table.bit_row(w)
            idx = groups.get(br)
            if idx is None:
                idx = len(self.members)
                groups[br] = idx
                self.members.append([])
            self.members[idx].append(w)
            self.class_of[w] = idx
        self.start = self.class_of[EMPTY]
        self.rep: List[Optional[Word]] = []
        for idx in range(len(self.members)):
            rows = [w for w in self.members[idx] if w in table.row_set]
            self.rep.append(min(rows, key=shortlex_key) if rows else None)

    @property
    def n(self) -> int:
        """The number of classes."""
        return len(self.members)

    def unclosed(self) -> List[Word]:
        """One shortlex-least frontier witness per class lacking a row (each
        such witness should be promoted to a row to close the table)."""
        out: List[Word] = []
        for idx in range(self.n):
            if self.rep[idx] is None:
                out.append(min(self.members[idx], key=shortlex_key))
        return out

    def is_closed(self) -> bool:
        return not self.unclosed()

    def step(self, c: int, a: Letter) -> int:
        """The class of ``rep[c].a`` (requires ``c`` closed)."""
        r = self.rep[c]
        assert r is not None, "step on an unclosed class"
        return self.class_of[r + (a,)]

    def fold_from(self, c: int, w: Word) -> int:
        """The class reached by folding ``w`` letterwise starting from class
        ``c`` (requires the visited classes closed)."""
        for a in w:
            c = self.step(c, a)
        return c

    def fold(self, w: Word) -> int:
        """The class reached by folding ``w`` letterwise from the start."""
        return self.fold_from(self.start, w)

    def separating_column(self, u: Word, v: Word) -> Optional[int]:
        """A column index where non-empty ``u`` and ``v`` differ, or ``None`` if
        their bit-rows agree."""
        bu, bv = self.table.bit_row(u), self.table.bit_row(v)
        for i in range(len(bu)):
            if bu[i] != bv[i]:
                return i
        return None

    def inconsistency(self) -> Optional[Tuple[Word, Word, Letter, int]]:
        """A witness ``(p, q, a, col)``: rows ``p, q`` share a class but ``p.a``
        and ``q.a`` do not, separated at column index ``col`` — or ``None`` if
        the table is consistent."""
        rows_by_class: Dict[int, List[Word]] = {}
        for w in self.table.rows:
            rows_by_class.setdefault(self.class_of[w], []).append(w)
        for members in rows_by_class.values():
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    p, q = members[i], members[j]
                    for a in self.table.alphabet.letters():
                        cp, cq = self.class_of[p + (a,)], self.class_of[q + (a,)]
                        if cp != cq:
                            col = self.separating_column(p + (a,), q + (a,))
                            assert col is not None
                            return (p, q, a, col)
        return None
