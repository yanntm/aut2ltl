"""Regression guard for the fault-verdict routing in the census drivers.

A leaked exception from `run_case` must NOT be banked as the soundness verdict
`FAIL` (spec §7 row F9 reserves that for a run that completed and produced a bad
byte). A run that never completed is routed by kind instead:

  * a leaked `_Budget` (the SIGALRM/finally race) -> ``BUDGET``
  * any other leaked exception                    -> ``CRASH``

This probe drives one `census_campaign` run per injected fault by monkeypatching
`run_case`, and asserts the verdict the driver banks for each.

    python3 -m tests.sosl.fault_verdict_probe

Prints ``OK`` and exits 0 on success; exits 1 on the first wrong verdict.
"""
from __future__ import annotations

import csv
import tempfile
from pathlib import Path
from typing import List

from sosl.experiment.run import _Budget
from tests.sosl import census_campaign


def _run_with_fault(exc: BaseException) -> List[dict]:
    """Run the 1-language census with ``run_case`` forced to raise ``exc``, and
    return the CSV rows the driver banked."""
    def _boom(*_a: object, **_k: object):
        raise exc

    orig = census_campaign.run_case
    census_campaign.run_case = _boom  # type: ignore[assignment]
    try:
        with tempfile.TemporaryDirectory() as tmp:
            census_campaign.main(
                ["--config", "default", "--limit", "1", "--out", tmp])
            with open(Path(tmp) / "results.csv", newline="") as fh:
                return list(csv.DictReader(fh))
    finally:
        census_campaign.run_case = orig  # type: ignore[assignment]


def main() -> int:
    ok = True
    for exc, want in ((_Budget(), "BUDGET"), (ValueError("boom"), "CRASH")):
        rows = _run_with_fault(exc)
        got = rows[0]["verdict"] if rows else "<no row>"
        tag = "ok" if got == want else "FAIL"
        if got != want:
            ok = False
        print(f"  {type(exc).__name__:12s} -> {got:8s} (want {want}) [{tag}]")
    print("OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
