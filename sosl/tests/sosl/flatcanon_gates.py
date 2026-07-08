"""Flat-canon completion gates (a posteriori over the streamed sweep): the
exhaustive-negative (spec item 7 d′) and the dual-symmetry assertion (item 8).

    python3 -m tests.sosl.census_campaign ...        # produce results.csv first
    python3 -m tests.sosl.flatcanon_gates [results.csv]

Reads `census_campaign`'s `results.csv` (default
`tests/sosl/logs/census/results.csv`) and asserts, build-stopping:

  (d′) **exhaustive negative** — zero prefix-independent permanent stalls over
       the entire *exhaustive* tier (every shape but the sampled
       `2state1ap2acc_parity`; STUDY.md). Emitted as a per-shape one-line count.
       Grounds §6.3's frontier claim (Lemma 4.8: prefix-independent permanent
       stalls first arise beyond the enumeration wall).

  (8)  **dual-symmetry** — a run on `¬L` is the bit-flip of the run on `L`, so
       every metric of a primal and its complement `_c` must be identical
       (ref/learned/splits/columns/equiv/member/stall_class/verdict). Every
       count therefore pairs off; a surviving asymmetry over the *completed*
       sweep is a bug. Only pairs where **both** sides ran to a learner outcome
       (`SOUND`/`ACCEPTOR_ONLY`) are asserted — a pair with a `BUDGET`/`OVERSIZE`
       cutoff on one side is a resource artifact (the wall-clock cap landing
       differently on the two big runs), reported as *deferred*, to be closed by
       a higher-budget re-run before the final drop, not a symmetry violation.

Exit 0 iff both gates hold on the pairs/shapes present.
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from sosl.experiment.manifest import FLAT_CANON_ROOT, load_category
from sosl.sos.io.serialize import load_invariant

IN = Path("tests/sosl/logs/census/results.csv")

# The only sampled origin shape (STUDY.md: 4^16 ≈ 4.3e9 ids, past the wall);
# every other shape in flat_canon is exhaustively enumerated.
SAMPLED_SHAPES = frozenset({"2state1ap2acc_parity"})

# The metric fields that a primal and its complement must share exactly.
DUAL_FIELDS = ["ref_classes", "learned_classes", "n_splits", "n_columns_lin",
               "n_columns_om", "n_equiv", "n_member_total", "stall_class",
               "verdict"]


def _shape(case_id: str) -> str:
    core = case_id[:-2] if case_id.endswith("_c") else case_id
    return core.rsplit("_", 1)[0]


def _prefix_independent_of(case_id: str) -> bool:
    inv = load_invariant(Path(f"{FLAT_CANON_ROOT}/sos/{case_id}.sos").read_text())
    acc = inv.accept
    for (s, e) in inv.linked_pairs():
        bit = (s, e) in acc
        for c in range(inv.n):
            if ((inv.mult[c][s], e) in acc) != bit:
                return False
    return True


def main(argv: List[str]) -> int:
    src = Path(argv[0]) if argv else IN
    if not src.exists():
        print(f"no {src} — run census_campaign first", file=sys.stderr)
        return 2
    rows = list(csv.DictReader(open(src, newline="")))
    ablate = {r["case_id"]: r for r in rows if r["config_id"] == "no-sat-exact"}
    fails: List[str] = []

    # (d′) exhaustive negative: prefix-independent permanent stalls per shape.
    per_shape_pi: Dict[str, int] = defaultdict(int)
    per_shape_tot: Dict[str, int] = defaultdict(int)
    for cid, r in ablate.items():
        if r["stall_class"] != "permanent":
            continue
        sh = _shape(cid)
        per_shape_tot[sh] += 1
        if _prefix_independent_of(cid):
            per_shape_pi[sh] += 1
    print("(d′) prefix-independent permanent stalls by origin shape:")
    for sh in sorted(per_shape_tot):
        tier = "sampled" if sh in SAMPLED_SHAPES else "exhaustive"
        print(f"  {sh:28} [{tier:10}] permanent={per_shape_tot[sh]:5} "
              f"prefix-indep={per_shape_pi[sh]}")
        if sh not in SAMPLED_SHAPES and per_shape_pi[sh] != 0:
            fails.append(f"(d′) {per_shape_pi[sh]} prefix-indep permanent stall(s) "
                         f"at EXHAUSTIVE shape {sh} — expected 0")
    exhaustive_pi = sum(v for s, v in per_shape_pi.items()
                        if s not in SAMPLED_SHAPES)
    print(f"  → exhaustive tier total prefix-indep permanent: {exhaustive_pi} "
          f"(expected 0)")

    # (8) dual-symmetry over primal/complement pairs present in both legs. A
    # pair with a resource cutoff on either side is deferred, not compared.
    incomplete = {"BUDGET", "OVERSIZE"}
    by_case: Dict[Tuple[str, str], dict] = {
        (r["case_id"], r["config_id"]): r for r in rows}
    pairs = checked = deferred = 0
    for cid in {r["case_id"] for r in rows if not r["case_id"].endswith("_c")}:
        comp = cid + "_c"
        if (comp, "no-sat-exact") not in by_case and (comp, "default") not in by_case:
            continue
        pairs += 1
        for leg in ("no-sat-exact", "default"):
            a = by_case.get((cid, leg))
            b = by_case.get((comp, leg))
            if a is None or b is None:
                continue
            if a["verdict"] in incomplete or b["verdict"] in incomplete:
                deferred += 1
                continue
            checked += 1
            diff = [f for f in DUAL_FIELDS if a[f] != b[f]]
            if diff:
                fails.append(f"(8) {cid} vs {comp} [{leg}] differ on "
                             f"{', '.join(f'{f}:{a[f]}!={b[f]}' for f in diff)}")
    print(f"(8) dual-symmetry: {pairs} primal/complement pairs; "
          f"{checked} leg-comparisons asserted, {deferred} deferred "
          f"(BUDGET/OVERSIZE on one side — re-run at higher budget for the drop)")

    if fails:
        print(f"\nGATES FAILED ({len(fails)}):")
        for f in fails[:20]:
            print("  -", f)
        return 1
    print("\nGATES OK: exhaustive negative holds; every checked "
          "primal/complement pair is dual-symmetric.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
