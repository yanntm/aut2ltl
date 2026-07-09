"""E10 tables from the branch-factoring ledger, ventilated by Wagner degree.

    python3 -m tests.sos2ltl.e10_report <e10_ledger.jsonl> \
        [--sos-dir genaut/corpus/flat_canon/sos]

The input records are built by `tests.sos2ltl.e10_ledger` over the
`flat_canon/sos` catalogue — one record per distinct language. Prints:

  * the **frame** — catalogue size, the group / decline / rendered cut;
  * the **structure** table: how far classes are finer than residuals on the
    exit fans, and how many fans are single-child (the arcs guard grouping
    turns into a `⊤` guard), per Wagner degree;
  * the **size** table: DAG and flat-tree totals per rendering, and the ratio
    each sharing buys against the `guards` column, per Wagner degree.

Prefix-independent languages are reported on their own line: they have one
residual, so residual indexing degenerates there into the paper's Lemma 5.2
emit-directly rule and their wins are not residual-sharing wins.

The unit throughout is the language (a `flat_canon/sos` file).
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from tests.sos2ltl.cat_sidecar import PHI_LABEL, cat_for, phi_rank

DEFAULT_SOS_DIR = "genaut/corpus/flat_canon/sos"
COLUMNS: Tuple[str, ...] = (
    "plain", "guards", "guards+group", "guards+residual", "all")


def _ratio(num: int, den: int) -> str:
    return f"{num / den:.2f}×" if den else "—"


def _pct(num: int, den: int) -> str:
    return f"{100.0 * num / den:.1f}%" if den else "—"


def _bucket(rows: List[Dict[str, Any]], sos_dir: str
            ) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        cat = cat_for(sos_dir, str(r["id"]))
        out[cat.phi if cat else "?"].append(r)
    return out


def _structure(rows: List[Dict[str, Any]]) -> Tuple[int, ...]:
    fans = sum(int(r["fans"]) for r in rows)
    return (
        len(rows), fans,
        sum(int(r["child_class"]) for r in rows),
        sum(int(r["child_residual"]) for r in rows),
        sum(int(r["one_class"]) for r in rows),
        sum(int(r["one_residual"]) for r in rows),
        sum(int(r["top_guard"]) for r in rows),
        sum(1 for r in rows if r["prefix_independent"]),
        sum(1 for r in rows if r["residuals"] < r["classes"]
            and not r["prefix_independent"]),
    )


def _sizes(rows: List[Dict[str, Any]], field: str) -> Dict[str, int]:
    return {c: sum(int(r["sizes"][c][field]) for r in rows) for c in COLUMNS}


def main(argv: List[str]) -> int:
    path = argv[0]
    sos_dir = argv[argv.index("--sos-dir") + 1] if "--sos-dir" in argv \
        else DEFAULT_SOS_DIR
    with open(path) as f:
        records = [json.loads(line) for line in f if line.strip()]

    group = [r for r in records if r["status"] == "group"]
    decline = [r for r in records if r["status"] == "decline"]
    ok = [r for r in records if r["status"] == "ok"]

    print(f"frame: {len(records)} languages — {len(ok)} rendered by the "
          f"engine, {len(decline)} declined to DG, {len(group)} group "
          f"(non-LTL, no formula)")
    if not ok:
        return 0

    buckets = _bucket(ok, sos_dir)
    order = sorted(buckets, key=phi_rank)

    print("\nstructure (exit fans of the rendered languages)\n")
    head = ("| ϕ | langs | fans | children/class | children/residual | "
            "1-child class | 1-child residual | ⊤-guard | pfxind | finer |")
    print(head)
    print("|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
    for phi in order + ["POOLED"]:
        rows = ok if phi == "POOLED" else buckets[phi]
        n, fans, cc, cr, oc, orr, tg, pi, finer = _structure(rows)
        label = "**POOLED**" if phi == "POOLED" else PHI_LABEL.get(phi, phi)
        print(f"| {label} | {n} | {fans} | {cc} | {cr} | {_pct(oc, fans)} | "
              f"{_pct(orr, fans)} | {tg} | {pi} | {finer} |")

    for field in ("hi_dag", "hi_tree", "dag", "tree"):
        note = ("post-`hi` simplifier — the shipped size"
                if field.startswith("hi_") else "raw label — traceability only")
        print(f"\nsize — {field} nodes ({note}), summed over the row\n")
        print("| ϕ | langs | " + " | ".join(COLUMNS)
              + " | group | residual | both |")
        print("|---|--:|" + "--:|" * (len(COLUMNS) + 3))
        for phi in order + ["POOLED"]:
            rows = ok if phi == "POOLED" else buckets[phi]
            s = _sizes(rows, field)
            label = "**POOLED**" if phi == "POOLED" else PHI_LABEL.get(phi, phi)
            base = s["guards"]
            print(f"| {label} | {len(rows)} | "
                  + " | ".join(str(s[c]) for c in COLUMNS)
                  + f" | {_ratio(base, s['guards+group'])}"
                  + f" | {_ratio(base, s['guards+residual'])}"
                  + f" | {_ratio(base, s['all'])} |")

    print("\nsize by AP count (the guard minimizer is a ≥ 2-AP mechanism: at "
          "1 AP a letter set is a literal or ⊤ and the cube union is already "
          "minimal)\n")
    print("| AP | langs | tree plain | tree guards | guards win | "
          "tree all | all win | hi_dag plain | hi_dag all | hi win |")
    print("|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
    for ap in sorted({int(r["aps"]) for r in ok}):
        rows = [r for r in ok if int(r["aps"]) == ap]
        s = _sizes(rows, "tree")
        h = _sizes(rows, "hi_dag")
        print(f"| {ap} | {len(rows)} | {s['plain']} | {s['guards']} | "
              f"{_ratio(s['plain'], s['guards'])} | {s['all']} | "
              f"{_ratio(s['plain'], s['all'])} | {h['plain']} | {h['all']} | "
              f"{_ratio(h['plain'], h['all'])} |")

    # Every rendering is exactness-preserving, but none is *proven* monotone in
    # size: a sharing can in principle enlarge a formula. Count where it does.
    print("\nmonotonicity — languages where a rendering is larger than the one "
          "it refines\n")
    for field in ("hi_dag", "dag", "tree"):
        for weaker, stronger in (("plain", "guards"),
                                 ("guards", "guards+group"),
                                 ("guards", "guards+residual"),
                                 ("guards+group", "all"),
                                 ("guards+residual", "all")):
            bad = [r["id"] for r in ok
                   if r["sizes"][stronger][field] > r["sizes"][weaker][field]]
            print(f"  {field}: {weaker} → {stronger}: {len(bad)} larger"
                  + (f"  e.g. {bad[:3]}" if bad else ""))

    pi_rows = [r for r in ok if r["prefix_independent"]]
    other = [r for r in ok if not r["prefix_independent"]]
    print("\nresidual indexing, split on prefix-independence "
          "(one residual ⟹ the Lemma 5.2 emit-directly rule, not a memo win)\n")
    print("| stratum | langs | dag guards | dag all | ratio | "
          "hi_dag guards | hi_dag all | hi ratio |")
    print("|---|--:|--:|--:|--:|--:|--:|--:|")
    for name, rows in (("prefix-independent", pi_rows),
                       ("the rest", other)):
        if not rows:
            continue
        s = _sizes(rows, "dag")
        h = _sizes(rows, "hi_dag")
        print(f"| {name} | {len(rows)} | {s['guards']} | {s['all']} | "
              f"{_ratio(s['guards'], s['all'])} | {h['guards']} | {h['all']} | "
              f"{_ratio(h['guards'], h['all'])} |")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
