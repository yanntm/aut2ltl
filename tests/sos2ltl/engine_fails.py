"""Rank the verified-non-equivalent sos2ltl answers, smallest first.

    python3 -m tests.sos2ltl.engine_fails <sos2ltl_survey.csv> \
        [--sos-dir genaut/corpus/flat_canon/sos] [--top N]

Reads a survey CSV (a `--use sos2ltl` run over `flat_canon/det`), keeps the
rows whose `validation` is `FAIL` (Spot verified the emitted formula is *not*
equivalent to the input language), and joins each to its language: `|𝒞|` (the
`.sos` class count), the canonical `D`'s state count, the Wagner degree (the
`.cat` sidecar), the producing technique, and the formula. Rows are ordered by
`(|𝒞|, states, formula size)` so the first line is the **smallest** language on
which the engine is unsound — the exhibit to describe in the report. Prints a
per-technique tally so an engine bug is not confused with a dg-baseline one.
"""
from __future__ import annotations

import csv
import os
import sys
from typing import Dict, List, Tuple

from tests.sos2ltl.cat_sidecar import cat_for

DEFAULT_SOS_DIR = "genaut/corpus/flat_canon/sos"


def _classes(sos_path: str) -> int:
    """The `|𝒞|` (class count) from a `.sos`'s `classes:` header, or -1."""
    if not os.path.exists(sos_path):
        return -1
    with open(sos_path) as f:
        for line in f:
            if line.startswith("classes:"):
                return int(line.split(":", 1)[1])
    return -1


def _states(hoa_path: str) -> int:
    """The `States:` count of a HOA file, or -1."""
    if not os.path.exists(hoa_path):
        return -1
    with open(hoa_path) as f:
        for line in f:
            if line.startswith("States:"):
                return int(line.split(":", 1)[1])
    return -1


def main(argv: List[str]) -> int:
    csv_path = argv[0]
    sos_dir = argv[argv.index("--sos-dir") + 1] if "--sos-dir" in argv \
        else DEFAULT_SOS_DIR
    det_dir = sos_dir.replace("/sos", "/det")
    top = int(argv[argv.index("--top") + 1]) if "--top" in argv else 12

    rows = list(csv.reader(open(csv_path)))
    h = rows[0]
    si, vi, ti, fi = (h.index("source"), h.index("validation"),
                      h.index("technique"), h.index("formula"))

    fails: List[Tuple[int, int, int, Dict[str, str]]] = []
    tech: Dict[str, int] = {}
    for r in rows[1:]:
        if len(r) <= vi or r[vi] != "FAIL":
            continue
        lang_id = os.path.basename(r[si])[:-4]  # strip .hoa
        tech[r[ti]] = tech.get(r[ti], 0) + 1
        n = _classes(os.path.join(sos_dir, lang_id + ".sos"))
        st = _states(os.path.join(det_dir, lang_id + ".hoa"))
        fails.append((n, st, len(r[fi]),
                      {"id": lang_id, "tech": r[ti], "formula": r[fi]}))

    fails.sort(key=lambda t: (t[0], t[1], t[2]))
    print(f"{len(fails)} verified-non-equivalent (FAIL) answers")
    print(f"  by technique: {tech}")
    print(f"  smallest {min(top, len(fails))} by (|𝒞|, states, |formula|):")
    print(f"  {'id':32s} {'|𝒞|':>4} {'st':>3} {'degree':>8}  technique / formula")
    for n, st, _, d in fails[:top]:
        cat = cat_for(sos_dir, d["id"])
        deg = cat.phi if cat else "?"
        print(f"  {d['id']:32s} {n:4d} {st:3d} {deg:>8}  {d['tech']}")
        print(f"       {d['formula']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
