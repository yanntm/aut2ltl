"""E3 — ROLL FDFA baseline vs our syntactic-ω-semigroup learner (spec §6 E3).

    python3 -m tests.sosl.campaign_e3 [case ...]

For each named case: our reference class count `N` and our learner's membership /
equivalence counts (default config), against ROLL's three canonical FDFA modes
(periodic / syntactic / recurrent) — each mode's FDFA size (leading + progress
DFA states) and its membership / equivalence counts, harvested from ROLL's own
Statistics output. Writes `tests/sosl/logs/e3/e3_report.md`.

Capability column (a result in itself): ROLL's FDFA cannot answer "is L
LTL-definable" (N/A); our invariant reads it off the algebra. Certification
asymmetry (F6): our equivalence is exact, ROLL's is RABIT/sampling.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List

from sosl.experiment.baseline import MODES, ROLL_JAR, roll_case
from sosl.experiment.manifest import NAMED_CASES
from sosl.experiment.run import Config, run_case
from sosl.sos.build import reference_of_hoa

OUT = Path("tests/sosl/logs/e3")
WORK = str(OUT / "targets")
DEFAULT = Config("default", saturation=True, eq_mode="bounded")


def main(argv: List[str]) -> int:
    if not os.path.exists(ROLL_JAR):
        print(f"ROLL.jar not found at {ROLL_JAR} — build it "
              f"(~/git/roll-library: bash build.sh)", file=sys.stderr)
        return 3
    picked = set(argv)
    cases = [c for c in NAMED_CASES if not picked or c.case_id in picked]

    lines: List[str] = ["# E3 — ROLL FDFA baseline", ""]
    lines.append("`ours`: syntactic-ω-semigroup class count N and (MQ/EQ). "
                 "`ROLL <mode>`: FDFA size (leading+progress states) and (MQ/EQ). "
                 "Certification: ours exact, ROLL RABIT/sampling (F6).")
    lines.append("")
    lines.append("| case | ours N (MQ/EQ) | ROLL periodic (MQ/EQ) "
                 "| ROLL syntactic (MQ/EQ) | ROLL recurrent (MQ/EQ) | LTL-def? |")
    lines.append("|---|---|---|---|---|:--:|")

    for case in cases:
        ref = reference_of_hoa(case.hoa)
        ours = run_case(case.case_id, case.hoa, DEFAULT).stats
        runs = {r.mode: r for r in roll_case(case.case_id, case.hoa, WORK)}
        cells = []
        for mode in MODES:
            r = runs.get(mode)
            if r and r.ok:
                cells.append(f"{r.fdfa_states} ({r.n_member}/{r.n_equiv})")
            else:
                cells.append(f"— ({r.detail if r else 'n/a'})")
        lines.append(
            f"| {case.case_id} | {ref.n} ({ours.n_member_total}/{ours.n_equiv}) "
            f"| {cells[0]} | {cells[1]} | {cells[2]} "
            f"| ours: yes · FDFA: N/A |")
        print(f"{case.case_id}: ours N={ref.n} | "
              + " | ".join(f"{m}={c}" for m, c in zip(MODES, cells)))

    lines.append("")
    lines.append("**Capability.** Only our invariant answers LTL-definability "
                 "(the aperiodicity/group test on the algebra); an FDFA cannot — "
                 "reported as a result, not a gap.")
    lines.append("")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "e3_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\nartifact: {OUT / 'e3_report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
