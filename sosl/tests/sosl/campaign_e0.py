"""E0 — the validation campaign, run through the driver (spec §6 E0, §8 M4.a).

    python3 -m tests.sosl.campaign_e0

Runs the E0 (case, config) matrix via `sosl.experiment.driver`, writes one
`stats.json` per run plus `results.csv` and the E0 report / E4 transcripts under
`tests/sosl/logs/e0/`, and asserts:

  - the E0 gate PASSES (zero FAIL, zero BUDGET, zero CRASH; permanent specimens
    certify ACCEPTOR_ONLY under no-saturation — spec §9 P4/F5);
  - the Even and EvenBlocks split/query ledgers are byte-stable against the M3
    baselines in `sosl_report.md` (spec §9 row P5).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict

from sosl.experiment.driver import run_e0
from sosl.experiment.report import (
    e0_gate,
    e0_report,
    render_ledger,
    render_signature,
)
from sosl.experiment.run import RunResult

OUT = Path("tests/sosl/logs/e0")

# The M3 baselines (sosl_report.md) the row-P5 lock pins: per-phase member
# counts (fill/harvest/saturation/pcache), the initial/final class counts, and
# the escalation count — default config.
BASELINES: Dict[str, dict] = {
    "even": dict(init=3, learned=5, fill=32, harvest=4, sat=7, pcache=8,
                 escalations=1),
    "evenblocks": dict(init=3, learned=8, fill=67, harvest=4, sat=14, pcache=14,
                       escalations=2),
}


def _check_baseline(res: RunResult) -> list:
    s = res.stats
    b = BASELINES[s.case_id]
    got = dict(init=s.n_classes_initial, learned=s.learned_classes,
               fill=s.n_member_fill, harvest=s.n_member_harvest,
               sat=s.n_member_saturation, pcache=s.n_member_pcache,
               escalations=s.n_saturation_escalations)
    return [f"{s.case_id}: {k} expected {b[k]} got {got[k]}"
            for k in b if b[k] != got[k]]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    campaign = run_e0(str(OUT))

    report = e0_report(campaign)
    (OUT / "e0_report.md").write_text(report, encoding="utf-8")
    print(report)

    # E4 transcripts for the default runs of every named case.
    transcript = []
    for res in campaign.results:
        if res.stats.config_id == "default" and res.invariant is not None:
            transcript.append(render_ledger(res))
            transcript.append(render_signature(res))
    (OUT / "e4_transcripts.md").write_text("\n".join(transcript), encoding="utf-8")

    problems = []
    gate = e0_gate(campaign)
    if gate is not None:
        problems.append(f"E0 gate FAIL: {gate}")

    # Row P5: the Even / EvenBlocks default-config ledgers must match M3.
    default = {r.stats.case_id: r for r in campaign.results
               if r.stats.config_id == "default"}
    for case_id in BASELINES:
        if case_id not in default:
            problems.append(f"row P5: {case_id} default run missing")
            continue
        problems += [f"row P5 drift: {msg}" for msg in _check_baseline(default[case_id])]

    print(f"\nartifacts: {campaign.csv_path}, {OUT/'e0_report.md'}, "
          f"{OUT/'e4_transcripts.md'}")
    if problems:
        print("\nFAILURES:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nALL OK — E0 gate PASS; Even/EvenBlocks ledgers byte-stable (row P5)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
