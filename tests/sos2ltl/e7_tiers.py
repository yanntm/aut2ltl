"""The ω-blindness tier table across E7 ledger outputs (F7 + addendum).

    python3 -m tests.sos2ltl.e7_tiers <e7_TAG.jsonl> [<e7_TAG2.jsonl> ...]

Reads the per-language records `e7_ledger` writes (each carries `h5_hit`,
`right_ideal`, `phase_collapse`) and reports the sufficient-condition
hierarchy `right ideal ⊊ phase-collapse ⊊ ω-blind`:

  * the H5 tier split — right-ideal / phase-collapse-only / P-level — per shape
    and pooled (the language is the unit; pass `--distinct` to drop shapes
    whose languages duplicate another, e.g. a `_parity` twin);
  * the containment / sufficiency guards that must hold: `right ideal ⟹ PC`
    (no RI &¬PC) and `PC ⟹ H5` (no ¬H5 & PC). A violation is a stop-the-line
    bug and exits nonzero.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List


def _tag(path: str) -> str:
    stem = Path(path).stem
    return stem[3:] if stem.startswith("e7_") else stem


def _tier(r: Dict) -> str:
    if not r["h5_hit"]:
        return "non-H5"
    if r["right_ideal"]:
        return "right-ideal"
    return "phase-collapse" if r["phase_collapse"] else "P-level"


def main(argv: List[str]) -> int:
    paths = [a for a in argv if not a.startswith("--")]
    distinct = "--distinct" in argv
    if distinct:  # drop shapes whose language set duplicates a kept one
        paths = [p for p in paths if "parity" not in p]

    pooled: Counter = Counter()
    bug: List[str] = []
    print(f"  {'shape':22s} {'RI':>4} {'PC-only':>8} {'P-level':>8} "
          f"{'H5':>5} {'non-H5':>7}")
    for p in paths:
        c: Counter = Counter()
        for l in Path(p).read_text().splitlines():
            if not l:
                continue
            r = json.loads(l)
            c[_tier(r)] += 1
            if r["right_ideal"] and not r["phase_collapse"]:
                bug.append(f"{r['id']}:RI&¬PC")
            if r["phase_collapse"] and not r["h5_hit"]:
                bug.append(f"{r['id']}:PC&¬H5")
        pooled.update(c)
        h5 = c["right-ideal"] + c["phase-collapse"] + c["P-level"]
        print(f"  {_tag(p):22s} {c['right-ideal']:4d} {c['phase-collapse']:8d} "
              f"{c['P-level']:8d} {h5:5d} {c['non-H5']:7d}")

    h5 = pooled["right-ideal"] + pooled["phase-collapse"] + pooled["P-level"]
    print(f"  {'POOLED':22s} {pooled['right-ideal']:4d} "
          f"{pooled['phase-collapse']:8d} {pooled['P-level']:8d} "
          f"{h5:5d} {pooled['non-H5']:7d}")
    print(f"\n  guards: right-ideal⟹PC and PC⟹H5  ->  "
          f"{'HOLD' if not bug else 'VIOLATED ' + str(bug)}")
    return 1 if bug else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
