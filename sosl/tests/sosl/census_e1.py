"""E1 census: the learner's cost metrics vs the reference class count N over the
tractable census, the N-spread the scatter plots need (spec §6 E1).

    python3 -m tests.sosl.census_e1 [shape ...]

Runs the learner (default config) over the given shapes, or the whole tractable
non-deferred census by default, and records per language: N (reference classes),
splits, membership by phase, equivalence queries, columns, wall time. Writes the
scatter data `results.csv` and a per-N summary (median splits / member vs N,
with the designed bounds) to `tests/sosl/logs/census_e1/`.
"""
from __future__ import annotations

import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from sosl.experiment.manifest import census_shapes
from sosl.experiment.run import Config, run_case

OUT = Path("tests/sosl/logs/census_e1")
DEFAULT = Config("default", saturation=True, eq_mode="bounded")


def main(argv: List[str]) -> int:
    cases = census_shapes(shapes=argv or None)
    if not cases:
        print("no census cases (is genaut/corpus/det built?)", file=sys.stderr)
        return 2

    OUT.mkdir(parents=True, exist_ok=True)
    rows: List[dict] = []
    bad = 0
    for i, case in enumerate(cases):
        s = run_case(case.case_id, case.hoa, DEFAULT, reference_sos=case.sos).stats
        if s.verdict != "SOUND":
            bad += 1
        rows.append({
            "case": case.case_id, "N": s.ref_classes,
            "n_classes_initial": s.n_classes_initial, "splits": s.n_splits,
            "member": s.n_member_total, "fill": s.n_member_fill,
            "harvest": s.n_member_harvest, "saturation": s.n_member_saturation,
            "pcache": s.n_member_pcache, "equiv": s.n_equiv,
            "cols_lin": s.n_columns_lin, "cols_om": s.n_columns_om,
            "ap": s.ap_count, "wall": round(s.wall_seconds, 3),
            "verdict": s.verdict,
        })
        if (i + 1) % 50 == 0:
            print(f"  ... {i + 1}/{len(cases)} ({bad} non-SOUND)",
                  file=sys.stderr, flush=True)

    with open(OUT / "results.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    by_n: Dict[int, List[dict]] = defaultdict(list)
    for r in rows:
        by_n[r["N"]].append(r)

    lines = ["# E1 census — learner cost vs N", ""]
    lines.append(f"{len(rows)} languages, {bad} non-SOUND. Per-N medians "
                 "(designed bounds: splits ≤ N; fill ~ O(N²·|Σ|)):")
    lines.append("")
    lines.append("| N | languages | median splits | max splits | median fill "
                 "| median member | median equiv |")
    lines.append("|--:|--:|--:|--:|--:|--:|--:|")
    for nval in sorted(by_n):
        grp = by_n[nval]
        sp = [r["splits"] for r in grp]
        lines.append(
            f"| {nval} | {len(grp)} | {statistics.median(sp):.0f} | {max(sp)} "
            f"| {statistics.median([r['fill'] for r in grp]):.0f} "
            f"| {statistics.median([r['member'] for r in grp]):.0f} "
            f"| {statistics.median([r['equiv'] for r in grp]):.0f} |")
    lines.append("")
    over = [r["case"] for r in rows if r["splits"] > r["N"]]
    lines.append(f"**splits ≤ N holds on all {len(rows)} languages: "
                 f"{'yes' if not over else 'NO — ' + str(over[:5])}.**")
    lines.append("")
    (OUT / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"E1 census: {len(rows)} langs, {bad} non-SOUND, "
          f"N in [{min(by_n)}, {max(by_n)}]")
    print(f"artifacts: {OUT/'results.csv'}, {OUT/'summary.md'}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
