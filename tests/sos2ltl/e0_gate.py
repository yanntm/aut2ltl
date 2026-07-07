"""The E0 gate — every sos2ltl probe on the triptych, one process per case.

    python3 -m tests.sos2ltl.e0_gate

Runs each probe as a subprocess under a per-case timeout and stops on the
first failure. Green means: the E0 predictions of
`research_notes/sos_toltl_experiments.md` hold end to end — read-offs,
layers, (A)/(B) widths, certificates byte-exact, dg synthesis equivalent,
translator verdicts, canonicity.
"""
from __future__ import annotations

import os
import subprocess
import sys
from typing import List, Tuple

SOS = "samples/fixtures/hoa/sos"
ABS_SOS = os.path.abspath(SOS)
# The classifier probe lives in the sosl subproject and runs from its root.
SOSL_CASES: List[Tuple[str, ...]] = [
    ("tests.sosl.classify_aperiodic", f"{ABS_SOS}/gf_aa.sos", "--expect", "ltl"),
    ("tests.sosl.classify_aperiodic", f"{ABS_SOS}/even.sos",
     "--expect", "group:a,1,2"),
    ("tests.sosl.classify_aperiodic", f"{ABS_SOS}/evenblocks.sos",
     "--expect", "group:a,1,2"),
]
CASES: List[Tuple[str, ...]] = [
    ("tests.sos2ltl.e0_layers", f"{SOS}/gf_aa.sos", "--expect", "gfaa"),
    ("tests.sos2ltl.e0_layers", f"{SOS}/even.sos", "--expect", "even"),
    ("tests.sos2ltl.e0_layers", f"{SOS}/evenblocks.sos", "--expect", "evenblocks"),
    ("tests.sos2ltl.e0_anchoring", f"{SOS}/gf_aa.sos", "--expect", "gfaa"),
    ("tests.sos2ltl.e0_anchoring", f"{SOS}/even.sos", "--expect", "even"),
    ("tests.sos2ltl.e0_anchoring", f"{SOS}/evenblocks.sos", "--expect", "evenblocks"),
    ("tests.sos2ltl.e0_windows", f"{SOS}/gf_aa.sos", "--expect", "gfaa"),
    ("tests.sos2ltl.e0_windows", f"{SOS}/even.sos"),
    ("tests.sos2ltl.e0_windows", f"{SOS}/evenblocks.sos"),
    ("tests.sos2ltl.e0_witness", f"{SOS}/gf_aa.sos", "--expect", "gfaa"),
    ("tests.sos2ltl.e0_witness", f"{SOS}/even.sos", "--expect", "even"),
    ("tests.sos2ltl.e0_witness", f"{SOS}/evenblocks.sos", "--expect", "evenblocks"),
    ("tests.sos2ltl.e7_dualscan", f"{SOS}/gf_aa.sos", "--expect", "gfaa"),
    ("tests.sos2ltl.e7_dualscan", f"{SOS}/even.sos",
     "--hoa", f"{SOS}/even.hoa", "--expect", "even"),
    ("tests.sos2ltl.e7_dualscan", f"{SOS}/evenblocks.sos",
     "--hoa", f"{SOS}/evenblocks.hoa", "--expect", "evenblocks"),
    ("tests.sos2ltl.e0_dg", f"{SOS}/gf_aa.sos", "--expect", "GF(a & Xa)"),
    ("tests.sos2ltl.e0_dg", f"{SOS}/even.sos"),
    ("tests.sos2ltl.e0_engine", f"{SOS}/gf_aa.sos", "--expect", "GF(a & Xa)"),
    ("tests.sos2ltl.e0_engine", f"{SOS}/even.sos", "--expect", "decline"),
    ("tests.sos2ltl.e0_engine", f"{SOS}/evenblocks.sos", "--expect", "decline"),
    ("tests.sos2ltl.e0_translator", f"{SOS}/gf_aa_parity.hoa",
     "--expect", "ok:GF(a & Xa)"),
    ("tests.sos2ltl.e0_translator", f"{SOS}/even.hoa", "--expect", "notltl:linear"),
    ("tests.sos2ltl.e0_translator", f"{SOS}/evenblocks.hoa",
     "--expect", "notltl:omega"),
    ("tests.sos2ltl.e0_canon", f"{SOS}/gf_aa_parity.hoa",
     "research_notes/sos_figs/sources/gf_aa_reset.hoa"),
]


def main() -> int:
    runs = [("sosl", c) for c in SOSL_CASES] + [(".", c) for c in CASES]
    for cwd, case in runs:
        module, args = case[0], list(case[1:])
        cmd = [sys.executable, "-m", module] + args
        print("::", " ".join(cmd[2:]))
        r = subprocess.run(cmd, timeout=15, cwd=cwd)
        if r.returncode != 0:
            print(f"E0 GATE FAILED at: {' '.join(cmd)} (cwd={cwd})")
            return 1
    print(f"E0 GATE: SUCCESS ({len(runs)} cases)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
