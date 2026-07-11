"""E3 census: ROLL FDFA baseline vs our learner over the flat catalogue, with
paired medians (spec §6 E3). Streams one raw row per (language, kind) as it goes,
then computes the summary a posteriori from that CSV — the genaut pattern (sweep
now, study later), so the ROLL-free summary is re-runnable without re-invoking
ROLL.

    python3 -m tests.sosl.census_e3 [--limit N] [--cases i:j] [--only KIND]
                                    [--roll-timeout S] [--out-csv FILE]
                                    [--from-sweep SWEEP_CSV] [--summary-only]
                                    [--done CSV]

Source is the flat catalogue `genaut/corpus/flat_canon` (the project standard).
Each row is one **kind** of one language, in a long format that concatenates
across shards: `case, kind, size, MQ, EQ`, where `kind` is `ours` (our class
count N, its MQ/EQ under the default config) or one of ROLL's three FDFA modes
(`size` = leading + progress states). The cluster unit is one `(case, mode)` — a
single sequential JVM — so `--cases i:j` slices the catalogue and `--only KIND`
picks one kind, and each shard writes its private `$OARRUN_OUT.csv` (the runner
forbids a shared file). `reap.sh` concatenates; `--summary-only` pivots the merged
CSV back per case. The `ours` kind is not run on the cluster: it equals the
learner sweep's default leg, so `--from-sweep SWEEP_CSV` derives those rows off a
finished `census_campaign` CSV (`size` = `ref_classes`, `MQ`/`EQ` =
`n_member_total`/`n_equiv`) instead of recomputing them.

The summary reports the per-metric medians, the size-comparison distribution (how
often the algebra is smaller / larger / tied against ROLL's smallest FDFA — the
wash inside the `N+N²` envelope, not a win), and the SoS-category ventilation
(the LTL cut). Resumable: `(case, kind)` rows already present are skipped.
Writes `tests/sosl/logs/census_e3/{results.csv, summary.md}` by default.

Resume reads that done set from the output file, which is empty in a fan-out shard
— so `--done CSV` supplies it **read-only, from a separate file**, typically a
committed record of an earlier drop, unioned with the output's own rows. A census
of a grown catalogue is then additive: only the new languages invoke ROLL.
"""
from __future__ import annotations

import csv
import os
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

from sosl.experiment.baseline import MODES, ROLL_JAR, run_roll, to_buchi_hoa
from sosl.experiment.manifest import (FLAT_CANON_ROOT, flat_canon_cases,
                                      load_category)
from sosl.experiment.run import Config, run_case

OUT = Path("tests/sosl/logs/census_e3")
DEFAULT = Config("default", saturation=True, eq_mode="bounded")
KINDS: Tuple[str, ...] = ("ours",) + MODES
FIELDS = ["case", "kind", "size", "MQ", "EQ"]


def _median(xs: List[float]) -> float:
    return statistics.median(xs) if xs else -1.0


def _done_rows(csv_path: Path) -> Set[Tuple[str, str]]:
    """The `(case, kind)` pairs already recorded — the resume set."""
    if not csv_path.exists():
        return set()
    with open(csv_path, newline="") as fh:
        return {(r["case"], r["kind"]) for r in csv.DictReader(fh)}


def _summary(csv_path: Path) -> None:
    """Compute the E3 summary a posteriori from the streamed long-format CSV:
    pivot per case, then paired medians, the size-comparison distribution, and the
    LTL-cut ventilation."""
    rows: List[dict] = list(csv.DictReader(open(csv_path, newline="")))
    # case -> kind -> size (ours = class count N, a ROLL mode = FDFA states)
    by_case: Dict[str, Dict[str, int]] = defaultdict(dict)
    for r in rows:
        by_case[r["case"]][r["kind"]] = int(r["size"])

    our_N: List[int] = []
    fdfa: Dict[str, List[int]] = {m: [] for m in MODES}
    smaller = larger = tied = 0
    ltl_cmp = {True: [0, 0, 0], False: [0, 0, 0], None: [0, 0, 0]}  # s/l/t
    for case, kinds in by_case.items():
        n = kinds.get("ours", -1)
        if n >= 0:
            our_N.append(n)
        best = -1
        for m in MODES:
            v = kinds.get(m, -1)
            if v >= 0:
                fdfa[m].append(v)
                best = v if best < 0 else min(best, v)
        if best < 0 or n < 0:
            continue
        cat = load_category(f"{FLAT_CANON_ROOT}/sos/{case}.sos")
        key = cat.ltl if cat else None
        if n < best:
            smaller += 1; ltl_cmp[key][0] += 1
        elif n > best:
            larger += 1; ltl_cmp[key][1] += 1
        else:
            tied += 1; ltl_cmp[key][2] += 1

    n_langs = len(by_case)
    lines = ["# E3 census — ROLL FDFA baseline (flat_canon)", ""]
    lines.append(f"{n_langs} languages. Paired medians (our class count N vs "
                 "ROLL's FDFA size = leading + progress states):")
    lines.append("")
    lines.append("| metric | ours | ROLL periodic | ROLL syntactic | ROLL recurrent |")
    lines.append("|---|--:|--:|--:|--:|")
    lines.append(f"| median size | {_median(our_N):.0f} | "
                 + " | ".join(f"{_median(fdfa[m]):.0f}" for m in MODES) + " |")
    lines.append("")
    cmp_n = smaller + larger + tied
    lines.append(f"**Size comparison over {cmp_n} languages** (algebra N vs ROLL's "
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
    print(f"E3: {n_langs} langs | median N={_median(our_N):.0f} "
          f"FDFA={{{', '.join(f'{m}:{_median(fdfa[m]):.0f}' for m in MODES)}}}")
    print(f"  size: algebra smaller {smaller} / larger {larger} / tied {tied}")
    print(f"artifacts: {OUT / 'results.csv'}, {OUT / 'summary.md'}")


def _ours_row(case) -> dict:
    """The `ours` row for a case: class count N and its MQ/EQ (default config)."""
    s = run_case(case.case_id, case.hoa, DEFAULT, reference_sos=case.sos).stats
    return {"case": case.case_id, "kind": "ours", "size": s.ref_classes,
            "MQ": s.n_member_total, "EQ": s.n_equiv}


def _ours_from_sweep(sweep_csv: str) -> List[dict]:
    """The `ours` long-rows read off a finished `census_campaign` CSV: one per
    default-leg row, `size` = `ref_classes` (the config-independent class count N),
    `MQ`/`EQ` = that leg's `n_member_total`/`n_equiv`. This is identical to running
    the learner again, without the recompute."""
    out: List[dict] = []
    with open(sweep_csv, newline="") as fh:
        for r in csv.DictReader(fh):
            if r.get("config_id") != "default":
                continue
            out.append({"case": r["case_id"], "kind": "ours",
                        "size": r["ref_classes"], "MQ": r["n_member_total"],
                        "EQ": r["n_equiv"]})
    return out


def _roll_row(case, mode: str, ba_file: str, roll_timeout: int) -> dict:
    """One ROLL-mode row for a case: FDFA size and MQ/EQ, or `-1`s if the run did
    not produce stats (timeout / parse failure)."""
    r = run_roll(ba_file, mode, case.case_id, roll_timeout)
    ok = r.ok
    return {"case": case.case_id, "kind": mode,
            "size": r.fdfa_states if ok else -1,
            "MQ": r.n_member if ok else -1, "EQ": r.n_equiv if ok else -1}


def main(argv: List[str]) -> int:
    limit = 0
    roll_timeout = 60
    summary_only = False
    cases_spec = ""
    only = ""
    out_csv = ""
    from_sweep = ""
    done_csv = ""
    skip = -1
    for i, a in enumerate(argv):
        if i == skip:
            continue
        if a == "--limit":
            limit = int(argv[i + 1]); skip = i + 1
        elif a == "--roll-timeout":
            roll_timeout = int(argv[i + 1]); skip = i + 1
        elif a == "--cases":
            cases_spec = argv[i + 1]; skip = i + 1
        elif a == "--only":
            only = argv[i + 1]; skip = i + 1
        elif a == "--out-csv":
            out_csv = argv[i + 1]; skip = i + 1
        elif a == "--from-sweep":
            from_sweep = argv[i + 1]; skip = i + 1
        elif a == "--done":
            done_csv = argv[i + 1]; skip = i + 1
        elif a == "--summary-only":
            summary_only = True

    OUT.mkdir(parents=True, exist_ok=True)
    if out_csv:
        csv_path = Path(out_csv)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        csv_path = OUT / "results.csv"

    if summary_only:
        if not csv_path.exists():
            print(f"no {csv_path}", file=sys.stderr)
            return 2
        _summary(csv_path)
        return 0

    if from_sweep:
        # The `ours` kind is exactly the learner sweep's default leg: our class
        # count N is the config-independent reference count (`ref_classes`), and
        # its MQ/EQ are that leg's `n_member_total`/`n_equiv`. Derive the rows from
        # the finished sweep CSV rather than re-running the learner.
        rows = _ours_from_sweep(from_sweep)
        fresh = not csv_path.exists()
        done = _done_rows(csv_path)
        n = 0
        with open(csv_path, "a", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS)
            if fresh:
                writer.writeheader()
            for row in rows:
                if (row["case"], "ours") in done:
                    continue
                writer.writerow(row)
                n += 1
        print(f"ours derived from {from_sweep}: {n} rows -> {csv_path}",
              file=sys.stderr)
        return 0

    kinds = KINDS
    if only:
        if only not in KINDS:
            print(f"--only expects one of {KINDS}, got {only!r}", file=sys.stderr)
            return 2
        kinds = (only,)
    if any(k in MODES for k in kinds) and not os.path.exists(ROLL_JAR):
        print(f"ROLL.jar not found at {ROLL_JAR}", file=sys.stderr)
        return 3

    cases = flat_canon_cases()
    if not cases:
        print("no flat_canon cases", file=sys.stderr)
        return 2
    if cases_spec:
        from tests.sosl.census_campaign import _parse_slice
        lo, hi = _parse_slice(cases_spec, len(cases))
        cases = cases[lo:hi]
        print(f"--cases {cases_spec}: languages [{lo}, {hi})", file=sys.stderr)
    if limit:
        cases = cases[:limit]

    # The output's own rows resume an interrupted run; `--done` adds a read-only
    # prior record (a committed earlier drop), which is what makes a fan-out shard
    # additive — its private output file is always empty.
    done = _done_rows(csv_path)
    if done_csv:
        done |= _done_rows(Path(done_csv))
    print(f"flat_canon E3: {len(cases)} languages x {len(kinds)} kind(s) "
          f"{kinds}; {len(done)} rows already done", file=sys.stderr, flush=True)

    fresh = not csv_path.exists()
    fh = open(csv_path, "a", newline="")
    writer = csv.DictWriter(fh, fieldnames=FIELDS)
    if fresh:
        writer.writeheader(); fh.flush()

    work_dir = str(OUT / "targets")
    os.makedirs(work_dir, exist_ok=True)
    for i, case in enumerate(cases):
        todo = [k for k in kinds if (case.case_id, k) not in done]
        if not todo:
            continue
        if "ours" in todo:
            writer.writerow(_ours_row(case)); fh.flush()
        roll_kinds = [k for k in todo if k in MODES]
        if roll_kinds:
            ba_file = os.path.join(work_dir, f"{case.case_id}.ba.hoa")
            try:
                with open(ba_file, "w", encoding="utf-8") as bf:
                    bf.write(to_buchi_hoa(case.hoa))
                for m in roll_kinds:
                    writer.writerow(_roll_row(case, m, ba_file, roll_timeout))
                    fh.flush()
            except Exception as exc:  # noqa: BLE001 -- record conversion faults per case
                for m in roll_kinds:
                    writer.writerow({"case": case.case_id, "kind": m, "size": -1,
                                     "MQ": -1, "EQ": -1})
                    fh.flush()
                print(f"  convert failed {case.case_id}: {exc}", file=sys.stderr)
        if (i + 1) % 25 == 0:
            print(f"  ... {i + 1}/{len(cases)}", file=sys.stderr, flush=True)
    fh.close()

    if not out_csv and not only:
        _summary(csv_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
