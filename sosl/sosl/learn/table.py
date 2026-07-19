"""The observation table: the learner's record of what it has asked the teacher.

Storage and querying only — the congruence view (classes, representatives,
step) is derived separately in `sosl.learn.partition`.

  - ``rows`` — the access words: ``eps`` and words promoted by closing (the
    shortlex-least letter is the first promotion — with no columns every
    letter shares the one non-identity class, which has no row);
    ``row_set`` is their membership set.
  - the *frontier* is ``rows . Sigma``; ``domain()`` is ``rows`` followed by the
    frontier (de-duplicated) — every word the table observes.
  - ``columns`` — the distinguishing contexts (`sosl.learn.columns`). The
    table opens with **no columns at all**: every column of every run is
    minted by a discordance; no experiment is given, all are found.
  - ``entry[(word, col_index)]`` — the cached membership bit, filled lazily by
    `fill`. The empty word is classified like any other: on an omega column
    whose loop would be empty (only ``eps`` on a ``([], [])``-shaped column) the
    bit is ``False`` — there is no such omega word — so ``eps`` merges with any
    word congruent to it rather than being forced into its own class.

**The letter collapse.** Letters sharing a full signature are speculatively
interchangeable: `fill` queries real bits only for rows, single letters, and
frontier extensions by each letter class's least member (its *rep*); a
non-rep cell carries its rep-cousin's bit as a **proxy**, marked in
``proxy``, unless the evidence ledger already holds the cell's own lasso —
evidence always wins. Proxies are bookkeeping, not knowledge: they are
recomputed from scratch on every `fill` pass (the collapse may refine), they
never witness a structural event (see `Partition` and `verify`), and a word
is `verify`-grounded — every proxied bit replaced by a real query — before it
may be promoted to a row, so rows only ever carry real bits.

Every membership query passes through the `Evidence` ledger
(`sosl.learn.evidence`): one teacher query per distinct infinite word across
the whole run, every later presentation a free replay. ``n_member`` counts the
actual teacher queries.
"""
from __future__ import annotations

from typing import Dict, List, Set, Tuple

from sosl.learn.columns import Column, Member, is_omega, query
from sosl.learn.evidence import Evidence
from sosl.sos.alphabet import EMPTY, Alphabet, Letter, Word
from sosl.sos.lasso import Lasso


class Table:
    """The mutable observation table over one alphabet and one teacher."""

    def __init__(self, alphabet: Alphabet, member: Member) -> None:
        self.alphabet = alphabet
        self.evidence = Evidence(member)
        self.rows: List[Word] = [EMPTY]
        self.row_set = set(self.rows)
        self.columns: List[Column] = []
        self.entry: Dict[Tuple[Word, int], bool] = {}
        # Cells whose bit is a proxy of the rep-cousin's, not the word's own.
        self.proxy: Set[Tuple[Word, int]] = set()

    @property
    def n_member(self) -> int:
        """Teacher queries posed so far (evidence cache misses)."""
        return self.evidence.n_member

    def _q(self, col: Column, w: Word) -> bool:
        return query(col, self.evidence.bit, w)

    def query_lasso(self, lasso: Lasso) -> bool:
        """A direct membership query through the evidence ledger (used by the
        chains and the P fill, which query lassos the column machinery does
        not shape)."""
        return self.evidence.bit(lasso)

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

    def letter_reps(self) -> Dict[Letter, Letter]:
        """The current letter collapse: each letter mapped to the least letter
        sharing its full signature (letters must be filled). Letters carry
        real bits only, so the collapse is always evidence-grounded."""
        first: Dict[Tuple[bool, ...], Letter] = {}
        rep_of: Dict[Letter, Letter] = {}
        for a in self.alphabet.letters():
            rep_of[a] = first.setdefault(self.bit_row((a,)), a)
        return rep_of

    def _fill_word(self, w: Word) -> None:
        """Query every missing bit of ``w`` — real bits. On an omega column
        whose loop ``w + col.y`` is empty the bit is ``False`` (no such omega
        word), so the empty word is filled like any other."""
        for i, col in enumerate(self.columns):
            key = (w, i)
            if key in self.entry:
                continue
            if is_omega(col) and not (w + col.y):
                self.entry[key] = False
            else:
                self.entry[key] = self._q(col, w)

    def fill(self) -> None:
        """Fill every ``(word, column)`` cell — real queries for rows, letters
        and rep-letter extensions; proxies for the rest (module doc). Proxies
        are dropped and re-derived on every pass: both the collapse and the
        cousin's bits may have moved since they were copied."""
        for key in self.proxy:
            del self.entry[key]
        self.proxy.clear()
        dom = self.domain()
        grounded = [w for w in dom if w in self.row_set or len(w) == 1]
        for w in grounded:
            self._fill_word(w)
        rep_of = self.letter_reps()
        speculative: List[Word] = []
        for w in dom:
            if w in self.row_set or len(w) == 1:
                continue
            if rep_of[w[-1]] == w[-1]:
                self._fill_word(w)
            else:
                speculative.append(w)
        for w in speculative:
            cousin = w[:-1] + (rep_of[w[-1]],)
            for i, col in enumerate(self.columns):
                key = (w, i)
                if key in self.entry:
                    continue
                bit = self.evidence.peek(col.lasso(w))
                if bit is None:
                    bit = self.entry[(cousin, i)]
                    self.proxy.add(key)
                self.entry[key] = bit

    def verify(self, w: Word) -> bool:
        """Ground ``w``: replace every proxied bit by a real query; return
        whether any bit changed. Ran on any word about to be promoted, so rows
        never carry proxies."""
        changed = False
        for i, col in enumerate(self.columns):
            key = (w, i)
            if key not in self.proxy:
                continue
            self.proxy.discard(key)
            real = self._q(col, w)
            if self.entry[key] != real:
                self.entry[key] = real
                changed = True
        return changed

    def bit_row(self, w: Word) -> Tuple[bool, ...]:
        """The full column signature of word ``w`` (must be filled)."""
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
