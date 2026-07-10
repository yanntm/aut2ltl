"""tests.sosl.cluster_plan — cut a flat_canon sweep into shards, emit a cmds.txt.

Two sweeps, one planner. Default plans the **learner sweep** (`census_campaign`):
one line per half-open `--cases` slice, each learning that slice under the
selected leg(s). `--e3` plans the **ROLL-baseline census** (`census_e3`): one line
per `(kind, case-slice)`, kind ∈ {ours} ∪ ROLL's three FDFA modes — each ROLL
line a single sequential JVM per case. Either way every line writes its private
`$OARRUN_OUT.csv` (the runner forbids a shared file — `O_APPEND` is not atomic
over NFS), and `reap.sh` concatenates. Submits nothing, reads nothing on the
cluster.

The split is driven by a single run's worst-case wall budget. A chunk holds as
many runs as the runner's per-command cap can bound at that worst case, so a
pathological run exhausts its own command and never the job around it. That cap
is `OARRUN_TIMEOUT`, read back from `cluster/config.sh` — sourced, not copied, so
the planner cannot drift from the runner (an env override is honoured by both).
Walltime stays the runner's 5-minute default; throughput comes from
`oarrun.sh --split`, which warns and names a fitting split.

    python3 -m tests.sosl.cluster_plan            # learner sweep, from sosl/
    python3 -m tests.sosl.cluster_plan --e3       # ROLL-baseline census
    RUN=$(cluster/oarrun.sh sosl/tests/sosl/logs/cluster/sweep.cmds)  # from repo root

Most runs finish in milliseconds, so packing to the worst case is nearly free. A
command cut at the cap keeps every row it flushed; `oarrun.sh --resume` reclaims
the rest.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from sosl.experiment.baseline import MODES
from sosl.experiment.manifest import flat_canon_cases

# Interpreter start plus imports (and the `cd sosl`), once per command, charged
# against the chunk's share of the per-command cap.
STARTUP_S: int = 10

# Wall budget for one (case, leg) learner run, in seconds — the `--budget`
# census_campaign caps each run at, and the figure a chunk is packed against.
PER_RUN_S: int = 60
# Per-(case, mode) ROLL JVM cap, and the E3 packing figure for a ROLL mode.
ROLL_TIMEOUT_S: int = 60
# Per-case budget for the cheap `ours` kind (reference class count + metrics).
OURS_BUDGET_S: int = 2

_LEGS = {"default": 1, "ablate": 1, "both": 2}


def runner_timeout(config: Path) -> int:
    """Read ``OARRUN_TIMEOUT`` back from the runner's config, in seconds.

    Sourced rather than parsed: ``config.sh`` is a shell file whose values may be
    overridden from the environment, and honouring that override is the point."""
    out = subprocess.run(
        ["bash", "-c", f'source "{config}" && printf %s "$OARRUN_TIMEOUT"'],
        capture_output=True, text=True, check=True).stdout.strip()
    return int(out)


def _chunk(timeout: int, per_run: int) -> int:
    """Runs per command: as many as fit the per-command cap at the worst case."""
    return max(1, (timeout - STARTUP_S) // per_run)


def _slices(n: int, chunk: int) -> List[str]:
    """The `i:j` half-open slice specs tiling `[0, n)` in steps of ``chunk``."""
    return [f"{i}:{min(i + chunk, n)}" for i in range(0, n, chunk)]


def _plan_sweep(n: int, timeout: int, legs: str, budget: int) -> List[str]:
    """One `census_campaign` line per `--cases` slice, sized so a command's cases
    (each `len(legs)` runs of ``budget`` s) fit the per-command cap."""
    per_case = _LEGS[legs] * budget
    if per_case + STARTUP_S > timeout:
        print(f"cluster_plan: one case's budget ({per_case}s for {legs}) plus "
              f"startup ({STARTUP_S}s) exceeds the cap ({timeout}s); commands will "
              f"be cut short — raise OARRUN_TIMEOUT or lower --budget", file=sys.stderr)
    chunk = _chunk(timeout, per_case)
    return [
        f'cd sosl && python3 -m tests.sosl.census_campaign '
        f'--config {legs} --cases {sl} --budget {budget} --out-csv "$OARRUN_OUT.csv"'
        for sl in _slices(n, chunk)
    ]


def _plan_e3(n: int, timeout: int, roll_timeout: int, ours_budget: int) -> List[str]:
    """One `census_e3` line per `(kind, case-slice)`: each ROLL mode packed by its
    JVM cap, the cheap `ours` kind packed by its own small budget."""
    if roll_timeout + STARTUP_S > timeout:
        print(f"cluster_plan --e3: one ROLL run ({roll_timeout}s) plus startup "
              f"({STARTUP_S}s) exceeds the cap ({timeout}s); commands will be cut "
              f"short — raise OARRUN_TIMEOUT or lower --roll-timeout", file=sys.stderr)
    lines: List[str] = []
    roll_chunk = _chunk(timeout, roll_timeout)
    for mode in MODES:
        lines += [
            f'cd sosl && python3 -m tests.sosl.census_e3 '
            f'--cases {sl} --only {mode} --roll-timeout {roll_timeout} '
            f'--out-csv "$OARRUN_OUT.csv"'
            for sl in _slices(n, roll_chunk)
        ]
    ours_chunk = _chunk(timeout, ours_budget)
    lines += [
        f'cd sosl && python3 -m tests.sosl.census_e3 '
        f'--cases {sl} --only ours --out-csv "$OARRUN_OUT.csv"'
        for sl in _slices(n, ours_chunk)
    ]
    return lines


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="tests.sosl.cluster_plan",
        description="Cut a flat_canon sweep into shards, write a cmds.txt.")
    p.add_argument("-o", "--out", type=Path,
                   default=Path("tests/sosl/logs/cluster/sweep.cmds"),
                   metavar="FILE", help="where to write the command list")
    p.add_argument("--config", type=Path, default=Path("../cluster/config.sh"),
                   metavar="FILE", help="the runner config to size chunks against")
    p.add_argument("--e3", action="store_true",
                   help="plan the ROLL-baseline census (census_e3) instead of the "
                        "learner sweep (census_campaign)")
    p.add_argument("--legs", choices=sorted(_LEGS), default="both",
                   help="learner sweep: which config(s) each case runs")
    p.add_argument("--budget", type=int, default=PER_RUN_S, metavar="S",
                   help="learner sweep: per-run wall budget (census cap + packing)")
    p.add_argument("--roll-timeout", type=int, default=ROLL_TIMEOUT_S, metavar="S",
                   help="E3: per-(case, mode) ROLL JVM cap and packing figure")
    p.add_argument("--ours-budget", type=int, default=OURS_BUDGET_S, metavar="S",
                   help="E3: per-case budget for the cheap `ours` kind")
    args = p.parse_args(argv)

    n = len(flat_canon_cases())
    if not n:
        print("cluster_plan: no flat_canon cases "
              "(is genaut/corpus/flat_canon/det built?)", file=sys.stderr)
        return 2

    timeout = runner_timeout(args.config)
    if args.e3:
        lines = _plan_e3(n, timeout, args.roll_timeout, args.ours_budget)
        what = (f"{n} languages x {len(MODES) + 1} kind(s) -> {len(lines)} commands "
                f"({args.roll_timeout}s/ROLL run, {args.ours_budget}s/ours case)")
    else:
        lines = _plan_sweep(n, timeout, args.legs, args.budget)
        what = (f"{n} languages x {_LEGS[args.legs]} leg(s) -> {len(lines)} commands "
                f"({args.budget}s/run)")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n")

    # The runner runs from the repo root; name the cmds file relative to it.
    repo_root = args.config.resolve().parent.parent
    cmds_rel = os.path.relpath(args.out.resolve(), repo_root)
    print(what)
    print(f"{timeout}s cap per command; wrote {args.out}\n")
    print(f"RUN=$(cluster/oarrun.sh {cmds_rel})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
