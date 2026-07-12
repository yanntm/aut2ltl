"""The batch driver: run a (case, config) matrix through `run_case` and write the
records as one `results.csv` — a CSV row per run is the only artifact.

Crash-isolation is a contract: `run_case` already turns a budget overrun or an
internal fault into a recorded verdict rather than an exception, and the driver
adds a defensive outer guard, so one case can never kill the campaign. The
driver holds each run's full `RunResult` (stats + invariant + ledger +
signature) in memory for the report layer; only the flat stats reach disk.

This driver runs in-process, so its budget is the cooperative one (see `run` —
`signal.alarm` cannot preempt a native call). That is sound for the E0 matrix of
named cases, which is what it serves; a *sweep* over the catalogue must use
`run_case_bounded`, whose kill the OS enforces.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from sosl.experiment.manifest import Case, e0_runs
from sosl.experiment.run import Config, RunResult, _Budget, run_case
from sosl.experiment.stats import CSV_FIELDS, RunStats, csv_row


@dataclass
class CampaignResult:
    """Everything a campaign produced: the per-run results (in matrix order) and
    the path of the artifact written (the CSV)."""

    results: List[RunResult]
    csv_path: str

    @property
    def stats(self) -> List[RunStats]:
        return [r.stats for r in self.results]


def run_matrix(
    matrix: List[Tuple[Case, Config]], out_dir: str,
    budget_seconds: Optional[int] = None,
) -> CampaignResult:
    """Execute ``matrix``, writing ``out_dir/results.csv`` at the end.
    ``budget_seconds`` overrides each config's own budget when given (used to
    keep an ad-hoc run bounded)."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    results: List[RunResult] = []
    for case, config in matrix:
        cfg = config
        if budget_seconds is not None:
            cfg = Config(**{**config.__dict__, "budget_seconds": budget_seconds})
        try:
            res = run_case(case.case_id, case.hoa, cfg, reference_sos=case.sos)
        except _Budget:
            # SIGALRM can leak past `run_case`'s own `finally` (the alarm firing
            # after its `except _Budget` is unreachable): still a clean timeout.
            stats = RunStats(case_id=case.case_id, config_id=cfg.config_id,
                             verdict="BUDGET", detail="DRIVER-CAUGHT:_Budget (finally-race)")
            res = RunResult(stats)
        except Exception as exc:  # noqa: BLE001 -- defensive: the driver never aborts
            # A leaked fault is a run that never completed, not a soundness FAIL
            # (spec §7 row F9): record CRASH.
            stats = RunStats(case_id=case.case_id, config_id=cfg.config_id,
                             verdict="CRASH",
                             detail=f"DRIVER-CAUGHT:{type(exc).__name__}: {exc}")
            res = RunResult(stats)
        results.append(res)

    csv_path = str(out / "results.csv")
    _write_csv(results, csv_path)
    return CampaignResult(results, csv_path)


def _write_csv(results: List[RunResult], path: str) -> None:
    """Concatenate the run stats into one CSV — one row per run, `CSV_FIELDS`
    header."""
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(CSV_FIELDS)
        for res in results:
            writer.writerow(csv_row(res.stats))


def run_e0(out_dir: str, budget_seconds: Optional[int] = None) -> CampaignResult:
    """Run the E0 validation matrix (spec §6) into ``out_dir``."""
    return run_matrix(e0_runs(), out_dir, budget_seconds)
