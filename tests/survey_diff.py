#!/usr/bin/env python3
"""
tests/survey_diff.py — quantitative diff of two survey CSVs (keyed on input).

Reads two CSVs written by `tests/survey.py` and keys both on the INPUT column
`formula` — an LTL formula, or for an HOA input the automaton's file name. The
two runs need NOT cover the same corpus (a grown benchmark, or one run answering
fewer inputs after a timeout), so the report has two stages:

  1. KEY SETS — how many inputs are absent from the left, absent from the right,
     and in common, plus how many each side actually *answered* (built a DAG for).
     This is where a "one file has fewer answers/queries" discrepancy shows up.
  2. COMMON DIFF — everything quantitative (equiv regressions/fixes, technique
     changes, size movers, totals) is computed STRICTLY on the common inputs, so
     a size delta reflects per-input change, not a difference in corpus size.

Worst-news-first; only changed rows are echoed. Run from the project root:
    python3 tests/survey_diff.py LEFT.csv RIGHT.csv
    python3 tests/survey_diff.py LEFT.csv RIGHT.csv --top 5   # fewer sample/mover rows
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

import pandas as pd

KEY = "formula"


def _load(path: str) -> pd.DataFrame:
    """Survey CSV -> DataFrame indexed by the input key (deduped, last wins)."""
    df = pd.read_csv(path, dtype=str).fillna("")
    if KEY not in df.columns:
        sys.exit(f"{path}: no '{KEY}' column — not a survey CSV?")
    return df.drop_duplicates(subset=KEY, keep="last").set_index(KEY)


def _num(s: "pd.Series") -> "pd.Series":
    return pd.to_numeric(s, errors="coerce")


def _answered(df: pd.DataFrame) -> int:
    """Rows with a built DAG (non-blank dag_nodes) = inputs aut2ltl answered."""
    return int(_num(df["dag_nodes"]).notna().sum())


def _pct(old: float, new: float) -> str:
    if old == 0:
        return "n/a" if new == 0 else "+inf"
    return f"{100.0 * (new - old) / old:+.1f}%"


def _print_sample(keys: List[str], cap: int) -> None:
    for k in keys[:cap]:
        print(f"    {k:.70s}")
    if len(keys) > cap:
        print(f"    ... +{len(keys) - cap} more")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Quantitative diff of two survey CSVs, keyed on the input column.")
    ap.add_argument("left")
    ap.add_argument("right")
    ap.add_argument("--top", type=int, default=10, help="max mover / sample rows to show")
    args = ap.parse_args()

    L, R = _load(args.left), _load(args.right)
    lk, rk = set(L.index), set(R.index)
    common = sorted(lk & rk)
    only_left = sorted(lk - rk)
    only_right = sorted(rk - lk)

    # --- stage 1: key sets -------------------------------------------------
    print("=== survey diff (keyed on input) ===")
    print(f"left ={args.left}   {len(lk)} inputs, {_answered(L)} answered")
    print(f"right={args.right}   {len(rk)} inputs, {_answered(R)} answered")
    print(f"key sets: {len(common)} common | "
          f"{len(only_left)} absent-from-right | {len(only_right)} absent-from-left")
    if only_left:
        print(f"  only in left ({len(only_left)}):")
        _print_sample(only_left, args.top)
    if only_right:
        print(f"  only in right ({len(only_right)}):")
        _print_sample(only_right, args.top)
    if not common:
        print("\nno common inputs — nothing to compare.")
        return 0

    # --- stage 2: diff on the common set -----------------------------------
    Lc, Rc = L.loc[common], R.loc[common]
    la, ra = _answered(Lc), _answered(Rc)
    note = "" if la == ra else "   <-- one side answered fewer"
    print(f"\non {len(common)} common inputs: answered  left {la}  right {ra}{note}")

    regressions: List[str] = []
    fixes: List[str] = []
    tech_changes: List[str] = []
    movers: List[Tuple[int, str, str]] = []
    for k in common:
        o, n = Lc.loc[k], Rc.loc[k]
        oe, ne = o.get("equiv", ""), n.get("equiv", "")
        if oe != ne:
            line = f"  {k:30.30s} {oe} -> {ne}"
            if oe == "True" and ne != "True":
                regressions.append(line + ("   *** HARD ***" if ne == "FALSE" else ""))
            elif ne == "True" and oe != "True":
                fixes.append(line)
            else:
                tech_changes.append(line)  # equiv churn that is neither (rare)
        if o.get("technique", "") != n.get("technique", ""):
            tech_changes.append(
                f"  {k:30.30s} {o.get('technique', '-')} -> {n.get('technique', '-')}")
        od, nd = _num(pd.Series([o.get("dag_nodes")]))[0], _num(pd.Series([n.get("dag_nodes")]))[0]
        if pd.notna(od) and pd.notna(nd) and od != nd:
            movers.append((int(abs(nd - od)), k, f"DAG {int(od)} -> {int(nd)} ({_pct(od, nd):>7s})"))

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
        for _, k, detail in movers[: args.top]:
            print(f"  {k:30.30s} {detail}")

    od_dag, nd_dag = _num(Lc["dag_nodes"]).sum(), _num(Rc["dag_nodes"]).sum()
    od_tree, nd_tree = _num(Lc["tree_nodes"]).sum(), _num(Rc["tree_nodes"]).sum()
    print("\ntotals (common set):")
    print(f"DAG nodes : {int(od_dag)} -> {int(nd_dag)}  ({_pct(od_dag, nd_dag)})")
    print(f"tree nodes: {int(od_tree)} -> {int(nd_tree)}  ({_pct(od_tree, nd_tree)})")
    print(f"{len(regressions)} regression(s), {len(fixes)} fix(es), DAG {_pct(od_dag, nd_dag)} "
          f"(on {len(common)} common of {len(lk)}L/{len(rk)}R)")
    return 1 if regressions else 0


if __name__ == "__main__":
    sys.exit(main())
