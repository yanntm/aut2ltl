"""M4.b — E1 (scaling) + E2 (saturation ablation), over the named cases.

    python3 -m tests.sosl.campaign_m4b

Runs the E2 matrix (every named case under both `default` and `no-sat-exact`)
once — E1 is the default-config view of the same runs — writes `e1_report.md`,
`e2_report.md`, and `results.csv` under `tests/sosl/logs/m4b/`, and asserts:

  - E1: splits ≤ N (reference class count) on every default run;
  - E2: each case's ablation-leg stall class matches theory (spec §6 E2 /
    manifest E2_EXPECT) — the two proven specimens permanent, the rest
    transient — and both specimens are rendered as first-class exhibits.

Census-free: the broad permanent-stall hunt over `genaut/corpus/` (E2's new
science) folds in later via `manifest.census_cases`.
"""
from __future__ import annotations

from pathlib import Path

from sosl.experiment.driver import run_matrix
from sosl.experiment.manifest import E2_EXPECT, e2_runs
from sosl.experiment.report import e1_report, e2_report

OUT = Path("tests/sosl/logs/m4b")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    campaign = run_matrix(e2_runs(), str(OUT))

    (OUT / "e1_report.md").write_text(e1_report(campaign), encoding="utf-8")
    (OUT / "e2_report.md").write_text(e2_report(campaign), encoding="utf-8")

    problems = []

    # E1: designed bound splits <= N on every default run.
    for r in campaign.results:
        s = r.stats
        if s.config_id == "default" and s.n_splits > s.ref_classes:
            problems.append(f"E1 bound: {s.case_id} splits {s.n_splits} > N "
                            f"{s.ref_classes}")

    # E2: ablation-leg stall class matches theory.
    ablation = {r.stats.case_id: r for r in campaign.results
                if r.stats.config_id == "no-sat-exact"}
    for case_id, expect in E2_EXPECT.items():
        r = ablation.get(case_id)
        if r is None:
            problems.append(f"E2: {case_id} ablation run missing")
            continue
        got = r.stats.stall_class
        if got != expect:
            problems.append(f"E2 cross-check: {case_id} stall {got} != {expect}")

    permanents = [cid for cid, r in ablation.items()
                  if r.stats.stall_class == "permanent"]

    print(e2_report(campaign))
    print(f"\nartifacts: {campaign.csv_path}, {OUT/'e1_report.md'}, "
          f"{OUT/'e2_report.md'}")
    print(f"permanent specimens: {sorted(permanents)}")

    if problems:
        print("\nFAILURES:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nALL OK — E1 bound holds; E2 stall classes match theory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
