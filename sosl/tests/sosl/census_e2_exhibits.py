"""E2 exhibits (a posteriori): the permanent-stall family of the flat catalogue,
read off the streamed sweep, then the sharpest rendered as first-class exhibits.

    python3 -m tests.sosl.census_e2_exhibits [results.csv] [top_k]

Reads the `no-sat-exact` rows of `census_campaign`'s `results.csv` (default:
`tests/sosl/logs/census/results.csv`) — with exact equivalence every surviving
stall (`stall_class == permanent`) is provably permanent. The catalogue is
already language-deduplicated, so every permanent row is a distinct language.
Tabulates the gap (reference − stall) distribution, cross-tabulates the permanent
family by prefix-independence and by the `.cat` SoS category (LTL cut, Wagner
degree), and re-runs just the permanent set live to render the `top_k` sharpest
via the E2 exhibit renderer (coarse fixpoint, canonical fixpoint, separating left
context). Writes `tests/sosl/logs/census_e2/flat_canon.md`.
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from sosl.experiment.driver import run_matrix
from sosl.experiment.manifest import (DEFAULT, NOSAT_EXACT, FLAT_CANON_ROOT,
                                      Case, load_category)
from sosl.experiment.run import RunResult
from sosl.sos.invariant import Invariant
from sosl.sos.io.serialize import load_invariant

IN = Path("tests/sosl/logs/census/results.csv")
OUT = Path("tests/sosl/logs/census_e2")


def _prefix_independent(inv: Invariant) -> bool:
    """Is L prefix-independent? Exactly: acceptance of every linked pair ``(s, e)``
    is invariant under left-multiplication ``s -> c·s`` — membership does not
    depend on the stem."""
    acc = inv.accept
    for (s, e) in inv.linked_pairs():
        bit = (s, e) in acc
        for c in range(inv.n):
            if (((inv.mult[c][s], e) in acc)) != bit:
                return False
    return True


def _paths(case_id: str) -> Tuple[str, str]:
    return (f"{FLAT_CANON_ROOT}/det/{case_id}.hoa",
            f"{FLAT_CANON_ROOT}/sos/{case_id}.sos")


def main(argv: List[str]) -> int:
    args = [a for a in argv]
    src = Path(args[0]) if args and args[0].endswith(".csv") else IN
    args = [a for a in args if not a.endswith(".csv")]
    top_k = int(args[0]) if args else 6
    if not src.exists():
        print(f"no {src} — run census_campaign first", file=sys.stderr)
        return 2

    perms: List[dict] = []
    with open(src, newline="") as fh:
        for r in csv.DictReader(fh):
            if r["config_id"] == "no-sat-exact" and r["stall_class"] == "permanent":
                perms.append({
                    "case": r["case_id"], "ref": int(r["ref_classes"]),
                    "stall": int(r["learned_classes"]),
                    "gap": int(r["ref_classes"]) - int(r["learned_classes"]),
                })
    if not perms:
        print("no permanent stalls in results.csv (ablation leg present?)",
              file=sys.stderr)
        return 0

    gaps: Dict[int, int] = defaultdict(int)
    for r in perms:
        gaps[r["gap"]] += 1

    # per-language structural features + SoS category
    feats = []
    for r in perms:
        hoa, sos = _paths(r["case"])
        inv = load_invariant(Path(sos).read_text())
        cat = load_category(sos)
        feats.append({
            "case": r["case"], "gap": r["gap"],
            "pi": _prefix_independent(inv),
            "ltl": (cat.ltl if cat else None),
            "phi": (cat.phi if cat else "?"),
            "cls": (cat.cls if cat else "?"),
        })

    lines: List[str] = ["# E2 permanent-stall exhibits — flat_canon", ""]
    lines.append(f"**{len(perms)} distinct permanent-stall languages** in the "
                 "complement-closed catalogue — a non-canonical right-congruence "
                 "fixpoint the exact oracle certifies, recovered by saturation.")
    lines.append("")
    lines.append("Gap (reference − stall) distribution:")
    lines.append("")
    lines.append("| gap | " + " | ".join(str(g) for g in sorted(gaps)) + " |")
    lines.append("|---|" + "--:|" * len(gaps))
    lines.append("| languages | "
                 + " | ".join(str(gaps[g]) for g in sorted(gaps)) + " |")
    lines.append("")

    pi_yes = sum(1 for f in feats if f["pi"])
    ltl_yes = sum(1 for f in feats if f["ltl"] is True)
    lines.append(f"Prefix-independent: **{pi_yes}/{len(feats)}**. "
                 f"LTL-definable: **{ltl_yes}/{len(feats)}**.")
    lines.append("")
    lines.append("By Wagner degree ϕ = (γ, s) (× prefix-independence):")
    lines.append("")
    lines.append("| ϕ | class | languages | prefix-indep | LTL | max gap |")
    lines.append("|---|---|--:|--:|--:|--:|")
    by_phi: Dict[str, List[dict]] = defaultdict(list)
    for f in feats:
        by_phi[f["phi"]].append(f)
    for phi in sorted(by_phi):
        grp = by_phi[phi]
        lines.append(
            f"| {phi} | {grp[0]['cls']} | {len(grp)} "
            f"| {sum(1 for f in grp if f['pi'])} "
            f"| {sum(1 for f in grp if f['ltl'] is True)} "
            f"| {max(f['gap'] for f in grp)} |")
    lines.append("")

    # Re-run just the permanent set live (cheap) to render exhibit ledgers.
    sharpest = sorted(perms, key=lambda r: (-r["gap"], r["case"]))[:top_k]
    sharp_cases = [Case(r["case"], _paths(r["case"])[0],
                        sos=_paths(r["case"])[1], tags=("flat_canon",))
                   for r in sharpest]
    matrix = ([(c, DEFAULT) for c in sharp_cases]
              + [(c, NOSAT_EXACT) for c in sharp_cases])
    from sosl.experiment.report import _permanent_exhibit
    campaign = run_matrix(matrix, str(OUT / "sharpest_runs"))
    index: Dict[Tuple[str, str], RunResult] = {
        (r.stats.case_id, r.stats.config_id): r for r in campaign.results}
    lines.append(f"## The {len(sharpest)} sharpest specimens")
    lines.append("")
    for r in sharpest:
        lines.append(_permanent_exhibit(r["case"], index))

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "flat_canon.md").write_text("\n".join(lines), encoding="utf-8")

    gap_kv = " ".join(f"{g}:{gaps[g]}" for g in sorted(gaps))
    print(f"flat_canon E2: {len(perms)} permanent languages; gaps {gap_kv}")
    print(f"  prefix-independent {pi_yes}/{len(feats)}; LTL {ltl_yes}/{len(feats)}")
    for r in sharpest:
        print(f"  {r['case']}: ref={r['ref']} stall={r['stall']} gap={r['gap']}")
    print(f"artifacts: {OUT / 'flat_canon.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
