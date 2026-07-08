"""E3 census: ROLL FDFA baseline vs our learner over the flat catalogue, with
paired medians (spec §6 E3). Streams one raw row per language as it goes, then
computes the summary a posteriori from that CSV — the genaut pattern (sweep now,
study later), so the ROLL-free summary is re-runnable without re-invoking ROLL.

    python3 -m tests.sosl.census_e3 [--limit N] [--roll-timeout S] [--summary-only]

Source is the flat catalogue `genaut/corpus/flat_canon` (the project standard).
For every language: our class count N and (MQ/EQ) under the default config, and
ROLL's three FDFA modes (FDFA size = leading + progress states, MQ, EQ). The
summary reports the per-metric medians, the size-comparison distribution (how
often the algebra is smaller / larger / tied against ROLL's smallest FDFA — the
wash inside the `N+N²` envelope, not a win), and the SoS-category ventilation
(the LTL cut). Resumable: languages already in `results.csv` are skipped.
Writes `tests/sosl/logs/census_e3/{results.csv, summary.md}`.
"""
from __future__ import annotations

import csv
import os
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

from sosl.experiment.baseline import MODES, ROLL_JAR, roll_case
from sosl.experiment.manifest import (FLAT_CANON_ROOT, flat_canon_cases,
                                      load_category)
from sosl.experiment.run import Config, run_case

OUT = Path("tests/sosl/logs/census_e3")
DEFAULT = Config("default", saturation=True, eq_mode="bounded")
FIELDS = (["case", "our_N", "our_MQ", "our_EQ"]
          + [f"{m}_{k}" for m in MODES for k in ("fdfa", "MQ", "EQ")])


def _median(xs: List[float]) -> float:
    return statistics.median(xs) if xs else -1.0


def _done_cases(csv_path: Path) -> Set[str]:
    if not csv_path.exists():
        return set()
    with open(csv_path, newline="") as fh:
        return {r["case"] for r in csv.DictReader(fh)}


def _summary(csv_path: Path) -> None:
    """Compute the E3 summary a posteriori from the streamed raw CSV: paired
    medians, the size-comparison distribution, and the LTL-cut ventilation."""
    rows: List[dict] = list(csv.DictReader(open(csv_path, newline="")))
    our_N = [int(r["our_N"]) for r in rows]
    fdfa: Dict[str, List[int]] = {m: [] for m in MODES}
    smaller = larger = tied = 0
    ltl_cmp = {True: [0, 0, 0], False: [0, 0, 0], None: [0, 0, 0]}  # s/l/t
    for r in rows:
        best = -1
        for m in MODES:
            v = int(r[f"{m}_fdfa"])
            if v >= 0:
                fdfa[m].append(v)
                best = v if best < 0 else min(best, v)
        if best < 0:
            continue
        n = int(r["our_N"])
        cat = load_category(f"{FLAT_CANON_ROOT}/sos/{r['case']}.sos")
        key = cat.ltl if cat else None
        if n < best:
            smaller += 1; ltl_cmp[key][0] += 1
        elif n > best:
            larger += 1; ltl_cmp[key][1] += 1
        else:
            tied += 1; ltl_cmp[key][2] += 1

    lines = ["# E3 census — ROLL FDFA baseline (flat_canon)", ""]
    lines.append(f"{len(rows)} languages. Paired medians (our class count N vs "
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
    lines.append("Size comparison ventilated by the LTL cut "
                 "(the capability our invariant reads off and ROLL's FDFAs cannot):")
    lines.append("")
    lines.append("| definability | smaller | larger | tied |")
    lines.append("|---|--:|--:|--:|")
    for label, key in (("LTL (aperiodic)", True), ("non-LTL", False)):
        s, l, t = ltl_cmp[key]
        if s + l + t:
            lines.append(f"| {label} | {s} | {l} | {t} |")
    lines.append("")
    (OUT / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"E3: {len(rows)} langs | median N={_median(our_N):.0f} "
          f"FDFA={{{', '.join(f'{m}:{_median(fdfa[m]):.0f}' for m in MODES)}}}")
    print(f"  size: algebra smaller {smaller} / larger {larger} / tied {tied}")
    print(f"artifacts: {OUT / 'results.csv'}, {OUT / 'summary.md'}")


def main(argv: List[str]) -> int:
    limit = 0
    roll_timeout = 60
    summary_only = False
    skip = -1
    for i, a in enumerate(argv):
        if i == skip:
            continue
        if a == "--limit":
            limit = int(argv[i + 1]); skip = i + 1
        elif a == "--roll-timeout":
            roll_timeout = int(argv[i + 1]); skip = i + 1
        elif a == "--summary-only":
            summary_only = True

    OUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUT / "results.csv"
    if summary_only:
        if not csv_path.exists():
            print(f"no {csv_path}", file=sys.stderr)
            return 2
        _summary(csv_path)
        return 0

    if not os.path.exists(ROLL_JAR):
        print(f"ROLL.jar not found at {ROLL_JAR}", file=sys.stderr)
        return 3
    cases = flat_canon_cases()
    if not cases:
        print("no flat_canon cases", file=sys.stderr)
        return 2
    if limit:
        cases = cases[:limit]
    done = _done_cases(csv_path)
    print(f"flat_canon E3: {len(cases)} languages; {len(done)} already done",
          file=sys.stderr, flush=True)

    fresh = not csv_path.exists()
    fh = open(csv_path, "a", newline="")
    writer = csv.DictWriter(fh, fieldnames=FIELDS)
    if fresh:
        writer.writeheader(); fh.flush()

    for i, case in enumerate(cases):
        if case.case_id in done:
            continue
        ours = run_case(case.case_id, case.hoa, DEFAULT,
                        reference_sos=case.sos).stats
        runs = {r.mode: r for r in roll_case(case.case_id, case.hoa,
                                             str(OUT / "targets"), roll_timeout)}
        row = {"case": case.case_id, "our_N": ours.ref_classes,
               "our_MQ": ours.n_member_total, "our_EQ": ours.n_equiv}
        for m in MODES:
            r = runs.get(m)
            row[f"{m}_fdfa"] = r.fdfa_states if r and r.ok else -1
            row[f"{m}_MQ"] = r.n_member if r and r.ok else -1
            row[f"{m}_EQ"] = r.n_equiv if r and r.ok else -1
        writer.writerow(row)
        fh.flush()
        if (i + 1) % 25 == 0:
            print(f"  ... {i + 1}/{len(cases)}", file=sys.stderr, flush=True)
    fh.close()

    _summary(csv_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
