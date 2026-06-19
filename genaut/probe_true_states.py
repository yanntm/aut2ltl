"""
genaut/probe_true_states.py — Entry 2: of the universal ("true") survivors, how
many did spot's Small pass leave non-canonical, and are they really universal?

Takes the census CSV, selects every row whose reconstructed formula is `1`, loads
the STORED automaton from the corpus (already Small-postprocessed — NO further
reduction here), and tallies its state count + determinism. Confirms language-
universality the honest way: complement(a).is_empty()  (NOT spot.is_universal,
which is the structural branching property). Reports the histograms and flags any
true row that is NOT actually universal (there should be none).

Usage:  python3 genaut/probe_true_states.py
"""
from __future__ import annotations

import csv
import os
from collections import Counter
from typing import List

import spot

HERE = os.path.dirname(__file__)
CSV_PATH = os.path.join(HERE, "logs", "genaut.csv")
CORPUS_DIR = os.path.join(HERE, "corpus", "2state1ap1acc")


def true_files() -> List[str]:
    out: List[str] = []
    with open(CSV_PATH, newline="") as fh:
        for row in csv.DictReader(fh):
            if (row.get("reconstructed") or "").strip() == "1":
                out.append(row["formula"].strip())
    return out


def main() -> None:
    files = true_files()
    print(f"universal ('true') survivors in census: {len(files)}")

    states_hist: Counter = Counter()
    det_hist: Counter = Counter()
    not_universal: List[str] = []
    for name in files:
        aut = spot.automaton(os.path.join(CORPUS_DIR, name))
        states_hist[aut.num_states()] += 1
        det_hist["det" if spot.is_deterministic(aut) else "nondet"] += 1
        if not spot.complement(aut).is_empty():
            not_universal.append(name)

    print("as stored (one Small pass, no further reduction):")
    print(f"  state-count histogram : {dict(sorted(states_hist.items()))}")
    print(f"  determinism histogram : {dict(det_hist)}")
    if not_universal:
        print(f"  *** NOT universal ({len(not_universal)}): {not_universal[:10]}")
    else:
        print(f"  universality (complement empty): all {len(files)} verified true.")


if __name__ == "__main__":
    main()
