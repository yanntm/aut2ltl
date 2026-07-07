"""sosl.experiment — the campaign layer over learn / validate.

Batch a corpus of automata through learn + validate under per-case budgets,
aggregate the per-run statistics into one CSV, and generate the E0–E6 reports.
Pointers only; the named modules own the logic.

    manifest   the versioned corpus + configuration list
    run        one instrumented run -> RunStats + invariant + ledger
    stats      the RunStats record and its JSON / CSV serializations
    driver     manifest x config iteration, budgets, CSV aggregation
    report     the E0 report and the E4 ledger / signature-matrix renderer
"""
from sosl.experiment.run import Config, RunResult, run_case
from sosl.experiment.stats import RunStats

__all__ = ["Config", "RunResult", "run_case", "RunStats"]
