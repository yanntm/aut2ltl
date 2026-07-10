"""Census-backed campaign over the flat, complement-closed catalogue: learn every
language under the default (saturation on) and the ablation (`--no-saturation
--eq-mode exact`) configs, **streaming one CSV row per run as it goes**.

    python3 -m tests.sosl.census_campaign [--config default|ablate|both]
                                          [--limit N] [--budget S] [--out DIR]

The source is the flat catalogue `genaut/corpus/flat_canon` (one file per
language up to AP relabeling, closed under complement — the project standard);
there are no shapes to select. `default` learns with saturation on (soundness +
E1 cost metrics); `ablate` runs `--no-saturation --eq-mode exact` (E2: with exact
equivalence every surviving stall is provably permanent).

This driver only *produces* the raw per-run data — it prints progress and appends
`<out>/results.csv` incrementally (genaut style: sweep now, study later). The
stats are computed a posteriori by `census_e1` (E1 soundness + per-N cost) and
`census_e2_exhibits` (E2 permanent-stall family + exhibits), each reading this
CSV. The run is **resumable**: `(case, config)` rows already present are skipped.
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path
from typing import List, Set, Tuple

from sosl.experiment.manifest import DEFAULT, NOSAT_EXACT, flat_canon_cases
from sosl.experiment.run import Config, _Budget, run_case
from sosl.experiment.stats import CSV_FIELDS, RunStats, csv_row

OUT = Path("tests/sosl/logs/census")
PER_CASE_BUDGET = 30


def _done_runs(csv_path: Path) -> Set[Tuple[str, str]]:
    """The `(case_id, config_id)` pairs already recorded in ``csv_path`` — the
    resume set, so an interrupted sweep continues where it stopped."""
    if not csv_path.exists():
        return set()
    with open(csv_path, newline="") as fh:
        return {(r["case_id"], r["config_id"]) for r in csv.DictReader(fh)}


def main(argv: List[str]) -> int:
    config_sel = "both"
    limit = 0
    budget = PER_CASE_BUDGET
    out = OUT
    skip = -1
    for i, a in enumerate(argv):
        if i == skip:
            continue
        if a == "--config":
            config_sel = argv[i + 1]
            skip = i + 1
        elif a == "--limit":
            limit = int(argv[i + 1])
            skip = i + 1
        elif a == "--budget":
            budget = int(argv[i + 1])
            skip = i + 1
        elif a == "--out":
            out = Path(argv[i + 1])
            skip = i + 1

    cases = flat_canon_cases()
    if not cases:
        print("no flat_canon cases (is genaut/corpus/flat_canon/det built?)",
              file=sys.stderr)
        return 2
    if limit:
        cases = cases[:limit]

    configs: List[Config] = []
    if config_sel in ("default", "both"):
        configs.append(Config(**{**DEFAULT.__dict__, "budget_seconds": budget}))
    if config_sel in ("ablate", "both"):
        configs.append(Config(**{**NOSAT_EXACT.__dict__, "budget_seconds": budget}))

    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / "results.csv"
    done = _done_runs(csv_path)
    total = len(cases) * len(configs)
    print(f"flat_canon: {len(cases)} languages x {len(configs)} config(s) "
          f"= {total} runs; {len(done)} already done", file=sys.stderr, flush=True)

    fresh = not csv_path.exists()
    fh = open(csv_path, "a", newline="")
    writer = csv.writer(fh)
    if fresh:
        writer.writerow(CSV_FIELDS)
        fh.flush()

    n = ran = 0
    tally: dict = {}
    t0 = time.time()
    for case in cases:
        for cfg in configs:
            n += 1
            if (case.case_id, cfg.config_id) in done:
                continue
            try:
                res = run_case(case.case_id, case.hoa, cfg, reference_sos=case.sos)
                st = res.stats
            except _Budget:
                # SIGALRM can fire inside `run_case`'s own `finally` window, after
                # its `except _Budget` is no longer reachable, so the alarm leaks
                # past `run_case`. The verdict is still a clean budget timeout, not
                # a fault: record BUDGET, never FAIL.
                st = RunStats(case_id=case.case_id, config_id=cfg.config_id,
                              verdict="BUDGET", detail="CAUGHT:_Budget (finally-race)")
            except Exception as exc:  # noqa: BLE001 -- the sweep never aborts
                # Any other leaked exception is a run that never completed, not a
                # run that completed with a bad byte: FAIL is a soundness verdict
                # (spec §7 row F9), so a fault is CRASH, never FAIL.
                st = RunStats(case_id=case.case_id, config_id=cfg.config_id,
                              verdict="CRASH",
                              detail=f"CAUGHT:{type(exc).__name__}: {exc}")
            writer.writerow(csv_row(st))
            fh.flush()
            ran += 1
            tally[st.verdict] = tally.get(st.verdict, 0) + 1
            if ran % 100 == 0:
                rate = ran / (time.time() - t0)
                eta = (total - n) / rate / 60 if rate else 0
                print(f"  {n}/{total}  ran={ran}  {dict(sorted(tally.items()))}"
                      f"  {rate:.1f}/s  eta~{eta:.0f}m",
                      file=sys.stderr, flush=True)
    fh.close()

    print(f"done: {ran} new runs; verdicts {dict(sorted(tally.items()))}",
          file=sys.stderr, flush=True)
    print(str(csv_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
