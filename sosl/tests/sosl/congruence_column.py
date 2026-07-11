"""Grade the `fixpoint_congruent` column of an ablation drop (spec §9 rows P9/P10).

    python3 -m tests.sosl.congruence_column CSV [--out DIR]

The CSV is an exact-ablation leg (`--no-saturation --eq-mode exact`) carrying the
`fixpoint_congruent` field. Three assertions, plus the cross-tab the E2 recount
reads:

  - **P9** (build-stopping): `fixpoint_congruent = false` on every
    `ACCEPTOR_ONLY` row. Theorem 5.3 leaves no other box — an exact-certified
    fixpoint is canonical (hence `SOUND`) or its partition is not a congruence.
    A `true` here convicts the oracle or the fold, not the theorem.
  - **P10** (NOT build-stopping): `fixpoint_congruent = true` on every `SOUND`
    row. Byte-equality out of a non-congruent partition has no known mechanism
    but is not excluded by Theorem 5.3, so a violation is a **theory finding**:
    the case ids are reported and the row is not banked.
  - **dual symmetry**: congruence is complement-invariant (a language and its
    complement share the syntactic congruence — `Invariant.complement` touches
    only `P`), so the two runs of a dual pair must agree. Pairs come from
    `manifest.dual_index` — resolved by language; a dual is never named.

Exit 0 iff P9 and dual symmetry hold and no row is unclassified; P10 violations
are reported and exit 2 (a finding to route to theory, not a build break).
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sosl.experiment.manifest import dual_index

ABLATION_CONFIG = "no-sat-exact"
# The verdicts the column is pinned on. The rest (BUDGET, OVERSIZE) never reach a
# fixpoint, so they carry no congruence claim and must read `n/a`.
PINNED = {"ACCEPTOR_ONLY": "false", "SOUND": "true"}


def _rows(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    ablation = [r for r in rows if r.get("config_id") == ABLATION_CONFIG]
    return ablation or rows


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csv", type=Path, help="the ablation drop's results CSV")
    ap.add_argument("--out", type=Path, default=Path("tests/sosl/logs/congruence"),
                    metavar="DIR", help="where the summary is written")
    args = ap.parse_args(argv)

    rows = _rows(args.csv)
    if not rows:
        print(f"no ablation rows in {args.csv}")
        return 1
    if "fixpoint_congruent" not in rows[0]:
        print(f"{args.csv}: no fixpoint_congruent column — this is not a "
              f"post-item-13 drop")
        return 1

    tab: Counter = Counter((r["verdict"], r["fixpoint_congruent"]) for r in rows)
    p9: List[str] = []      # build-stopping
    p10: List[str] = []     # theory finding
    stray: List[str] = []   # a verdict with no fixpoint carrying a claim
    for r in rows:
        v, c = r["verdict"], r["fixpoint_congruent"]
        want = PINNED.get(v)
        if want is None:
            if c != "n/a":
                stray.append(f"{r['case_id']}: {v} carries "
                             f"fixpoint_congruent={c} (want n/a — no fixpoint)")
        elif c != want:
            (p9 if v == "ACCEPTOR_ONLY" else p10).append(
                f"{r['case_id']}: {v} with fixpoint_congruent={c} (want {want})")

    # Dual symmetry, over pairs resolved by language.
    seen = {r["case_id"]: r["fixpoint_congruent"] for r in rows}
    duals = dual_index()
    asym: List[str] = []
    unpaired = 0
    checked = set()
    for cid, val in seen.items():
        d = duals.get(cid)
        if d is None or d not in seen:
            unpaired += 1
            continue
        if (d, cid) in checked:
            continue
        checked.add((cid, d))
        if seen[d] != val:
            asym.append(f"{cid} ({val}) vs its complement {d} ({seen[d]})")

    lines = ["# Congruence column — P9 / P10 / dual symmetry", "",
             f"source: `{args.csv}`  ({len(rows)} ablation rows)", "",
             "| verdict | fixpoint_congruent | rows |", "|---|---|---|"]
    for (v, c), n in sorted(tab.items()):
        lines.append(f"| {v} | {c} | {n} |")
    lines += ["", f"dual pairs checked: {len(checked)}; "
                  f"rows with no partner in this CSV: {unpaired}", ""]
    for name, bad in (("P9 (build-stopping)", p9), ("P10 (theory finding)", p10),
                      ("dual symmetry", asym), ("unclassified", stray)):
        lines.append(f"- **{name}**: "
                     + ("clean" if not bad else f"{len(bad)} violation(s)"))
        lines += [f"  - {b}" for b in bad[:50]]
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "congruence_column.md").write_text("\n".join(lines) + "\n",
                                                   encoding="utf-8")

    for (v, c), n in sorted(tab.items()):
        print(f"  {v:<15} {c:<6} {n}")
    print(f"dual pairs checked: {len(checked)} (unpaired rows: {unpaired})")
    if stray:
        print(f"UNCLASSIFIED ({len(stray)}):")
        for s in stray[:10]:
            print("  -", s)
    if p9 or asym:
        print("BUILD-STOPPING:")
        for b in p9 + asym:
            print("  -", b)
        return 1
    if stray:
        return 1
    if p10:
        print(f"P10 VIOLATED on {len(p10)} row(s) — byte-equality from a "
              f"non-congruent partition. A theory finding: report the case ids, "
              f"do NOT bank the rows.")
        for b in p10[:20]:
            print("  -", b)
        return 2
    print(f"OK — P9 clean, P10 clean, dual-symmetric over {len(checked)} pairs.")
    print(f"summary: {args.out / 'congruence_column.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
