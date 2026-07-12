"""Memo-effectiveness stats for one bls cascade build.

    python3 tests/probes/bls/memo_stats.py <file.hoa>

Decomposes the input, emits Fin(C) for every reachable configuration on ONE
CascadeHolder, and prints the construction counters: distinct reach
expansions (`reach_calls` = memo misses), memo populations, result DAG size,
wall time. No oracle and no stringification — a pure construction-cost
probe. Holder fields are read defensively (getattr) so the same probe runs
on code states with different memo layouts.
"""
from __future__ import annotations

import sys
import time
from typing import Tuple

import spot

from aut2ltl.bls.gap import decompose_aut
from aut2ltl.bls.cascade.holder import CascadeHolder
from aut2ltl.bls.operators.fin import fin_c
from aut2ltl.ltl.builders import _Or, _simp_f
from aut2ltl.ltl.metrics import dag_node_count


def main(path: str) -> int:
    casc = decompose_aut(spot.automaton(path))
    holder = CascadeHolder(casc)
    configs = casc.all_configs()
    t0 = time.monotonic()
    fins = [fin_c(c, holder) for c in configs]
    dt = time.monotonic() - t0
    total = _simp_f(_Or(*fins))
    inst = getattr(holder, "inst_memo", None)
    inst_pairs = len(inst) if inst is not None else 0
    inst_nodes = sum(len(m) for m in inst.values()) if inst is not None else 0
    print(f"{path}: levels={casc.num_levels} configs={len(configs)}")
    print(f"  wall={dt:.3f}s reach_calls={holder.reach_calls} "
          f"reach_memo={len(holder.reach_memo)} helper_memo={len(holder.helper_memo)} "
          f"uncond_memo={len(holder.uncond_memo)} inst_pairs={inst_pairs} "
          f"inst_nodes={inst_nodes}")
    print(f"  all-Fin DAG={dag_node_count(total)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
