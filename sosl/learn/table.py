"""The observation table: the learner's record of what it has asked the teacher.

Storage and querying only — the congruence view (classes, representatives,
step) is derived separately in `sosl.learn.partition`.

  - ``rows`` — the access words (``eps``, the letters, and words promoted by
    closing); ``row_set`` is their membership set.
  - the *frontier* is ``rows . Sigma``; ``domain()`` is ``rows`` followed by the
    frontier (de-duplicated) — every word the table observes.
  - ``columns`` — the distinguishing contexts (`sosl.learn.columns`); the table
    is seeded with the single omega column ``([], [])`` (the bit of ``p`` is
    whether ``p^omega`` is in L).
  - ``entry[(word, col_index)]`` — the cached membership bit, filled lazily by
    `fill`; the empty word skips omega columns (it is a permanent singleton).

Every membership query passes through `_q`, which counts them (``n_member``).
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from sosl.learn.columns import Column, Member, OmCol, is_omega, query
from sosl.objects.alphabet import EMPTY, Alphabet, Word


class Table:
    """The mutable observation table over one alphabet and one teacher."""

    def __init__(self, alphabet: Alphabet, member: Member) -> None:
        self.alphabet = alphabet
        self._member = member
        self.n_member = 0
        self.rows: List[Word] = [EMPTY] + [(a,) for a in alphabet.letters()]
        self.row_set = set(self.rows)
        self.columns: List[Column] = [OmCol(EMPTY, EMPTY)]
        self.entry: Dict[Tuple[Word, int], bool] = {}

    def _q(self, col: Column, w: Word) -> bool:
        self.n_member += 1
        return query(col, self._member, w)

    def domain(self) -> List[Word]:
        """Rows then frontier (``rows . Sigma``), de-duplicated, in a stable
        order — the words the table classifies."""
        seen = set()
        out: List[Word] = []
        for r in self.rows:
            if r not in seen:
                seen.add(r)
                out.append(r)
        for r in self.rows:
            for a in self.alphabet.letters():
                w = r + (a,)
                if w not in seen:
                    seen.add(w)
                    out.append(w)
        return out

    def fill(self) -> None:
        """Query every missing ``(word, column)`` bit (omega columns skip the
        empty word)."""
        for w in self.domain():
            for i, col in enumerate(self.columns):
                if w == EMPTY and is_omega(col):
                    continue
                key = (w, i)
                if key not in self.entry:
                    self.entry[key] = self._q(col, w)

    def bit_row(self, w: Word) -> Tuple[bool, ...]:
        """The full column signature of a non-empty word ``w`` (must be filled)."""
        assert w != EMPTY, "the empty word has no omega bits; it is a singleton"
        return tuple(self.entry[(w, i)] for i in range(len(self.columns)))

    def add_row(self, w: Word) -> bool:
        """Promote ``w`` to a row; return whether it was new."""
        if w in self.row_set:
            return False
        self.row_set.add(w)
        self.rows.append(w)
        return True

    def add_column(self, col: Column) -> int:
        """Append a distinguishing column; return its index."""
        self.columns.append(col)
        return len(self.columns) - 1
