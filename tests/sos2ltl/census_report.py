"""E1/E2 tables from a census JSONL (the `SOS2LTL_CENSUS` side channel).

Reads the per-input records a `--use sos2ltl` survey run appended (one JSON
object per line: `n`, `aperiodic`, `prefix_independent`, and a `layers` list of
per-layer `a_width` / `kinds` / `b_status` / `b_width` / `b_trivial`), restricts
to the LTL specimens (`aperiodic == true`), and prints:

  E1 — condition-(A) anchoring: layer-width histogram, fraction of layers
       anchoring at k=1 and at k<=3, frozen-layer share, per-language full
       stem-transcribability at k<=3, prefix-independence share.
  E2 — condition-(B) windows: over final-candidate layers (non-TRANSIENT), the
       status split and, among conflict-free layers, the smallest passing width
       histogram with the fraction determined at k'<=2 and k'<=3.

    python3 -m tests.sos2ltl.census_report <records.jsonl>
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


def _frozen(layer: Dict[str, Any]) -> bool:
    """A final-candidate layer with no within-layer movement: it has an
    internal cycle (non-TRANSIENT) yet every letter is neutral or exits."""
    kinds = layer["kinds"]
    return (layer["b_status"] != "TRANSIENT"
            and "reset" not in kinds and "mixed" not in kinds)


def _pct(num: int, den: int) -> str:
    return f"{num}/{den} ({100.0 * num / den:.1f}%)" if den else f"{num}/0 (—)"


def main(argv: List[str]) -> int:
    recs = [json.loads(l) for l in Path(argv[0]).read_text().splitlines() if l]
    errors = [r for r in recs if "error" in r]
    ltl = [r for r in recs if r.get("aperiodic") and "error" not in r]
    nonltl = [r for r in recs if not r.get("aperiodic") and "error" not in r]

    print(f"records: {len(recs)}  LTL: {len(ltl)}  non-LTL: {len(nonltl)}"
          f"  errors: {len(errors)}")
    if not ltl:
        print("no LTL specimens — nothing to report")
        return 0

    # --- E1: condition (A) over all layers of LTL specimens ---
    layers = [la for r in ltl for la in r["layers"]]
    awid: Counter = Counter(
        "FAIL" if la["a_width"] is None else la["a_width"] for la in layers)
    frozen = sum(_frozen(la) for la in layers)
    full_k3 = sum(
        all(la["a_width"] is not None and la["a_width"] <= 3 for la in r["layers"])
        for r in ltl)
    pind = sum(bool(r.get("prefix_independent")) for r in ltl)
    at1 = awid.get(1, 0)
    at3 = sum(awid.get(k, 0) for k in (1, 2, 3))

    print("\n=== E1 — anchoring (condition A) ===")
    print(f"layers total: {len(layers)}  (over {len(ltl)} LTL specimens)")
    print(f"  width histogram: {dict(sorted(awid.items(), key=lambda x: str(x[0])))}")
    print(f"  anchor at k=1 : {_pct(at1, len(layers))}")
    print(f"  anchor at k<=3: {_pct(at3, len(layers))}")
    print(f"  frozen layers : {_pct(frozen, len(layers))}")
    print(f"  languages fully stem-transcribable at k<=3: {_pct(full_k3, len(ltl))}")
    print(f"  prefix-independent languages: {_pct(pind, len(ltl))}")

    # --- E2: condition (B) over final-candidate layers ---
    finals = [la for la in layers if la["b_status"] != "TRANSIENT"]
    bstat: Counter = Counter(la["b_status"] for la in finals)
    passes = [la for la in finals if la["b_status"] == "PASS"]
    bwid: Counter = Counter(la["b_width"] for la in passes)
    trivial = sum(bool(la["b_trivial"]) for la in passes)
    # "determined" = a PASS verdict (UNDECIDED is a guard-tripped gap, not a
    # determinacy, even though it carries a conflict-free width).
    det2 = sum(la["b_width"] <= 2 for la in passes)
    det3 = sum(la["b_width"] <= 3 for la in passes)

    print("\n=== E2 — window determinacy (condition B) ===")
    print(f"final-candidate layers: {len(finals)}")
    print(f"  status split : {dict(bstat)}")
    print(f"  PASS width histogram: {dict(sorted(bwid.items(), key=lambda x: str(x[0])))}"
          f"  (trivial {trivial}/{len(passes)})")
    print(f"  determined at k'<=2: {_pct(det2, len(finals))}")
    print(f"  determined at k'<=3: {_pct(det3, len(finals))}")
    if bstat.get("FAIL"):
        print(f"  FAIL layers (witness pairs recorded): {bstat['FAIL']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
