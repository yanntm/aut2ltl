"""Pair legality: P saturated under conjugacy of linked pairs.

After the stamp sweep runs clean, the table's classes carry a genuine finite
semigroup (the induced product ``mult[c][d] = fold_from(c, rep(d))``). Its
acceptance layer ``P`` is a cache of teacher truths — one bit per linked pair
``(s, e)``, on the keyed lasso ``rep(s).rep(e)^omega`` — and well-formedness
demands ``P`` constant across the conjugacy steps

    (s, (c.d)^pi)  ~  (s.c, (d.c)^pi)

one omega-word, two names, one verdict. The scan costs no queries beyond the
``P`` entries themselves (each memoized in the evidence ledger, so re-scans
are free). A violation is refereed on the common rotated lasso — ONE
membership query, and the two presentations ``rep(s).(rep(c).rep(d))^omega``
and ``(rep(s).rep(c)).(rep(d).rep(c))^omega`` share their canonical form, so
the referee bit is fetched once — and the presentation naming the losing pair
is a discordant lasso for the ordinary chain (`process_counterexample`).

Scan order (normative, for reproducible traces): ``s``, then ``c``, then ``d``
in class-id order; the first violating triple fires.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from sosl.learn.partition import Partition
from sosl.learn.table import Table
from sosl.sos.lasso import Lasso

Mult = List[List[int]]


def induced_mult(p: Partition) -> Mult:
    """The induced product on the table's classes,
    ``mult[c][d] = fold_from(c, rep(d))`` — well defined exactly when the
    stamp-legality sweep is clean (the caller's premise)."""
    n = p.n
    return [[p.fold_from(c, p.rep[d]) for d in range(n)] for c in range(n)]


def _idem(mult: Mult, c: int) -> int:
    """The idempotent power ``c^pi`` of class ``c`` under ``mult``."""
    n = len(mult)
    powers = [c]
    for _ in range(2 * n):
        powers.append(mult[powers[-1]][c])
    for i in range(1, n + 1):
        if powers[i - 1] == powers[2 * i - 1]:
            return powers[i - 1]
    raise AssertionError("no idempotent power (product not associative?)")


def saturation_violation(table: Table, p: Partition) -> Optional[Lasso]:
    """The discordant lasso of the first conjugacy violation, or ``None`` when
    the pair layer is saturated.

    Fills ``P`` on demand — one keyed-lasso bit per linked pair met, through
    the evidence ledger — and compares it across one-step conjugates. On a
    violation, one referee query on the rotated lasso decides which name lies;
    the returned lasso is the presentation bearing that name, ready for the
    chain. ``None`` certifies well-formedness of ``<S_T, P>``."""
    mult = induced_mult(p)
    n = p.n
    idem: Dict[int, int] = {}
    P: Dict[Tuple[int, int], bool] = {}

    def idem_of(c: int) -> int:
        e = idem.get(c)
        if e is None:
            e = idem[c] = _idem(mult, c)
        return e

    def pbit(s: int, e: int) -> bool:
        bit = P.get((s, e))
        if bit is None:
            bit = P[(s, e)] = table.query_lasso(Lasso(p.rep[s], p.rep[e]))
        return bit

    for s in range(n):
        if s == p.start:
            continue
        for c in range(n):
            if c == p.start:
                continue
            for d in range(n):
                if d == p.start:
                    continue
                e1 = idem_of(mult[c][d])
                if mult[s][e1] != s:
                    continue
                s2, e2 = mult[s][c], idem_of(mult[d][c])
                if (s, e1) == (s2, e2):
                    continue
                b1, b2 = pbit(s, e1), pbit(s2, e2)
                if b1 == b2:
                    continue
                # The rotated lasso, in its two presentations; one referee bit.
                w1 = Lasso(p.rep[s], p.rep[c] + p.rep[d])            # names (s, e1)
                w2 = Lasso(p.rep[s] + p.rep[c], p.rep[d] + p.rep[c])  # names (s2, e2)
                b0 = table.query_lasso(w1)
                return w1 if b0 != b1 else w2
    return None
