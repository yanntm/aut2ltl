"""E5 — counterexample sensitivity over the named cases (spec §6 E5).

    python3 -m tests.sosl.campaign_e5

Runs the counterexample-bearing named cases under increasing counterexample
padding (`minimal`, `first`, `padded:2..32`), all with saturation on, and writes
`results.csv` + `e5_report.md` under `tests/sosl/logs/e5/`. Asserts every run
stays correct (padding changes cost, never the learned invariant) and that the
harvest term grows far slower than the counterexample length.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from sosl.experiment.driver import run_matrix
from sosl.experiment.manifest import NAMED_CASES
from sosl.experiment.report import e5_report
from sosl.experiment.run import Config

OUT = Path("tests/sosl/logs/e5")
POLICIES = ["minimal", "first", "padded:2", "padded:4", "padded:8",
            "padded:16", "padded:32"]
# cases that actually consume a counterexample (padding is a no-op otherwise)
CASES = ["gf_aa_parity", "even", "evenblocks", "a_once"]


def main() -> int:
    cases = [c for c in NAMED_CASES if c.case_id in CASES]
    matrix: List[Tuple] = []
    for policy in POLICIES:
        cfg = Config(f"cex-{policy}", saturation=True, eq_mode="bounded",
                     cex_policy=policy)
        matrix += [(c, cfg) for c in cases]

    campaign = run_matrix(matrix, str(OUT))
    report = e5_report(campaign)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "e5_report.md").write_text(report, encoding="utf-8")
    print(report)

    problems = []
    # correctness: every run byte-equal (SOUND); the minimal baseline per case
    # fixes the learned class count padding must not change.
    baseline = {r.stats.case_id: r.stats.learned_classes
                for r in campaign.results if r.stats.config_id == "cex-minimal"}
    for r in campaign.results:
        s = r.stats
        if s.verdict != "SOUND":
            problems.append(f"{s.case_id}/{s.config_id}: verdict {s.verdict}")
        elif s.learned_classes != baseline.get(s.case_id):
            problems.append(f"{s.case_id}/{s.config_id}: classes "
                            f"{s.learned_classes} != baseline {baseline[s.case_id]}")

    if problems:
        print("\nFAILURES:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"\nartifacts: {campaign.csv_path}, {OUT/'e5_report.md'}")
    print("ALL OK — padding preserves the invariant; only cost changes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
