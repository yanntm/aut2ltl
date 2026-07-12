"""Regression guard for the fault-verdict routing in the census drivers.

`FAIL` is a *soundness* verdict (spec §7 row F9): it is reserved for a run that
completed and produced a bad byte. A run that never completed must be routed by
kind instead, and never banked as FAIL:

  * a run that exhausts its budget            -> ``BUDGET``
  * a run killed at the wall by the OS        -> ``BUDGET`` (a hard kill is a
    budget overrun the run could not report itself)
  * a child that dies any other way           -> ``CRASH``
  * a fault in the parent's own machinery     -> ``CRASH``

    python3 -m tests.sosl.fault_verdict_probe

The sweep runs each case in its own process (`run_case_bounded`), so the
in-process `_Budget` race the old routing guarded is gone: the child owns the
alarm and the parent owns the kill. This probe drives the sweep once per injected
fault — faking the bounded runner's outcome, and faulting the parent — and
asserts the verdict banked for each.

Prints ``OK`` and exits 0 on success; exits 1 on the first wrong verdict.
"""
from __future__ import annotations

import csv
import tempfile
from pathlib import Path
from typing import Callable, List

from aut2ltl.bounded import BoundedResult
from sosl.experiment import run as run_mod
from tests.sosl import census_campaign


def _sweep_rows(tmp: str) -> List[dict]:
    census_campaign.main(["--config", "default", "--limit", "1", "--out", tmp])
    with open(Path(tmp) / "results.csv", newline="") as fh:
        return list(csv.DictReader(fh))


def _with_bounded(fake: Callable[..., BoundedResult]) -> List[dict]:
    """Run the 1-language sweep with the bounded runner's *subprocess* faked, so
    the parent's classification of that outcome is what gets exercised."""
    orig = run_mod.bounded.run
    run_mod.bounded.run = fake  # type: ignore[assignment]
    try:
        with tempfile.TemporaryDirectory() as tmp:
            return _sweep_rows(tmp)
    finally:
        run_mod.bounded.run = orig  # type: ignore[assignment]


def _with_parent_fault(exc: BaseException) -> List[dict]:
    """Run the sweep with `run_case_bounded` itself raising — the parent-side
    guard, which must bank CRASH rather than abort the sweep."""
    def _boom(*_a: object, **_k: object):
        raise exc

    orig = census_campaign.run_case_bounded
    census_campaign.run_case_bounded = _boom  # type: ignore[assignment]
    try:
        with tempfile.TemporaryDirectory() as tmp:
            return _sweep_rows(tmp)
    finally:
        census_campaign.run_case_bounded = orig  # type: ignore[assignment]


def _killed(*_a: object, **_k: object) -> BoundedResult:
    """The child was killed at the wall: no row, no exit code."""
    return BoundedResult(argv=[], rc=None, out="", err="", wall_s=75.0,
                         timed_out=True)


def _died(*_a: object, **_k: object) -> BoundedResult:
    """The child died without printing a row (import error, OOM, signal)."""
    return BoundedResult(argv=[], rc=1, out="", err="ImportError: no spot",
                         wall_s=0.4, timed_out=False)


def main() -> int:
    ok = True
    checks = [
        ("hard kill at the wall", lambda: _with_bounded(_killed), "BUDGET"),
        ("child died (rc!=0)", lambda: _with_bounded(_died), "CRASH"),
        ("parent-side fault", lambda: _with_parent_fault(ValueError("boom")),
         "CRASH"),
    ]
    for name, drive, want in checks:
        rows = drive()
        got = rows[0]["verdict"] if rows else "<no row>"
        if got != want:
            ok = False
        print(f"  {name:24s} -> {got:8s} (want {want}) "
              f"[{'ok' if got == want else 'FAIL'}]")
    print("OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
