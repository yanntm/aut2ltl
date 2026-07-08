"""E3 baseline: the ROLL FDFA learner over the same census languages (spec §6 E3).

ROLL (`~/git/roll-library`) learns the *language* of a target Büchi automaton, so
the baseline feeds it a state-based Büchi presentation of each census language
(via Spot) and parses its `Statistics` output — membership / equivalence counts
and the learned FDFA size (leading + progress DFAs) — for the three canonical
FDFA modes (periodic / syntactic / recurrent). These pair against our class count
`N` and query counts under the same counting rules (one lasso = one membership).

Protocol asymmetry (recorded, spec §9 F6): ROLL answers its own equivalence
queries with RABIT / sampling over automata, not our exact Cayley oracle — so a
ROLL run is certified differently from ours. Capability: an FDFA cannot answer
"is L LTL-definable" (N/A); our invariant can (the group test).
"""
from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import spot

ROLL_JAR = os.path.expanduser("~/git/roll-library/ROLL.jar")
MODES = ("periodic", "syntactic", "recurrent")

# the Statistics lines we harvest: label -> field
_FIELDS = {
    "#T.S": "target_states", "#H.S": "buchi_states",
    "#L.S": "leading_states", "#F.S": "fdfa_states",
    "#MQ": "n_member", "#EQ": "n_equiv",
}
_LINE = re.compile(r"(#[A-Za-z.]+)\s*=\s*(\d+)")


@dataclass
class RollRun:
    """One ROLL FDFA-learning run's harvested stats (`-1` on a field not seen)."""

    case_id: str
    mode: str
    target_states: int = -1
    buchi_states: int = -1
    leading_states: int = -1
    fdfa_states: int = -1
    n_member: int = -1
    n_equiv: int = -1
    ok: bool = False
    detail: str = ""


def to_buchi_hoa(hoa_path: str) -> str:
    """A **state-based** Büchi HOA of the language of ``hoa_path`` (Spot), the
    form ROLL parses. ``SBAcc`` is essential: ROLL reads state-based acceptance,
    and a transition-based Büchi (the default `postprocess` output) is misread as
    a trivial language. Any Büchi presentation of L is an acceptable target."""
    aut = spot.automaton(hoa_path)
    ba = spot.postprocess(aut, "BA", "SBAcc", "Small", "Low")
    return ba.to_str("hoa")


def run_roll(buchi_hoa_file: str, mode: str, case_id: str,
             timeout_s: int = 120) -> RollRun:
    """Run ROLL's FDFA learner (``mode``) on a Büchi HOA file and harvest stats."""
    run = RollRun(case_id=case_id, mode=mode)
    try:
        proc = subprocess.run(
            ["java", "-jar", ROLL_JAR, "learn", buchi_hoa_file,
             f"-{mode}", "-table"],
            capture_output=True, text=True, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        run.detail = "timeout"
        return run
    if proc.returncode != 0:
        run.detail = f"exit {proc.returncode}: " + proc.stderr.strip()[:200]
        return run
    for label, value in _LINE.findall(proc.stdout):
        if label in _FIELDS:
            setattr(run, _FIELDS[label], int(value))
    run.ok = run.n_member >= 0 and run.fdfa_states >= 0
    if not run.ok and not run.detail:
        run.detail = "no stats parsed"
    return run


def roll_case(case_id: str, hoa_path: str, work_dir: str,
              timeout_s: int = 120) -> List[RollRun]:
    """Convert one census automaton to a Büchi HOA and run ROLL in all three FDFA
    modes; returns one `RollRun` per mode."""
    os.makedirs(work_dir, exist_ok=True)
    ba_file = os.path.join(work_dir, f"{case_id}.ba.hoa")
    try:
        with open(ba_file, "w", encoding="utf-8") as fh:
            fh.write(to_buchi_hoa(hoa_path))
    except Exception as exc:  # noqa: BLE001 -- record conversion faults per case
        return [RollRun(case_id, m, detail=f"convert: {exc}") for m in MODES]
    return [run_roll(ba_file, m, case_id, timeout_s) for m in MODES]
