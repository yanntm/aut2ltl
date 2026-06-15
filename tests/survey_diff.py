#!/usr/bin/env python3
"""
tests/survey_diff.py — quantitative diff of two survey CSVs.

Replaces the old `compare_sizes.py` (which parsed survey_sizes log lines). It
reads two CSVs written by `tests/survey.py` (keyed on the `formula` column) and
prints a DENSE, SHORT report meant to be read whole at a glance — only changed
rows, capped mover lists, and a one-line bottom line. It deliberately does NOT
echo unchanged rows (a 35-row corpus would otherwise drown the signal).

What it surfaces, worst-news-first:
  * equiv regressions      — True -> {FALSE, SPOT_TIMEOUT, UNVERIFIED_SIZE, ...}
                             (a True -> FALSE is a HARD regression)
  * equiv fixes            — anything -> True
  * size movers            — the top |Δ DAG nodes| rows (build cost driver)
  * technique changes      — which formulas now take a different portfolio path
  * totals                 — summed DAG / tree nodes old vs new, with % delta

Run from the project root:
    python3 tests/survey_diff.py OLD.csv NEW.csv
    python3 tests/survey_diff.py OLD.csv NEW.csv --top 5   # fewer mover rows
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _load(path: str) -> Dict[str, dict]:
    """formula -> row dict, from a survey CSV."""
    rows: Dict[str, dict] = {}
    with Path(path).open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rows[row["formula"]] = row
    return rows


def _int(row: dict, key: str) -> Optional[int]:
    val = row.get(key, "")
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def _sum(rows: Dict[str, dict], key: str) -> int:
    return sum(v for v in (_int(r, key) for r in rows.values()) if v is not None)


def _pct(old: int, new: int) -> str:
    if old == 0:
        return "n/a" if new == 0 else "+inf"
    return f"{100.0 * (new - old) / old:+.1f}%"


def main() -> int:
    ap = argparse.ArgumentParser(description="Quantitative diff of two survey CSVs.")
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--top", type=int, default=10, help="max size-mover rows to show")
    args = ap.parse_args()

    old, new = _load(args.old), _load(args.new)
    common = [f for f in new if f in old]
    only_new = [f for f in new if f not in old]
    only_old = [f for f in old if f not in new]

    regressions: List[str] = []
    fixes: List[str] = []
    tech_changes: List[str] = []
    movers: List[Tuple[int, str, str]] = []  # (|delta|, formula, detail)
    for f in common:
        o, n = old[f], new[f]
        oe, ne = o.get("equiv", ""), n.get("equiv", "")
        if oe != ne:
            line = f"  {f:30.30s} {oe} -> {ne}"
            if oe == "True" and ne != "True":
                regressions.append(line + ("   *** HARD ***" if ne == "FALSE" else ""))
            elif ne == "True" and oe != "True":
                fixes.append(line)
            else:
                tech_changes.append(line)  # equiv churn that is neither (rare)
        if o.get("technique") != n.get("technique"):
            tech_changes.append(f"  {f:30.30s} {o.get('technique','-')} -> {n.get('technique','-')}")
        od, nd = _int(o, "dag_nodes"), _int(n, "dag_nodes")
        if od is not None and nd is not None and od != nd:
            movers.append((abs(nd - od), f, f"DAG {od} -> {nd} ({_pct(od, nd):>7s})"))

    print("=== survey diff ===")
    print(f"old={args.old}")
    print(f"new={args.new}")
    print(f"matched {len(common)} formulas"
          + (f"; {len(only_new)} only-new; {len(only_old)} only-old" if (only_new or only_old) else ""))

    if regressions:
        print(f"\nEQUIV REGRESSIONS ({len(regressions)}):")
        print("\n".join(regressions))
    if fixes:
        print(f"\nequiv fixes ({len(fixes)}):")
        print("\n".join(fixes))
    if tech_changes:
        print(f"\ntechnique changes ({len(tech_changes)}):")
        print("\n".join(tech_changes[: args.top]))
        if len(tech_changes) > args.top:
            print(f"  ... +{len(tech_changes) - args.top} more")

    movers.sort(reverse=True)
    if movers:
        print(f"\ntop size movers (of {len(movers)} changed):")
        for _, f, detail in movers[: args.top]:
            print(f"  {f:30.30s} {detail}")

    od_dag, nd_dag = _sum(old, "dag_nodes"), _sum(new, "dag_nodes")
    od_tree, nd_tree = _sum(old, "tree_nodes"), _sum(new, "tree_nodes")
    print("\n=== totals (matched + unmatched, per file) ===")
    print(f"DAG nodes : {od_dag} -> {nd_dag}  ({_pct(od_dag, nd_dag)})")
    print(f"tree nodes: {od_tree} -> {nd_tree}  ({_pct(od_tree, nd_tree)})")
    print(f"\nBOTTOM LINE: {len(regressions)} regression(s), {len(fixes)} fix(es), "
          f"DAG {_pct(od_dag, nd_dag)}.")
    return 1 if regressions else 0


if __name__ == "__main__":
    sys.exit(main())
