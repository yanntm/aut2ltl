"""Witness lock (spec §6 E2 recorded-outcome item 7; row P8) — the
prefix-independent permanent-stall witnesses that refute the prefix-dependence
necessity conjecture. Build-stopping assertions:

  (a) prefix-independence on each witness's **canonical** invariant —
      `(s, e) ∈ P ⟺ (c·s, e) ∈ P` for every class `c` and linked pair `(s, e)`;
  (b) the ω-sort column signature (paper Cor. 4.7(b), row P8): every column
      minted in the saturated (default-config) run is of the ω-sort
      (`n_columns_lin == 0`). A single linear mint convicts the predicate or the
      sweep — no third option. Retroactively gates `GF(aa)` and `EvenBlocks`.
  (c) emits full exhibits (coarse + canonical `.sos` + complete split ledger)
      to `tests/sosl/logs/witness_lock/exhibits.md` for the report.

    python3 -m tests.sosl.witness_lock

Exit 0 iff every assertion holds; nonzero (with the offending case) otherwise.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Tuple

from sosl.experiment.manifest import DEFAULT, NOSAT_EXACT, case_by_id
from sosl.experiment.report import _permanent_exhibit
from sosl.experiment.run import RunResult, run_case
from sosl.sos.invariant import Invariant

FC = "../genaut/corpus/flat_canon"
OUT = Path("tests/sosl/logs/witness_lock")

# The refutation witnesses (primals); their complements close each under dual.
WITNESSES: List[str] = [
    "2state1ap2acc_parity_0088836118",
    "2state1ap2acc_parity_1178851077",
]
# Prefix-independent named cases the ω-sort discipline (P8) also gates.
PREFIX_INDEP_NAMED: List[str] = ["gf_aa_parity", "evenblocks"]


def _prefix_independent(inv: Invariant) -> bool:
    """`(s, e) ∈ P ⟺ (c·s, e) ∈ P` for every class `c` and linked pair `(s, e)`:
    acceptance is invariant under left-multiplication, so membership does not
    depend on the stem (the canonical, spec-worded predicate)."""
    acc = inv.accept
    for (s, e) in inv.linked_pairs():
        bit = (s, e) in acc
        for c in range(inv.n):
            if ((inv.mult[c][s], e) in acc) != bit:
                return False
    return True


def _paths(case_id: str) -> Tuple[str, str]:
    return f"{FC}/det/{case_id}.hoa", f"{FC}/sos/{case_id}.sos"


def main(argv: List[str]) -> int:
    fails: List[str] = []
    index: Dict[Tuple[str, str], RunResult] = {}
    witness_ids = [w + suf for w in WITNESSES for suf in ("", "_c")]

    # (a) + (b) on the witnesses, both legs (coarse for the exhibit, saturated
    # for the ω-sort signature and the canonical prefix-independence check).
    for cid in witness_ids:
        hoa, sos = _paths(cid)
        canon = run_case(cid, hoa, DEFAULT, reference_sos=sos)
        coarse = run_case(cid, hoa, NOSAT_EXACT, reference_sos=sos)
        index[(cid, "default")] = canon
        index[(cid, "no-sat-exact")] = coarse
        s = canon.stats
        if s.verdict != "SOUND":
            fails.append(f"{cid}: default verdict {s.verdict} (expected SOUND)")
        if canon.invariant is None or not _prefix_independent(canon.invariant):
            fails.append(f"{cid}: canonical invariant is NOT prefix-independent (a)")
        if s.n_columns_lin != 0:
            fails.append(f"{cid}: {s.n_columns_lin} linear column(s) — ω-sort "
                         f"signature violated (b, row P8)")
        if coarse.stats.stall_class != "permanent":
            fails.append(f"{cid}: ablation stall_class={coarse.stats.stall_class} "
                         f"(expected permanent)")

    # (b) retro-gate: the named prefix-independent cases must be all-ω-sort too.
    for cid in PREFIX_INDEP_NAMED:
        case = case_by_id(cid)
        if case is None:
            fails.append(f"{cid}: not in the named manifest")
            continue
        r = run_case(cid, case.hoa, DEFAULT, reference_sos=case.sos)
        if r.invariant is None or not _prefix_independent(r.invariant):
            fails.append(f"{cid}: canonical invariant not prefix-independent")
        if r.stats.n_columns_lin != 0:
            fails.append(f"{cid}: {r.stats.n_columns_lin} linear column(s) "
                         f"(row P8 — prefix-independent case must be all ω-sort)")

    # (c) exhibits into the report artifact (primals only — complements are the
    # byte-flip and add nothing to read).
    OUT.mkdir(parents=True, exist_ok=True)
    lines = ["# Witness lock — prefix-independent permanent stalls", ""]
    lines.append("The refutation of the prefix-dependence necessity conjecture: "
                 "prefix-independent languages whose right-congruence fixpoint is "
                 "a **certified permanent stall**, recovered only by the "
                 "saturation sweep's ω-power (rotation) columns.")
    lines.append("")
    for w in WITNESSES:
        lines.append(_permanent_exhibit(w, index))
    (OUT / "exhibits.md").write_text("\n".join(lines), encoding="utf-8")

    if fails:
        print("WITNESS LOCK FAILED:")
        for f in fails:
            print("  -", f)
        return 1
    print(f"WITNESS LOCK OK: {len(witness_ids)} witnesses prefix-independent + "
          f"permanent, all ω-sort (0 linear columns); "
          f"{len(PREFIX_INDEP_NAMED)} named cases conform (P8).")
    print(f"exhibits: {OUT / 'exhibits.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
