"""E1 census (a posteriori): the learner's cost vs the reference class count N,
computed from the streamed sweep — the genaut pattern (sweep now, study later).

    python3 -m tests.sosl.census_e1 [results.csv]

Reads the `default`-config rows of `census_campaign`'s `results.csv` (default:
`tests/sosl/logs/census/results.csv`), joins each language's `.cat` category
(the LTL cut + Wagner degree, from the flat_canon sidecar), and writes a summary
to `tests/sosl/logs/census_e1/summary.md`: the SOUND tally over the whole
catalogue, per-N cost medians with the designed bounds (`splits ≤ N`;
`fill ~ O(N²·|Σ|)`), and — the SoS acceptance-class ventilation — soundness and
cost split by the LTL / non-LTL cut and by Wagner degree.
"""
from __future__ import annotations

import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

from sosl.experiment.manifest import FLAT_CANON_ROOT, load_category

IN = Path("tests/sosl/logs/census/results.csv")
OUT = Path("tests/sosl/logs/census_e1")


def _sos_of(case_id: str) -> str:
    return f"{FLAT_CANON_ROOT}/sos/{case_id}.sos"


def _median(xs: List[float]) -> float:
    return statistics.median(xs) if xs else 0.0


def main(argv: List[str]) -> int:
    src = Path(argv[0]) if argv else IN
    if not src.exists():
        print(f"no {src} — run census_campaign first", file=sys.stderr)
        return 2

    rows: List[dict] = []
    with open(src, newline="") as fh:
        for r in csv.DictReader(fh):
            if r["config_id"] != "default":
                continue
            cat = load_category(_sos_of(r["case_id"]))
            rows.append({
                "case": r["case_id"], "N": int(r["ref_classes"]),
                "splits": int(r["n_splits"]), "fill": int(r["n_member_fill"]),
                "member": int(r["n_member_total"]), "equiv": int(r["n_equiv"]),
                "wall": float(r["wall_seconds"]), "verdict": r["verdict"],
                "ltl": (cat.ltl if cat else None),
                "phi": (cat.phi if cat else "?"),
                "cls": (cat.cls if cat else "?"),
            })
    if not rows:
        print("no default-config rows in results.csv", file=sys.stderr)
        return 2

    bad = [r for r in rows if r["verdict"] != "SOUND"]
    by_n: Dict[int, List[dict]] = defaultdict(list)
    for r in rows:
        by_n[r["N"]].append(r)

    lines = ["# E1 census — learner cost vs N (flat_canon)", ""]
    lines.append(f"{len(rows)} languages of the complement-closed catalogue, "
                 f"**{len(rows) - len(bad)} SOUND** ({len(bad)} non-SOUND). "
                 f"N ∈ [{min(by_n)}, {max(by_n)}].")
    lines.append("")
    lines.append("Per-N cost medians (designed bounds: splits ≤ N; "
                 "fill ~ O(N²·|Σ|)):")
    lines.append("")
    lines.append("| N | languages | median splits | max splits | median fill "
                 "| median member | median equiv |")
    lines.append("|--:|--:|--:|--:|--:|--:|--:|")
    for nval in sorted(by_n):
        grp = by_n[nval]
        sp = [r["splits"] for r in grp]
        lines.append(
            f"| {nval} | {len(grp)} | {statistics.median(sp):.0f} | {max(sp)} "
            f"| {_median([r['fill'] for r in grp]):.0f} "
            f"| {_median([r['member'] for r in grp]):.0f} "
            f"| {_median([r['equiv'] for r in grp]):.0f} |")
    lines.append("")
    over = [r["case"] for r in rows if r["splits"] > r["N"]]
    lines.append(f"**splits ≤ N holds on all {len(rows)} languages: "
                 f"{'yes' if not over else 'NO — ' + str(over[:5])}.**")
    lines.append("")

    # SoS acceptance-class ventilation: the LTL cut and the Wagner degree.
    lines.append("## Ventilation by SoS category")
    lines.append("")
    lines.append("The LTL-definability cut (aperiodicity of 𝓘(L)), soundness and "
                 "median cost on each side:")
    lines.append("")
    lines.append("| definability | languages | SOUND | median N | median splits "
                 "| median member |")
    lines.append("|---|--:|--:|--:|--:|--:|")
    for label, pred in (("LTL (aperiodic)", True), ("non-LTL", False),
                        ("uncategorized", None)):
        grp = [r for r in rows if r["ltl"] is pred]
        if not grp:
            continue
        ok = sum(1 for r in grp if r["verdict"] == "SOUND")
        lines.append(
            f"| {label} | {len(grp)} | {ok} "
            f"| {_median([r['N'] for r in grp]):.0f} "
            f"| {_median([r['splits'] for r in grp]):.0f} "
            f"| {_median([r['member'] for r in grp]):.0f} |")
    lines.append("")
    lines.append("By Wagner degree ϕ = (γ, s):")
    lines.append("")
    lines.append("| ϕ | class | languages | SOUND | median N | median splits |")
    lines.append("|---|---|--:|--:|--:|--:|")
    by_phi: Dict[str, List[dict]] = defaultdict(list)
    for r in rows:
        by_phi[r["phi"]].append(r)
    for phi in sorted(by_phi):
        grp = by_phi[phi]
        ok = sum(1 for r in grp if r["verdict"] == "SOUND")
        cls = grp[0]["cls"]
        lines.append(
            f"| {phi} | {cls} | {len(grp)} | {ok} "
            f"| {_median([r['N'] for r in grp]):.0f} "
            f"| {_median([r['splits'] for r in grp]):.0f} |")
    lines.append("")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"E1 census: {len(rows)} langs, {len(bad)} non-SOUND, "
          f"N in [{min(by_n)}, {max(by_n)}]")
    if bad:
        print("  non-SOUND:", [r["case"] for r in bad[:10]])
    print(f"artifacts: {OUT / 'summary.md'}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
