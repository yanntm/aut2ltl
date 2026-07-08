"""E3 census-wide: ROLL FDFA baseline vs our learner over a whole shape, with
paired medians (spec §6 E3, the census extension of `campaign_e3`).

    python3 -m tests.sosl.census_e3 [shape] [per_case_roll_timeout_s]

For every language of the shape (default 2state1ap1acc): our class count N and
(MQ/EQ) under the default config, and ROLL's three FDFA modes (FDFA size, MQ,
EQ). Reports the per-metric medians and the size-comparison distribution — how
often the algebra is smaller / larger / tied against ROLL's smallest FDFA — the
census evidence that the size table is a wash inside the N+N² envelope, not a
win. Writes `tests/sosl/logs/census_e3/<shape>.md` + `results.csv`.
"""
from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path
from typing import Dict, List

from sosl.experiment.baseline import MODES, ROLL_JAR, roll_case
from sosl.experiment.manifest import census_shapes
from sosl.experiment.run import Config, run_case

OUT = Path("tests/sosl/logs/census_e3")
DEFAULT = Config("default", saturation=True, eq_mode="bounded")


def _median(xs: List[int]) -> float:
    return statistics.median(xs) if xs else -1.0


def main(argv: List[str]) -> int:
    import os
    if not os.path.exists(ROLL_JAR):
        print(f"ROLL.jar not found at {ROLL_JAR}", file=sys.stderr)
        return 3
    shape = argv[0] if argv else "2state1ap1acc"
    roll_timeout = int(argv[1]) if len(argv) > 1 else 60

    cases = census_shapes(shapes=[shape])
    if not cases:
        print(f"no census cases for {shape}", file=sys.stderr)
        return 2

    OUT.mkdir(parents=True, exist_ok=True)
    rows: List[dict] = []
    our_N: List[int] = []
    fdfa: Dict[str, List[int]] = {m: [] for m in MODES}
    smaller = larger = tied = 0

    for i, case in enumerate(cases):
        ours = run_case(case.case_id, case.hoa, DEFAULT, reference_sos=case.sos).stats
        runs = {r.mode: r for r in roll_case(case.case_id, case.hoa,
                                             str(OUT / "targets"), roll_timeout)}
        row = {"case": case.case_id, "our_N": ours.ref_classes,
               "our_MQ": ours.n_member_total, "our_EQ": ours.n_equiv}
        best: int = -1
        for m in MODES:
            r = runs.get(m)
            row[f"{m}_fdfa"] = r.fdfa_states if r and r.ok else -1
            row[f"{m}_MQ"] = r.n_member if r and r.ok else -1
            row[f"{m}_EQ"] = r.n_equiv if r and r.ok else -1
            if r and r.ok:
                fdfa[m].append(r.fdfa_states)
                best = r.fdfa_states if best < 0 else min(best, r.fdfa_states)
        rows.append(row)
        our_N.append(ours.ref_classes)
        if best >= 0:
            if ours.ref_classes < best:
                smaller += 1
            elif ours.ref_classes > best:
                larger += 1
            else:
                tied += 1
        if (i + 1) % 20 == 0:
            print(f"  ... {i + 1}/{len(cases)}", file=sys.stderr, flush=True)

    with open(OUT / "results.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    lines = [f"# E3 census — ROLL FDFA baseline over {shape}", ""]
    lines.append(f"{len(cases)} languages. Paired medians (our class count N vs "
                 "ROLL's FDFA size = leading + progress states):")
    lines.append("")
    lines.append("| metric | ours | ROLL periodic | ROLL syntactic | ROLL recurrent |")
    lines.append("|---|--:|--:|--:|--:|")
    lines.append(f"| median size | {_median(our_N):.0f} | "
                 + " | ".join(f"{_median(fdfa[m]):.0f}" for m in MODES) + " |")
    lines.append("")
    n = smaller + larger + tied
    lines.append(f"**Size comparison over {n} languages** (algebra N vs ROLL's "
                 f"smallest FDFA): algebra smaller **{smaller}**, larger "
                 f"**{larger}**, tied **{tied}**. The objects trade places inside "
                 "the `N+N²` envelope — a wash, not a win (Prop. 5.3(a)); the "
                 "capability column (LTL-definability, ours only) is the result.")
    lines.append("")
    (OUT / f"{shape}.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"{shape}: {len(cases)} langs | median N={_median(our_N):.0f} "
          f"FDFA={{{', '.join(f'{m}:{_median(fdfa[m]):.0f}' for m in MODES)}}}")
    print(f"  size: algebra smaller {smaller} / larger {larger} / tied {tied}")
    print(f"artifacts: {OUT/'results.csv'}, {OUT/(shape+'.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
