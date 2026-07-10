"""tests.sosl.cluster_plan — cut the flat_canon sweep into shards, emit a cmds.txt.

Writes one `census_campaign` invocation per line, each learning a half-open slice
`[i, j)` of the fixed `flat_canon_cases()` order and redirecting its CSV into the
private `$OARRUN_OUT.csv` the cluster runner hands it (the runner forbids a shared
output file — `O_APPEND` is not atomic over NFS). Submits nothing and reads
nothing on the cluster.

The split is driven by one number: a single run's worst-case wall budget (the
`--budget` handed to `census_campaign`, default 60 s). A case costs that budget
once per selected leg (`both` = two), and a chunk holds as many cases as the
runner's per-command cap can bound at that worst case, so a pathological case
exhausts its own command and never the job around it.

That cap is `OARRUN_TIMEOUT`, read back from `cluster/config.sh` — sourced, not
copied, so the planner cannot drift from the runner it plans for (an env override
of the cap is honoured by both). Walltime stays the runner's 5-minute default;
throughput comes from `oarrun.sh --split`, which warns and names a fitting split.

    python3 -m tests.sosl.cluster_plan            # from sosl/
    RUN=$(cluster/oarrun.sh sosl/tests/sosl/logs/cluster/sweep.cmds)   # from repo root

Most languages learn in milliseconds, so packing to the worst case is nearly free.
A command cut at the cap keeps every row it flushed; `oarrun.sh --resume` reclaims
the rest.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from sosl.experiment.manifest import flat_canon_cases

# Interpreter start plus imports (and the `cd sosl`), once per command, charged
# against the chunk's share of the per-command cap.
STARTUP_S: int = 10

# Wall budget for one (case, leg) run, in seconds — the `--budget` census_campaign
# caps each run at, and the figure a chunk is packed against.
PER_RUN_S: int = 60

_LEGS = {"default": 1, "ablate": 1, "both": 2}


def runner_timeout(config: Path) -> int:
    """Read ``OARRUN_TIMEOUT`` back from the runner's config, in seconds.

    Sourced rather than parsed: ``config.sh`` is a shell file whose values may be
    overridden from the environment, and honouring that override is the point."""
    out = subprocess.run(
        ["bash", "-c", f'source "{config}" && printf %s "$OARRUN_TIMEOUT"'],
        capture_output=True, text=True, check=True).stdout.strip()
    return int(out)


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="tests.sosl.cluster_plan",
        description="Cut the flat_canon sweep into shards, write a cmds.txt.")
    p.add_argument("-o", "--out", type=Path,
                   default=Path("tests/sosl/logs/cluster/sweep.cmds"),
                   metavar="FILE", help="where to write the command list")
    p.add_argument("--config", type=Path, default=Path("../cluster/config.sh"),
                   metavar="FILE", help="the runner config to size chunks against")
    p.add_argument("--legs", choices=sorted(_LEGS), default="both",
                   help="which config(s) each case runs (both = two runs/case)")
    p.add_argument("--budget", type=int, default=PER_RUN_S, metavar="S",
                   help="per-run wall budget, both the census cap and the packing "
                        "figure")
    args = p.parse_args(argv)

    n = len(flat_canon_cases())
    if not n:
        print("cluster_plan: no flat_canon cases "
              "(is genaut/corpus/flat_canon/det built?)", file=sys.stderr)
        return 2

    timeout = runner_timeout(args.config)
    per_case = _LEGS[args.legs] * args.budget
    chunk = max(1, (timeout - STARTUP_S) // per_case)
    if per_case + STARTUP_S > timeout:
        print(f"cluster_plan: one case's budget ({per_case}s for {args.legs}) "
              f"plus startup ({STARTUP_S}s) exceeds the per-command cap "
              f"({timeout}s); every command will be cut short — raise "
              f"OARRUN_TIMEOUT or lower --budget", file=sys.stderr)

    lines = [
        f'cd sosl && python3 -m tests.sosl.census_campaign '
        f'--config {args.legs} --cases {i}:{min(i + chunk, n)} '
        f'--budget {args.budget} --out-csv "$OARRUN_OUT.csv"'
        for i in range(0, n, chunk)
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n")

    # The runner runs from the repo root; name the cmds file relative to it.
    repo_root = args.config.resolve().parent.parent
    cmds_rel = os.path.relpath(args.out.resolve(), repo_root)
    print(f"{n} languages x {_LEGS[args.legs]} leg(s) -> {len(lines)} commands "
          f"of <={chunk} case(s)")
    print(f"{args.budget}s per run, {per_case}s per case, {timeout}s cap per command")
    print(f"wrote {args.out}\n")
    print(f"RUN=$(cluster/oarrun.sh {cmds_rel})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
