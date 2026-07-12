"""tests.sosl.cluster_plan — cut a flat_canon sweep into shards, emit a cmds.txt.

Two sweeps, one planner. Default plans the **learner sweep** (`census_campaign`):
one line per half-open `--cases` slice, each learning that slice under the
selected leg(s). `--e3` plans the **ROLL-baseline census** (`census_e3`): one line
per `(ROLL mode, case-slice)`, one of ROLL's three FDFA modes — each a single
sequential JVM per case. E3's fourth kind, `ours`, is NOT planned: it equals the
learner sweep's default leg, so it is derived post-hoc with
`census_e3 --from-sweep`, never re-run (it is heavy-tailed, and redundant). Either
way every line writes its private `$OARRUN_OUT.csv` (the runner forbids a shared
file — `O_APPEND` is not atomic over NFS), and `reap.sh` concatenates. Submits
nothing, reads nothing on the cluster.

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

`--done CSV` names a prior drop's results: those rows are already done, so a slice
made entirely of them is not emitted, and every emitted line carries the flag on
to the command, which skips them too. Growing the catalogue then costs only its
new languages — the drop is additive rather than a re-sweep. The path is used
verbatim in the commands, which `cd sosl` first, so name it as they see it.

Most runs finish in milliseconds, so packing to the worst case is nearly free. A
command cut at the cap keeps every row it flushed; `oarrun.sh --resume` reclaims
the rest.
"""
from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple

from sosl.experiment.baseline import MODES
from sosl.experiment.manifest import DEFAULT, NOSAT_EXACT, flat_canon_cases
from sosl.experiment.run import KILL_GRACE_S

# Interpreter start plus imports (and the `cd sosl`), once per command, charged
# against the chunk's share of the per-command cap.
STARTUP_S: int = 10

# Wall budget for one (case, leg) learner run, in seconds — the `--budget`
# census_campaign caps each run at, and the figure a chunk is packed against.
PER_RUN_S: int = 60
# Per-(case, mode) ROLL JVM cap, and the E3 packing figure for a ROLL mode.
ROLL_TIMEOUT_S: int = 60

_LEGS = {"default": 1, "ablate": 1, "both": 2}

# The `config_id` each leg writes in the sweep CSV — what a done set is keyed by.
_LEG_CONFIGS = {
    "default": (DEFAULT.config_id,),
    "ablate": (NOSAT_EXACT.config_id,),
    "both": (DEFAULT.config_id, NOSAT_EXACT.config_id),
}


def _done_pairs(csv_path: Optional[Path], case_col: str, kind_col: str) -> Set[Tuple[str, str]]:
    """The `(case, kind)` pairs a prior drop's CSV already records, under that
    file's own column names (`case_id`/`config_id` for the sweep, `case`/`kind`
    for E3). Absent file, empty set — planning is then unfiltered."""
    if csv_path is None or not csv_path.exists():
        return set()
    with open(csv_path, newline="") as fh:
        return {(r[case_col], r[kind_col]) for r in csv.DictReader(fh)}


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


def _slices(n: int, chunk: int) -> List[Tuple[int, int]]:
    """The half-open `[i, j)` slice bounds tiling `[0, n)` in steps of ``chunk``."""
    return [(i, min(i + chunk, n)) for i in range(0, n, chunk)]


def _plan_sweep(case_ids: List[str], timeout: int, legs: str, budget: int,
                done: Set[Tuple[str, str]], done_csv: Optional[Path]) -> List[str]:
    """One `census_campaign` line per `--cases` slice, sized so a command's cases
    (each `len(legs)` runs of ``budget`` s) fit the per-command cap. A slice whose
    every `(case, config)` is in ``done`` is not emitted at all — the shard would
    do nothing but pay startup — and each emitted line carries `--done` so the
    campaign skips the covered languages it already has."""
    # Pack against the run's ENFORCED ceiling, not its budget. `run_case_bounded`
    # kills a run at `budget + KILL_GRACE_S`, so that sum — not `budget` — is the
    # worst case a command must fit. Packing against the bare budget leaves no
    # room for the kill grace or the child's startup, and a command whose cases
    # all burn their budget then dies ON the cap, losing the rows it had not yet
    # flushed. (Budget-burners are not spread out: a language's complement is the
    # same algebra and burns too, and duals are adjacent in case order, so they
    # arrive in adjacent pairs and land in one command.)
    per_case = _LEGS[legs] * (budget + KILL_GRACE_S)
    if per_case + STARTUP_S > timeout:
        print(f"cluster_plan: one case's enforced ceiling ({per_case}s for "
              f"{legs}: budget {budget}s + {KILL_GRACE_S}s kill grace) plus "
              f"startup ({STARTUP_S}s) exceeds the cap ({timeout}s); commands will "
              f"be cut short — raise OARRUN_TIMEOUT or lower --budget", file=sys.stderr)
    chunk = _chunk(timeout, per_case)
    configs = _LEG_CONFIGS[legs]
    done_arg = f' --done {done_csv}' if done_csv else ""
    lines: List[str] = []
    for lo, hi in _slices(len(case_ids), chunk):
        todo = [c for c in case_ids[lo:hi]
                if any((c, cfg) not in done for cfg in configs)]
        if not todo:
            continue
        lines.append(
            f'cd sosl && python3 -m tests.sosl.census_campaign '
            f'--config {legs} --cases {lo}:{hi} --budget {budget} '
            f'--out-csv "$OARRUN_OUT.csv"{done_arg}')
    return lines


def _plan_e3(case_ids: List[str], timeout: int, roll_timeout: int,
             done: Set[Tuple[str, str]], done_csv: Optional[Path]) -> List[str]:
    """One `census_e3` line per `(ROLL mode, case-slice)`, each mode packed by its
    JVM cap. A `(mode, slice)` whose every case is already in ``done`` is not
    emitted, and each emitted line carries `--done`, so a grown catalogue invokes
    ROLL only on its new languages. The `ours` kind is NOT planned: it equals the
    learner sweep's default leg (heavy-tailed, and redundant), so it is derived
    post-hoc with `census_e3 --from-sweep`, never re-run on the cluster."""
    if roll_timeout + STARTUP_S > timeout:
        print(f"cluster_plan --e3: one ROLL run ({roll_timeout}s) plus startup "
              f"({STARTUP_S}s) exceeds the cap ({timeout}s); commands will be cut "
              f"short — raise OARRUN_TIMEOUT or lower --roll-timeout", file=sys.stderr)
    lines: List[str] = []
    roll_chunk = _chunk(timeout, roll_timeout)
    done_arg = f' --done {done_csv}' if done_csv else ""
    for mode in MODES:
        for lo, hi in _slices(len(case_ids), roll_chunk):
            todo = [c for c in case_ids[lo:hi] if (c, mode) not in done]
            if not todo:
                continue
            lines.append(
                f'cd sosl && python3 -m tests.sosl.census_e3 '
                f'--cases {lo}:{hi} --only {mode} --roll-timeout {roll_timeout} '
                f'--out-csv "$OARRUN_OUT.csv"{done_arg}')
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
    p.add_argument("--done", type=Path, default=None, metavar="CSV",
                   help="a prior drop's results CSV: its rows are already done, so "
                        "they are neither planned nor re-run (the path is passed "
                        "through to each command, so name it as the command sees "
                        "it — the commands `cd sosl` first)")
    args = p.parse_args(argv)

    case_ids = [c.case_id for c in flat_canon_cases()]
    n = len(case_ids)
    if not n:
        print("cluster_plan: no flat_canon cases "
              "(is genaut/corpus/flat_canon/det built?)", file=sys.stderr)
        return 2

    timeout = runner_timeout(args.config)
    if args.e3:
        done = _done_pairs(args.done, "case", "kind")
        lines = _plan_e3(case_ids, timeout, args.roll_timeout, done, args.done)
        todo = len({c for c in case_ids if any((c, m) not in done for m in MODES)})
        what = (f"{n} languages ({todo} to run) x {len(MODES)} ROLL mode(s) -> "
                f"{len(lines)} commands "
                f"({args.roll_timeout}s/ROLL run; ours derived from the sweep)")
    else:
        done = _done_pairs(args.done, "case_id", "config_id")
        lines = _plan_sweep(case_ids, timeout, args.legs, args.budget, done, args.done)
        configs = _LEG_CONFIGS[args.legs]
        todo = len({c for c in case_ids
                    if any((c, cfg) not in done for cfg in configs)})
        what = (f"{n} languages ({todo} to run) x {_LEGS[args.legs]} leg(s) -> "
                f"{len(lines)} commands ({args.budget}s/run)")

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
