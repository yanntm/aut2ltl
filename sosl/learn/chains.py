"""Counterexample processing: turn a mispredicted lasso into one class split.

A counterexample ``(w, z)`` is normalized to ``(w', z') = (w.z^k, z^k)`` with
``k`` the loop's stabilization power, then one *junction* query decides whether
the fault is on the stem or the loop:

  - **stem chain** — the bits ``g_i = member(rep(psi(w'[:i])).w'[i:], z')`` run
    from ``member(w', z')`` (i = 0) to the junction (i = |w'|); a binary search
    finds an adjacent flip ``i`` and mints the linear column
    ``(eps, w'[i+1:], z')``;
  - **loop chain** — the bits ``d_i = member(rep(psi(w')), rep(psi(z'[:i])).z'[i:])``
    run from the junction (i = 0) to the fully-reduced prediction (i = |z'|); a
    binary search finds a flip and mints the omega column
    ``(rep(psi(w')), z'[i+1:])``.

Either way exactly one column is added, which distinguishes a frontier word from
its row and so splits a class on the next stabilization. ``rep(psi(x))`` is the
representative of ``x``'s current class (non-empty for non-empty ``x`` by the
eps-singleton invariant), so every queried lasso is well-formed.
"""
from __future__ import annotations

from typing import Callable, Dict

from sosl.learn.columns import LinCol, OmCol
from sosl.learn.partition import Partition
from sosl.learn.table import Table
from sosl.objects.alphabet import EMPTY, Word
from sosl.objects.lasso import Lasso
from sosl.trace import TRACE_ON, trace


def _stab_power(p: Partition, loop: Word) -> int:
    """The least ``k <= 2n`` with ``fold(loop^{2k}) == fold(loop^k)`` — the loop's
    stabilization power under ``step`` from the start."""
    n = p.n
    efold = [p.start]
    for _ in range(4 * n):
        efold.append(p.fold_from(efold[-1], loop))
    for k in range(1, 2 * n + 1):
        if efold[2 * k] == efold[k]:
            return k
    return n


def _find_flip(bit: Callable[[int], bool], lo: int, hi: int) -> int:
    """Given ``bit(lo) != bit(hi)``, an index ``i in [lo, hi-1]`` with
    ``bit(i) != bit(i+1)``, by binary search."""
    blo = bit(lo)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if bit(mid) != blo:
            hi = mid
        else:
            lo = mid
    return lo


def process_counterexample(table: Table, p: Partition, lasso: Lasso) -> None:
    """Add the one column the counterexample ``lasso`` demands (see module doc)."""
    member = table.query_lasso

    def repfold(x: Word) -> Word:
        return p.rep[p.fold(x)]

    k = _stab_power(p, lasso.loop)
    wp = lasso.stem + lasso.loop * k
    zp = lasso.loop * k

    a_bit = member(Lasso(wp, zp))
    junction = member(Lasso(repfold(wp), zp))
    if TRACE_ON:
        trace("chain", f"normalize k={k} |w'|={len(wp)} |z'|={len(zp)}; "
              f"A={a_bit} J={junction} -> {'stem' if a_bit != junction else 'loop'} chain")

    if a_bit != junction:
        length = len(wp)
        g_cache: Dict[int, bool] = {0: a_bit, length: junction}

        def g(i: int) -> bool:
            if i not in g_cache:
                g_cache[i] = member(Lasso(repfold(wp[:i]) + wp[i:], zp))
            return g_cache[i]

        i = _find_flip(g, 0, length)
        if TRACE_ON:
            trace("chain", f"stem flip i={i} -> LinCol(eps, y={wp[i + 1:]}, t=|{len(zp)}|)")
        table.add_column(LinCol(EMPTY, wp[i + 1:], zp))
    else:
        length = len(zp)
        sw = repfold(wp)
        d_cache: Dict[int, bool] = {0: junction}

        def d(i: int) -> bool:
            if i not in d_cache:
                d_cache[i] = member(Lasso(sw, repfold(zp[:i]) + zp[i:]))
            return d_cache[i]

        i = _find_flip(d, 0, length)
        if TRACE_ON:
            trace("chain", f"loop flip i={i} -> OmCol(x=|{len(sw)}|, y={zp[i + 1:]})")
        table.add_column(OmCol(sw, zp[i + 1:]))
