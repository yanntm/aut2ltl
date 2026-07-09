"""Smoke test of the C++ core's C1 layer via _core.selftest: primitive
sanity (set algebra, model counts, fixpoint disciplines agreeing) and the
instrumentation stream arriving as parseable JSONL records. Requires the
built extension (cmake -B build && cmake --build build in sos_sdd/)."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sos_sdd import _core  # noqa: E402


def main() -> None:
    records: List[Dict[str, Any]] = []
    res = _core.selftest(lambda line: records.append(json.loads(line)))

    assert res["card_A"] == 5.0, res
    assert res["algebra_ok"], res
    assert res["card_closure"] == 5.0, res
    assert res["rounds"] == 5, res
    assert res["disciplines_agree"], res
    assert "table_peak" in res, res

    evs = [r["ev"] for r in records]
    assert evs[0] == "config" and evs[-1] == "verdict", evs
    ops = [r for r in records if r["ev"] == "op"]
    assert {o["op"] for o in ops} >= {"build-A", "closure-step",
                                      "layered-closure", "saturation-closure"}, evs
    steps = [o for o in ops if o["op"] == "closure-step"]
    assert [s["round"] for s in steps] == list(range(1, res["rounds"] + 1)), steps
    assert all("ms" in o and "table_peak" in o for o in ops)

    print("SUCCESS")


if __name__ == "__main__":
    main()
