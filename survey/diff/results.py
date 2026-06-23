"""survey.diff.results — compare two survey RESULT CSVs.

Where ltl_diff compares LANGUAGES, this compares RUNS. Reads two CSVs written by
survey, keys both on the unique `source` column, and reports in two tiers:

  CONSISTENCY (the gate, symmetric — order of the two args does not matter):
    * FAIL    — a run's formula was verified NON-equivalent to its own input.
    * CLASH   — the two runs contradict on one input: one produced an LTL formula,
                the other declared the language NOT_LTL. One of them is unsound.
    Only these set a non-zero exit. (We hold no certificate for NOT_LTL, so a bare
    NOT_LTL is not faulted — but LTL-vs-NOT_LTL between two runs is a red flag.)

  QUANTITATIVE (directional readout, never gates): answered / validated counts,
    validation moves, result + technique changes, size movers and totals. The
    left->right direction is just measurement order, not a verdict of which run
    is the baseline.

Keyed by COLUMN NAME (pandas), so it survives schema reshuffles. Worst-news-first;
only changed rows are echoed.

    python -m survey.diff.results LEFT.csv RIGHT.csv
    python -m survey.diff.results LEFT.csv RIGHT.csv --top 5
"""
from __future__ import annotations

import argparse
import sys
from typing import List, Tuple

import pandas as pd

KEY = "source"  # the unique provenance key every survey CSV carries
NOT_LTL = {"NOT_LTL", "PROBABLY_NOT_LTL"}  # a "no LTL formula exists" verdict


def _load(path: str) -> pd.DataFrame:
    """Survey CSV -> DataFrame indexed by the unique source key (last wins)."""
    df = pd.read_csv(path, dtype=str).fillna("")
    if KEY not in df.columns:
        sys.exit(f"{path}: no '{KEY}' column — not a survey CSV?")
    return df.drop_duplicates(subset=KEY, keep="last").set_index(KEY)


def _num(s: "pd.Series") -> "pd.Series":
    return pd.to_numeric(s, errors="coerce")


def _answered(df: pd.DataFrame) -> int:
    """Rows where aut2ltl produced a formula (result == LTL)."""
    if "result" not in df.columns:
        return 0
    return int((df["result"] == "LTL").sum())


def _validated(df: pd.DataFrame) -> int:
    """Rows the spot oracle confirmed equivalent (validation == TRUE)."""
    if "validation" not in df.columns:
        return 0
    return int((df["validation"] == "TRUE").sum())


def _verified(df: pd.DataFrame) -> bool:
    """Whether this run carries verification verdicts at all (else --no-verify:
    all OFF/empty, so no FAIL/CLASH consistency check is possible)."""
    if "validation" not in df.columns:
        return False
    return bool(df["validation"].isin(["TRUE", "FAIL"]).any())


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
        description="Compare two survey CSVs (consistency gate + quantitative), "
                    "keyed on the source column.")
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
    print("=== survey diff (keyed on source) ===")
    print(f"left ={args.left}   {len(lk)} inputs, "
          f"{_answered(L)} answered, {_validated(L)} validated")
    print(f"right={args.right}   {len(rk)} inputs, "
          f"{_answered(R)} answered, {_validated(R)} validated")
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

    lver, rver = _verified(L), _verified(R)
    if not (lver and rver):
        side = "left" if not lver else "right"
        print(f"\nnote: {side} ran without verification — no FAIL/CLASH gate on it.")

    # --- stage 2: consistency gate (symmetric) -----------------------------
    Lc, Rc = L.loc[common], R.loc[common]
    fails: List[str] = []     # FAIL on either side (verified non-equivalent)
    clashes: List[str] = []   # LTL vs NOT_LTL between the two runs (one unsound)
    val_moves: List[str] = []  # quantitative: validation token changed (no FAIL)
    result_changes: List[str] = []
    tech_changes: List[str] = []
    movers: List[Tuple[int, str, str]] = []
    for k in common:
        o, n = Lc.loc[k], Rc.loc[k]
        ov, nv = o.get("validation", ""), n.get("validation", "")
        orr, nrr = o.get("result", ""), n.get("result", "")
        if ov == "FAIL" or nv == "FAIL":
            fails.append(f"  {k:30.30s} left {ov or '-'} | right {nv or '-'}")
        if (orr == "LTL" and nrr in NOT_LTL) or (nrr == "LTL" and orr in NOT_LTL):
            clashes.append(f"  {k:30.30s} left {orr or '-'} | right {nrr or '-'}")
        if ov != nv and ov != "FAIL" and nv != "FAIL":
            val_moves.append(f"  {k:30.30s} {ov or '-'} -> {nv or '-'}")
        if orr != nrr:
            result_changes.append(f"  {k:30.30s} {orr or '-'} -> {nrr or '-'}")
        if o.get("technique", "") != n.get("technique", ""):
            tech_changes.append(
                f"  {k:30.30s} {o.get('technique', '-') or '-'} -> {n.get('technique', '-') or '-'}")
        od, nd = _num(pd.Series([o.get("dag")]))[0], _num(pd.Series([n.get("dag")]))[0]
        if pd.notna(od) and pd.notna(nd) and od != nd:
            movers.append((int(abs(nd - od)), k, f"DAG {int(od)} -> {int(nd)} ({_pct(od, nd):>7s})"))

    if fails or clashes:
        print(f"\nCONSISTENCY: {len(fails)} FAIL, {len(clashes)} CLASH   <-- UNSOUND")
        if fails:
            print(f"  FAIL — verified non-equivalent ({len(fails)}):")
            print("\n".join(fails[: args.top]))
        if clashes:
            print(f"  CLASH — LTL vs NOT_LTL ({len(clashes)}):")
            print("\n".join(clashes[: args.top]))
    else:
        print("\nCONSISTENCY: OK   (no FAIL, no LTL/NOT_LTL clash)")

    # --- stage 3: quantitative readout (left -> right; never gates) --------
    la, ra = _answered(Lc), _answered(Rc)
    lv, rv = _validated(Lc), _validated(Rc)
    note = "" if la == ra else "   <-- one side answered fewer"
    print(f"\non {len(common)} common: answered {la} -> {ra}{note}; validated {lv} -> {rv}")

    if val_moves:
        print(f"\nvalidation moves ({len(val_moves)}):")
        print("\n".join(val_moves[: args.top]))
        if len(val_moves) > args.top:
            print(f"  ... +{len(val_moves) - args.top} more")
    if result_changes:
        print(f"\nresult changes ({len(result_changes)}):")
        print("\n".join(result_changes[: args.top]))
        if len(result_changes) > args.top:
            print(f"  ... +{len(result_changes) - args.top} more")
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

    od_dag, nd_dag = _num(Lc["dag"]).sum(), _num(Rc["dag"]).sum()
    od_tree, nd_tree = _num(Lc["tree"]).sum(), _num(Rc["tree"]).sum()
    print("\ntotals (common set):")
    print(f"DAG nodes : {int(od_dag)} -> {int(nd_dag)}  ({_pct(od_dag, nd_dag)})")
    print(f"tree nodes: {int(od_tree)} -> {int(nd_tree)}  ({_pct(od_tree, nd_tree)})")
    verdict = "UNSOUND" if (fails or clashes) else "consistent"
    print(f"{verdict}: {len(fails)} FAIL, {len(clashes)} CLASH | "
          f"validated {lv} -> {rv}, DAG {_pct(od_dag, nd_dag)} "
          f"(on {len(common)} common of {len(lk)}L/{len(rk)}R)")
    return 1 if (fails or clashes) else 0


if __name__ == "__main__":
    sys.exit(main())
