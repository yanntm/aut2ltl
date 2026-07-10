"""Decompose the engine's declines over a survey CSV, by precondition.

    python3 -m tests.sos2ltl.decline_split <sos2ltl_survey.csv> \
        [--sos-dir genaut/corpus/flat_canon/sos]

For every row whose technique is the DG fallback (`sos2ltl+sos2ltl.dg`),
re-runs the engine's own read-offs on the language's `.sos`: the uncapped
condition-(A) fixpoint per layer, and the window-term computability per
final-candidate layer. Prints the split — languages with a no-width layer
(the scoped-fallback stratum, paper Prop 4.14) vs. languages declining on
a window-term budget gap alone — plus, over the *whole* catalogue, the
distribution of finite (A)-widths ≥ 2 (the graded stratum the engine now
renders; a width ≥ 4 language is one the capped E1 tester called FAIL
that the uncapped fixpoint anchors — H7 material).
"""
from __future__ import annotations

import csv
import os
import sys
from collections import Counter
from typing import List, Optional

from aut2ltl.sos2ltl import anchoring, engine, windows
from aut2ltl.sos2ltl.cayley import build
from sosl.sos import load_invariant

DEFAULT_SOS_DIR = "genaut/corpus/flat_canon/sos"


def main(argv: List[str]) -> int:
    csv_path = argv[0]
    sos_dir = (argv[argv.index("--sos-dir") + 1] if "--sos-dir" in argv
               else DEFAULT_SOS_DIR)

    dg_ids: List[str] = []
    engine_widths: Counter = Counter()
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            tech = row.get("technique", "")
            if tech == "sos2ltl+sos2ltl.dg":
                dg_ids.append(row["input"].removesuffix(".hoa"))
            elif tech == "sos2ltl+sos2ltl.engine":
                engine_widths[row["input"].removesuffix(".hoa")] = 0

    no_width, window_gap, both, neither = [], [], [], []
    for lang in dg_ids:
        path = os.path.join(sos_dir, lang + ".sos")
        with open(path) as f:
            inv = load_invariant(f.read())
        cay = build(inv)
        anch = anchoring.analyze(cay)
        a_fail = any(la.width is None for la in anch)
        lets = engine._Letters(inv)
        w_gap = False
        if not a_fail:
            for i in range(len(cay.layers)):
                rep = windows.analyze_layer(cay, i)
                if engine._window_term(cay, i, rep, lets) is None:
                    w_gap = True
                    break
        (both if a_fail and w_gap else
         no_width if a_fail else
         window_gap if w_gap else neither).append(lang)

    print(f"{len(dg_ids)} DG-fallback languages:")
    print(f"  (A) no-width layer:        {len(no_width)}")
    print(f"  window-term gap only:      {len(window_gap)}")
    print(f"  neither (unexpected!):     {len(neither)} {neither[:5]}")

    width_hist: Counter = Counter()
    for lang in engine_widths:
        path = os.path.join(sos_dir, lang + ".sos")
        with open(path) as f:
            inv = load_invariant(f.read())
        cay = build(inv)
        top = max(la.width for la in anchoring.analyze(cay))
        width_hist[top] += 1
    print("rendered languages by max (A)-width:")
    for w in sorted(width_hist):
        print(f"  k = {w}: {width_hist[w]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
