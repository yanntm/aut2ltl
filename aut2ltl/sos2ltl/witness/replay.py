"""The toggle check — validate a counting family by membership queries.

The verification contract of a certificate (`algorithm.md`): `2·period + 1`
sample lassos, `n = 0 … 2·period`, each queried against a membership oracle
and compared to the declared pattern. The oracle is any `Lasso → bool` —
the invariant's own read-off for a self-check, or an independent acceptor
of the language for a trust-nothing replay.
"""
from __future__ import annotations

from typing import Callable

from sosl.sos import Lasso

from .family import Family


def toggles(family: Family, member: Callable[[Lasso], bool]) -> bool:
    """Whether the family validates against `member`: the declared pattern
    is non-constant and every sample on the window `n = 0 … 2·period`
    agrees with it."""
    if len(set(family.pattern)) < 2:
        return False
    return all(
        member(family.sample(n)) == family.expected(n)
        for n in range(2 * family.period + 1))
