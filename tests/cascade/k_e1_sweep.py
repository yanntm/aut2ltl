"""K-E1: (C) on the C3-undecided census stratum, with the K-E7 scan piggybacked.

    python3 -m tests.cascade.k_e1_sweep <census.jsonl> <corpus/sos DIR> [--out CSV] [--limit N]

Reads a census jsonl (`census_build` output), takes every layer C3 left
`UNDECIDED`, and runs the config (C)-decider at widths k=0..3 (stop at first
pass) under a per-width node budget, plus the K-E7 sandwich scan on the same
closures. Writes one CSV row per undecided layer. Each layer is self-bounded by
the budget, so a frozen-layer explosion becomes a BUDGET datum, never a hang.

CSV columns: id, layer, nC, R, sigma, aperiodic, c3_status, result, pass_k,
k0,k1,k2,k3 (P/C/B/-), collectedF, max_states, absorption, group, other, bug, time_s.
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import List, Optional

from aut2ltl.sos2ltl.cayley import build  # noqa: F401  (puts sosl on sys.path)
from sosl.sos import load_invariant
from sosl.sos.classify.aperiodic import is_aperiodic

from tests.cascade.config_machine import decide, quotient_letters
from tests.cascade.sandwich import scan

BUDGET = 150000
WIDTHS = range(4)
HEADER = ("id,layer,nC,R,sigma,aperiodic,c3_status,result,pass_k,"
          "k0,k1,k2,k3,collectedF,max_states,absorption,group,other,"
          "other_split,bug,time_s")


def sweep_layer(inv, R, aperiodic) -> dict:
    """Decide (C) at k=0..3 (stop at first pass) and run the sandwich scan;
    return the row fields."""
    per_k: List[str] = []
    pass_k: Optional[int] = None
    collected = 0
    max_states = 0
    mech = {"absorption": 0, "group": 0, "other": 0, "BUG": 0}
    other_split = 0  # verdict-splitting 'other' — the genuine third-mechanism flag
    for k in WIDTHS:
        dec = decide(inv, R, k, budget=BUDGET, assert_sc=False)
        collected = max(collected, dec.n_collected)
        max_states = max(max_states, dec.max_states)
        fails, _ = scan(inv, dec.closures, aperiodic, dec.entryst)
        for f in fails:
            mech[f.mechanism] = mech.get(f.mechanism, 0) + 1
            if f.mechanism == "other" and f.splits:
                other_split += 1
        if dec.budget:
            per_k.append("B")
        elif dec.c_holds:
            per_k.append("P")
            pass_k = k
            break
        else:
            per_k.append("C")
    while len(per_k) < len(WIDTHS):
        per_k.append("-")

    if pass_k is not None:
        result = f"C@{pass_k}"
    elif "C" in per_k:
        result = "CONFLICT"
    else:
        result = "BUDGET"
    return {
        "result": result, "pass_k": pass_k if pass_k is not None else "",
        "per_k": per_k, "collectedF": collected, "max_states": max_states,
        "mech": mech, "other_split": other_split,
    }


def main(argv: List[str]) -> int:
    census, sos_dir = argv[0], argv[1].rstrip("/")
    out = argv[argv.index("--out") + 1] if "--out" in argv \
        else "tests/cascade/logs/k_e1.csv"
    limit = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else None

    targets = []
    with open(census) as f:
        for line in f:
            rec = json.loads(line)
            if "layers" not in rec:
                continue
            for i, lay in enumerate(rec["layers"]):
                if lay.get("b_status") == "UNDECIDED":
                    targets.append((rec["id"], i))
    if limit:
        targets = targets[:limit]

    header = HEADER
    os.makedirs(os.path.dirname(out), exist_ok=True)
    n_conflict = n_pass = n_budget = n_other = n_split = 0
    with open(out, "w") as fh:
        fh.write(header + "\n")
        for lang_id, layer_id in targets:
            with open(os.path.join(sos_dir, lang_id + ".sos")) as sf:
                inv = load_invariant(sf.read())
            cay = build(inv)
            R = frozenset(cay.layers[layer_id])
            ap = is_aperiodic(inv)
            t0 = time.time()
            r = sweep_layer(inv, R, ap)
            dt = time.time() - t0
            m = r["mech"]
            row = [lang_id, layer_id, inv.n, len(R), len(quotient_letters(inv)),
                   int(ap), "UNDECIDED", r["result"], r["pass_k"],
                   *r["per_k"], r["collectedF"], r["max_states"],
                   m["absorption"], m["group"], m["other"], r["other_split"],
                   m["BUG"], f"{dt:.2f}"]
            fh.write(",".join(map(str, row)) + "\n")
            fh.flush()
            n_pass += r["result"].startswith("C@")
            n_conflict += r["result"] == "CONFLICT"
            n_budget += r["result"] == "BUDGET"
            n_other += m["other"] > 0
            n_split += r["other_split"] > 0

    print(f"K-E1: {len(targets)} undecided layers -> {out}")
    print(f"  pass(C@k)={n_pass}  conflict={n_conflict}  budget={n_budget}")
    print(f"  layers with any 'other' sandwich fail: {n_other}")
    print(f"  layers with verdict-SPLITTING 'other' (third mechanism): {n_split}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
