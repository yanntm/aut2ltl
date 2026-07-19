"""The evidence: every teacher bit witnessed so far, keyed by the omega-word.

The learner's ground truth. One bit per queried lasso, however the query
arose — a table fill, a chain step, a P-slot, a counterexample — memoized by
the canonical form of the denoted infinite word (`Lasso.canonical`), so two
presentations of one word cost one query and can never disagree. Everything
else the learner holds is derived from this set; in particular the belief can
be replayed against it, query-free, and a contradiction is a discordant lasso
whose teacher bit is already in hand.

``n_member`` counts actual teacher queries — cache misses; rereading evidence
is free.
"""
from __future__ import annotations

from typing import Callable, Dict, Iterator, Tuple

from sosl.sos.lasso import Lasso

Member = Callable[[Lasso], bool]


class Evidence:
    """The run-wide lasso -> bit ledger, filled through one teacher callable."""

    def __init__(self, member: Member) -> None:
        self._member = member
        self._bits: Dict[Lasso, bool] = {}
        self.n_member = 0

    def bit(self, lasso: Lasso) -> bool:
        """The teacher's bit on ``lasso``: replayed from the ledger when the
        denoted word has been queried before (under any presentation), else
        one counted teacher query on the canonical form."""
        key = lasso.canonical()
        cached = self._bits.get(key)
        if cached is None:
            self.n_member += 1
            cached = self._member(key)
            self._bits[key] = cached
        return cached

    def items(self) -> Iterator[Tuple[Lasso, bool]]:
        """The witnessed bits, canonical lasso each, in first-query order —
        deterministic for a run, so replay scans are reproducible."""
        return iter(self._bits.items())

    def __len__(self) -> int:
        return len(self._bits)
