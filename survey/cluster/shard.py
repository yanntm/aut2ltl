"""survey.cluster.shard — run one index range of a discovered survey, CSV to stdout.

Re-enumerates the given inputs with `survey.discovery.discover` and runs only
`examples[I:J]`. Discovery is sorted, so the range names the same examples here
as it did wherever the range was chosen; pass the same `--folder` arguments, in
the same order, or the indices mean something else.

The CSV shard streams into `--out`, one flushed row per example, so a command
killed at its cap keeps every example it finished; stdout stays empty and the
summary and trace go to stderr. Each example keeps the `source` it was discovered
with, which is what makes the shards reassemble into a CSV comparable, row for
row, with an unsharded run.

    python3 -m survey.cluster.shard --folder samples/benchmark/inputs --slice 0:8 \
        --out shard.csv
"""
from __future__ import annotations

import argparse
import contextlib
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from survey.discovery import discover
from survey.example import Example
from survey.run import run


def parse_slice(text: str) -> Tuple[int, int]:
    """Parse `I:J` into (I, J), a half-open range with 0 <= I < J."""
    lo, _, hi = text.partition(":")
    try:
        i, j = int(lo), int(hi)
    except ValueError:
        raise argparse.ArgumentTypeError(f"--slice wants I:J, got {text!r}")
    if not 0 <= i < j:
        raise argparse.ArgumentTypeError(f"--slice wants 0 <= I < J, got {text!r}")
    return i, j


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="survey.cluster.shard",
        description="Run one index range of the examples discovered under the "
                    "given folders; the CSV shard prints to stdout.")
    p.add_argument("--folder", action="append", default=[], metavar="PATH",
                   required=True, help="file or dir, recursed (repeatable); must "
                                       "match the planner's folders, in order")
    p.add_argument("--slice", type=parse_slice, required=True, metavar="I:J",
                   help="half-open index range into the discovered examples")
    p.add_argument("--out", type=Path, required=True, metavar="FILE",
                   help="stream the CSV shard here, one flushed row per example")
    p.add_argument("--use", action="append", default=[], metavar="TECH",
                   help="technique, passed through opaquely (repeatable); omit "
                        "for the default")
    p.add_argument("--build-timeout", type=int, default=15, metavar="S")
    p.add_argument("--equiv-timeout", type=int, default=15, metavar="S")
    args = p.parse_args(argv)

    examples: List[Example] = list(discover([Path(d) for d in args.folder]))
    i, j = args.slice
    chunk = examples[i:j]
    if not chunk:
        print(f"survey.cluster.shard: empty slice {i}:{j} of {len(examples)} "
              f"examples", file=sys.stderr)
        return 2

    # Stream straight into the named file: `run` opens it up front and flushes a
    # row per record, so a command killed at its cap keeps every example it
    # finished. Buffering the CSV and writing it at the end would forfeit the
    # whole chunk. The summary, which `run` prints to stdout, goes to stderr.
    with contextlib.redirect_stdout(sys.stderr):
        return run(chunk, args.use, csv_file=args.out, verify=True,
                   verbose=False, build_timeout=args.build_timeout,
                   equiv_timeout=args.equiv_timeout)


if __name__ == "__main__":
    sys.exit(main())
