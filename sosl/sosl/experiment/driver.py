"""The batch driver: run a (case, config) matrix through `run_case`, write one
`stats.json` per run, and concatenate the records into one `results.csv`.

Crash-isolation is a contract: `run_case` already turns a budget overrun or an
internal fault into a recorded verdict rather than an exception, and the driver
adds a defensive outer guard, so one case can never kill the campaign. The
driver holds each run's full `RunResult` (stats + invariant + ledger +
signature) in memory for the report layer; only the flat stats reach disk.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from sosl.experiment.manifest import Case, e0_runs
from sosl.experiment.run import Config, RunResult, run_case
from sosl.experiment.stats import CSV_FIELDS, RunStats, csv_row


@dataclass
class CampaignResult:
    """Everything a campaign produced: the per-run results (in matrix order) and
    the paths of the artifacts written (per-run JSON files and the CSV)."""

    results: List[RunResult]
    json_paths: List[str]
    csv_path: str

    @property
    def stats(self) -> List[RunStats]:
        return [r.stats for r in self.results]


def _run_id(case: Case, config: Config) -> str:
    """A filesystem-safe id for one (case, config) run."""
    return f"{case.case_id}__{config.config_id}"


def run_matrix(
    matrix: List[Tuple[Case, Config]], out_dir: str,
    budget_seconds: Optional[int] = None,
) -> CampaignResult:
    """Execute ``matrix``, writing ``out_dir/<case>__<config>.json`` per run and
    ``out_dir/results.csv`` at the end. ``budget_seconds`` overrides each
    config's own budget when given (used to keep an ad-hoc run bounded)."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    results: List[RunResult] = []
    json_paths: List[str] = []
    for case, config in matrix:
        cfg = config
        if budget_seconds is not None:
            cfg = Config(**{**config.__dict__, "budget_seconds": budget_seconds})
        try:
            res = run_case(case.case_id, case.hoa, cfg, reference_sos=case.sos)
        except Exception as exc:  # noqa: BLE001 -- defensive: the driver never aborts
            stats = RunStats(case_id=case.case_id, config_id=cfg.config_id,
                             verdict="MISMATCH",
                             detail=f"DRIVER-CAUGHT:{type(exc).__name__}: {exc}")
            res = RunResult(stats)
        json_path = str(out / f"{_run_id(case, cfg)}.json")
        res.stats.write_json(json_path)
        results.append(res)
        json_paths.append(json_path)

    csv_path = str(out / "results.csv")
    _write_csv(results, csv_path)
    return CampaignResult(results, json_paths, csv_path)


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
