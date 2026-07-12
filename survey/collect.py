"""survey.collect — the generic run → row → validate collector.

The reusable core of a survey, factored out of the aut2ltl-specific pipeline:
run an arbitrary tool on each discovered `Example` under a strict per-item
budget, turn each run into one CSV row, optionally post-validate that row on an
independent path, and stream everything to a crash-safe, resumable CSV.

Three plug points live in a `Scenario`:

  * `invoke(example)  -> Invocation`  — how the tool is spawned for one input
                                        (the fixed context, e.g. a knowledge K,
                                        is captured on the Scenario instance);
  * `extract(example, result) -> Row` — the tool's stats parsed into row cells;
  * `validate(example, row)   -> Row` — the post step (default: no-op).

Everything else — subprocess isolation (via `aut2ltl.bounded`, the one correct
`timeout` + reap wrapper), the streaming + checkpoint/resume, the summary — is
generic and shared, so a new experiment or probe supplies only its `Scenario`
and never re-implements (or mis-implements) process isolation. This is the base
that ad-hoc probes should build on instead of hand-rolling subprocess plumbing.
"""
from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from aut2ltl import bounded
from survey.example import Example

Row = Dict[str, object]


@dataclass
class Invocation:
    """One tool spawn under `bounded`: the argv, optional stdin, optional cwd."""

    argv: List[str]
    stdin: Optional[str] = None
    cwd: Optional[Path] = None


class Scenario:
    """The pluggable contract. Subclass and override the three plug points;
    `columns` is the CSV schema (`source`, the unique resume key, is always
    appended). `key` defaults to the example's provenance."""

    columns: Sequence[str] = ()

    def key(self, ex: Example) -> str:
        """The unique resume/dedup id for one example (a checkpoint row is
        skipped when its key is already present)."""
        return ex.source or ex.display

    def invoke(self, ex: Example) -> Invocation:
        raise NotImplementedError

    def extract(self, ex: Example, res: "bounded.BoundedResult") -> Row:
        raise NotImplementedError

    def validate(self, ex: Example, row: Row) -> Row:
        """The post step: extra cells derived by re-checking the tool's output
        on an independent path. Default no-op. Returning `{"validation": ...}`
        with the token `FAIL` marks a hard failure the collector counts."""
        return {}

    def summary(self, rows: Sequence[Row]) -> List[str]:
        return [f"collected {len(rows)} rows"]


def collect(examples: Sequence[Example], scenario: Scenario, *,
            csv_path: Path, ckpt_path: Optional[Path] = None, budget: int = 15,
            validate: bool = True, verbose: bool = False,
            progress_every: int = 25) -> Tuple[List[Row], int]:
    """Run every example through the scenario, streaming to a resumable
    checkpoint and a final sorted CSV. Returns `(rows, n_fail)` where `n_fail`
    counts rows whose `validation` cell is `FAIL`.

    Isolation, resume and crash-safety are the collector's job: each run is a
    bounded subprocess, each row is flushed to the checkpoint as it is produced,
    and a re-run skips the keys already checkpointed."""
    cols = list(scenario.columns)
    if "source" not in cols:
        cols.append("source")
    csv_path = Path(csv_path)
    ckpt_path = Path(ckpt_path) if ckpt_path is not None else csv_path.with_suffix(".ckpt")
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    done: Dict[str, Row] = {}
    if ckpt_path.exists():
        with open(ckpt_path, newline="") as fh:
            for r in csv.DictReader(fh):
                done[str(r.get("source", ""))] = r

    examples = list(examples)
    keys = [scenario.key(ex) for ex in examples]
    todo = [(ex, k) for ex, k in zip(examples, keys) if k not in done]
    if verbose:
        print(f"collect: {len(examples)} examples, {len(done)} checkpointed, "
              f"{len(todo)} to run (budget {budget}s)", file=sys.stderr)

    fresh = not ckpt_path.exists()
    with open(ckpt_path, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        if fresh:
            w.writeheader()
            fh.flush()
        for i, (ex, k) in enumerate(todo, 1):
            row: Row = {c: "" for c in cols}
            row["source"] = k
            inv = scenario.invoke(ex)
            res = bounded.run(inv.argv, budget, stdin=inv.stdin, cwd=inv.cwd)
            row.update(scenario.extract(ex, res))
            if validate:
                row.update(scenario.validate(ex, row))
            row["source"] = k
            w.writerow(row)
            fh.flush()
            done[k] = row
            if verbose and i % progress_every == 0:
                print(f"  {i}/{len(todo)}", file=sys.stderr)

    rows = [done[k] for k in keys]
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in sorted(rows, key=lambda r: str(r.get("source", ""))):
            w.writerow({c: r.get(c, "") for c in cols})

    for line in scenario.summary(rows):
        print(line)
    n_fail = sum(1 for r in rows if str(r.get("validation")) == "FAIL")
    return rows, n_fail
