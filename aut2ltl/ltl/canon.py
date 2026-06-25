"""
aut2ltl/ltl/canon.py — canonical state numbering for an automaton (twa in, twa out).

A `twa_graph`'s state indices are transport-dependent (a process-boundary round-trip
returns the same automaton index-permuted), so anything keyed on its serialization
misses. `normalize` renumbers by a label-canonical traversal so two index-permuted
copies come out identical. The automaton-side peer of `printers.dag_md5`. Heuristic,
not iso-canonical — a residual miss only costs a recompute.
"""
from __future__ import annotations

from collections import deque
from typing import Dict, List, TYPE_CHECKING

import spot

if TYPE_CHECKING:
    from spot import twa_graph


def normalize(aut: "twa_graph") -> "twa_graph":
    """Copy of `aut` with states renumbered canonically: `0` = initial, then BFS
    visiting successors in label-canonical order (cond string, then acceptance).
    Index-permuted copies of one automaton normalize identically. Unreachable states
    trail in old-index order; acceptance/APs/edges preserved."""
    bd = aut.get_dict()
    n = aut.num_states()
    init = aut.get_init_state_number()

    def sorted_out(s: int) -> List["spot.twa_graph.edge_storage"]:
        return sorted(aut.out(s),
                      key=lambda e: (spot.bdd_format_formula(bd, e.cond), str(e.acc)))

    order: List[int] = []
    edges_of: Dict[int, list] = {}
    seen = [False] * n
    dq: "deque[int]" = deque([init])
    seen[init] = True
    while dq:
        s = dq.popleft()
        order.append(s)
        es = sorted_out(s)
        edges_of[s] = es
        for e in es:
            if not seen[e.dst]:
                seen[e.dst] = True
                dq.append(e.dst)
    for s in range(n):
        if not seen[s]:
            order.append(s)
            edges_of[s] = sorted_out(s)

    new = {old: i for i, old in enumerate(order)}
    out = spot.make_twa_graph(bd)
    out.copy_acceptance_of(aut)
    out.copy_ap_of(aut)
    out.new_states(n)
    out.set_init_state(new[init])
    for s in order:
        for e in edges_of[s]:
            out.new_edge(new[s], new[e.dst], e.cond, e.acc)
    return out


__all__ = ["normalize"]
