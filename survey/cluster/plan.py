"""survey.cluster.plan — discover once, cut into shards, emit a cmds.txt.

Writes one `survey.cluster.shard` invocation per line, each redirecting its CSV
into the private `$OARRUN_OUT.csv` that the cluster runner hands it. Submits
nothing and reads nothing on the cluster.

The split is driven by one number: the worst case of a single example,
`--build-timeout + --equiv-timeout`. What discovery actually found does not
matter beyond its count. A chunk holds as many examples as the runner's
per-command cap can bound at that worst case, so a pathological example can
exhaust its own command and never the job around it.

That cap is read back from `cluster/config.sh` — sourced, not copied, so the
planner cannot drift from the runner it plans for. Nothing needs naming twice,
and neither command below takes a flag:

    python3 -m survey.cluster.plan --folder samples/benchmark -o cmds.txt
    RUN=$(cluster/oarrun.sh cmds.txt)

Most examples finish in milliseconds, so packing to the worst case is nearly free
and the job's walltime is a bet on the average. A job that loses the bet is killed
having kept every result it already wrote; `oarrun.sh --resume` reclaims the rest.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from survey.discovery import discover

# Interpreter start plus imports, once per command. Generous, because it is
# charged against every chunk's share of the per-command cap.
STARTUP_S: int = 20


def runner_timeout(config: Path) -> int:
    """Read OARRUN_TIMEOUT back from the runner's config, in seconds.

    Sourced rather than parsed: config.sh is a shell file whose values may be
    overridden from the environment, and honouring that override is the point.
    """
    out = subprocess.run(
        ["bash", "-c", f'source "{config}" && printf %s "$OARRUN_TIMEOUT"'],
        capture_output=True, text=True, check=True).stdout.strip()
    return int(out)


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="survey.cluster.plan",
        description="Discover the examples, cut them into shards, write cmds.txt.")
    p.add_argument("--folder", action="append", default=[], metavar="PATH",
                   required=True, help="file or dir, recursed (repeatable)")
    p.add_argument("-o", "--out", type=Path, default=Path("cmds.txt"),
                   metavar="FILE", help="where to write the command list")
    p.add_argument("--config", type=Path, default=Path("cluster/config.sh"),
                   metavar="FILE", help="the runner config to size chunks against")
    p.add_argument("--use", action="append", default=[], metavar="TECH",
                   help="technique, forwarded opaquely to every shard "
                        "(repeatable); omit for the default")
    p.add_argument("--build-timeout", type=int, default=15, metavar="S")
    p.add_argument("--equiv-timeout", type=int, default=15, metavar="S")
    args = p.parse_args(argv)

    n = sum(1 for _ in discover([Path(d) for d in args.folder]))
    if not n:
        print("survey.cluster.plan: no readable examples found", file=sys.stderr)
        return 2

    timeout = runner_timeout(args.config)
    worst_example = args.build_timeout + args.equiv_timeout
    chunk = max(1, (timeout - STARTUP_S) // worst_example)
    if timeout and chunk * worst_example + STARTUP_S > timeout:
        print(f"survey.cluster.plan: one example's worst case ({worst_example}s) "
              f"plus startup ({STARTUP_S}s) exceeds the per-command cap "
              f"({timeout}s); a slow example will be killed as a TIMEOUT",
              file=sys.stderr)

    folder_args = " ".join(f"--folder {d}" for d in args.folder)
    use_args = "".join(f"--use {t} " for t in args.use)
    lines = [
        f'python3 -m survey.cluster.shard {folder_args} '
        f'--slice {i}:{min(i + chunk, n)} {use_args}'
        f'--build-timeout {args.build_timeout} '
        f'--equiv-timeout {args.equiv_timeout} > "$OARRUN_OUT.csv"'
        for i in range(0, n, chunk)
    ]
    # The conventional destination is under the ignored logs/ tree, which a fresh
    # clone does not have.
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n")

    print(f"{n} examples -> {len(lines)} commands of <={chunk}")
    print(f"{worst_example}s worst case per example, {timeout}s cap per command")
    print(f"wrote {args.out}\n")
    print(f"RUN=$(cluster/oarrun.sh {args.out})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
