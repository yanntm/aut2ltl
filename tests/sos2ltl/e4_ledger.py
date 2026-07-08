"""E4(a)-vs-(b) size ledger from two survey CSVs, joined on `source`.

    python3 -m tests.sos2ltl.e4_ledger <sos2ltl.csv> <sos2ltl_dg.csv>

`(a)` is the sos2ltl engine (walk+window, dg fallback, under `hi`); `(b)` is
the raw dg baseline. Both CSVs are keyed by the unique `source` column. Over
the LTL specimens `(a)` decides, reports: engine-vs-dg coverage of `(a)`; the
flat-tree ledger `(a)` vs `(b)` (share with `a_tree <= b_tree`, the largest
`(b)` blow-ups with the engine's size beside them); the DAG-size comparison;
and the FLAT_OVERFLOW population (a `(b)` flat tree Spot cannot materialize).
"""
from __future__ import annotations

import csv
import sys
from typing import Any, Dict, List, Optional

FLAT_OVERFLOW = 10 ** 6  # a flat tree past this is treated as unflattenable


def _int(s: str) -> Optional[int]:
    return int(s) if s not in ("", None) else None


def _index(path: str) -> Dict[str, Dict[str, Any]]:
    return {r["source"]: r for r in csv.DictReader(open(path))}


def _pct(num: int, den: int) -> str:
    return f"{num}/{den} ({100.0 * num / den:.1f}%)" if den else f"{num}/0 (—)"


def main(argv: List[str]) -> int:
    a, b = _index(argv[0]), _index(argv[1])
    ltl = [(s, r) for s, r in a.items() if r["result"] == "LTL"]

    eng = [(s, r) for s, r in ltl if r["technique"].endswith(".engine")]
    dgf = [(s, r) for s, r in ltl if r["technique"].endswith(".dg")]
    print(f"(a) sos2ltl LTL specimens: {len(ltl)}  "
          f"[engine {len(eng)}, dg fallback {len(dgf)}]")

    # Join on source: engine-covered (a) vs the raw dg baseline (b).
    leq = pairs = a_over = b_over = 0
    top: List[Any] = []
    b_missing = 0
    for s, ra in eng:
        rb = b.get(s)
        if rb is None or rb["result"] != "LTL":
            b_missing += 1
            continue
        at, bt = _int(ra["tree"]), _int(rb["tree"])
        ad, bd = _int(ra["dag"]), _int(rb["dag"])
        if at is None or bt is None:
            continue
        pairs += 1
        leq += at <= bt
        a_over += at >= FLAT_OVERFLOW
        b_over += bt >= FLAT_OVERFLOW
        top.append((bt, at, s, ad, bd))

    print("\n=== E4 — flat-tree ledger, engine-covered specimens ===")
    print(f"joined engine/baseline pairs: {pairs}  (b missing/declined: {b_missing})")
    print(f"  a_tree <= b_tree           : {_pct(leq, pairs)}")
    print(f"  (a) FLAT_OVERFLOW (>=1e6)  : {_pct(a_over, pairs)}")
    print(f"  (b) FLAT_OVERFLOW (>=1e6)  : {_pct(b_over, pairs)}")

    top.sort(reverse=True)
    print("\n  largest (b) baseline blow-ups (b_tree | a_tree | a_dag | b_dag):")
    for bt, at, s, ad, bd in top[:8]:
        print(f"    {bt:>18} | {at:>10} | a_dag {ad} | b_dag {bd}  {s.split('/')[-1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
