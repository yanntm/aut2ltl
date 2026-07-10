"""survey.cluster.shard — run one index range of a discovered survey, CSV to stdout.

Re-enumerates the given inputs with `survey.discovery.discover` and runs only
`examples[I:J]`. Discovery is sorted, so the range names the same examples here
as it did wherever the range was chosen; pass the same `--folder` arguments, in
the same order, or the indices mean something else.

Stdout carries the CSV and nothing else — one self-contained shard with its own
header, ready to redirect into a private file; the end-of-run summary and the
trace go to stderr. Each example keeps the `source` it was discovered with, which
is what makes the shards reassemble into a CSV comparable, row for row, with an
unsharded run.

    python3 -m survey.cluster.shard --folder samples/benchmark --slice 0:7
"""
from __future__ import annotations

import argparse
import contextlib
import sys
import tempfile
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

    # `run` puts the CSV on stdout only when it has no --logs, and its end-of-run
    # summary on stdout either way. Give it a logs dir so the two are separable,
    # divert the summary to stderr, and leave stdout holding nothing but CSV.
    with tempfile.TemporaryDirectory() as tmp:
        with contextlib.redirect_stdout(sys.stderr):
            rc = run(chunk, args.use, logs_dir=Path(tmp), verify=True,
                     verbose=False, build_timeout=args.build_timeout,
                     equiv_timeout=args.equiv_timeout)
        for csv in Path(tmp).glob("survey_*.csv"):
            sys.stdout.write(csv.read_text())
    return rc


if __name__ == "__main__":
    sys.exit(main())
