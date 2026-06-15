#!/usr/bin/env python3
"""
tests/sl/init_scc_report.py — for each HOA file, report whether the INITIAL
state lies in a multi-state SCC (size >= 2). Tests the hypothesis that
SlDriven's full-suffix delegation misbehaves exactly when init is already in a
nontrivial SCC (delegation fires at label(init), before any invariant re-add).

Usage:
    python3 tests/sl/init_scc_report.py <hoa-file> [<hoa-file> ...]
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import spot
from aut2ltl.language import Language


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    print(f"{'file':40s} {'init':>4s} {'sccSz':>5s} {'states':>6s}  init_in_multi_scc")
    for path in sys.argv[1:]:
        tgba = Language.of(spot.automaton(path)).tgba()
        init = tgba.get_init_state_number()
        si = spot.scc_info(tgba)
        scc = si.scc_of(init)
        sz = len(si.states_of(scc))
        print(f"{Path(path).name:40s} {init:4d} {sz:5d} {tgba.num_states():6d}"
              f"  {'YES' if sz >= 2 else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
