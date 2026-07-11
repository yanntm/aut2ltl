"""K-E1 conflict triage: ALG-7-verify a raw (C)-conflict on one corpus layer.

    python3 -m tests.cascade.k_e1_verify <id> <layer-id> <k> [budget] [--out CSV]

Loads `genaut/corpus/flat_canon/sos/<id>.sos`, resolves `<layer-id>` to its
class set through the Cayley SCC decomposition, and runs the early-exit
conflict finder (`find_c_conflict`) at width `<k>`. On CONFLICT it replays
ALG-7 on the reconstruction: the two loop words share their base and their
recurring edge set; membership of the two lassos is re-checked with
`inv.member` (independent of the closure) and the induced linked pairs are
tested for conjugacy (Lemma C.11). GENUINE = the verdict toggles and the
pairs are non-conjugate.

Beside the printout, one CSV row goes to `--out`, else `$OARRUN_OUT.csv`
when set (the cluster contract: shard with one command per (id, layer),
reap concatenates), else nowhere. Columns:

    id,layer,k,nC,R,sigma,aperiodic,status,states,F,toggles,conjugate,genuine,time_s

`status` is CONFLICT | CLEAN | BUDGET; the ALG-7 columns are blank unless
CONFLICT. Exit code: 0 = CONFLICT verified or CLEAN; 2 = BUDGET.
"""
from __future__ import annotations

import os
import sys
import time
from typing import List, Optional

from aut2ltl.sos2ltl.cayley import build
from sosl.sos import load_invariant
from sosl.sos.classify.aperiodic import is_aperiodic

from tests.cascade.config_machine import find_c_conflict, quotient_letters
from tests.cascade.k_e2_transfer import verify_conflict

CORPUS = "genaut/corpus/flat_canon/sos"
HEADER = ("id,layer,k,nC,R,sigma,aperiodic,status,states,F,"
          "toggles,conjugate,genuine,time_s")


def main(argv: List[str]) -> int:
    out: Optional[str] = None
    if "--out" in argv:
        i = argv.index("--out")
        out = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    elif os.environ.get("OARRUN_OUT"):
        out = os.environ["OARRUN_OUT"] + ".csv"
    lang_id, layer_id, k = argv[0], int(argv[1]), int(argv[2])
    budget = int(argv[3]) if len(argv) > 3 else 10 ** 6
    with open(f"{CORPUS}/{lang_id}.sos") as f:
        inv = load_invariant(f.read())
    ap = is_aperiodic(inv)
    cay = build(inv)
    R = frozenset(cay.layers[layer_id])
    print(f"# {lang_id} layer {layer_id} R={{{','.join(map(str, sorted(R)))}}} "
          f"k={k} aperiodic={ap} nC={inv.n}")
    t0 = time.time()
    con = find_c_conflict(inv, R, k, budget=budget)
    print(f"  find_c_conflict: {con.status} (states={con.states})")
    v = {"m1": "", "m2": "", "conjugate": "", "genuine": ""}
    if con.status == "CONFLICT":
        print(f"  shared recurring edge set |F|={len(con.F)}")
        v = verify_conflict(inv, con)
    if out:
        row = [lang_id, layer_id, k, inv.n, len(R), len(quotient_letters(inv)),
               int(ap), con.status, con.states,
               len(con.F) if con.F is not None else "",
               "" if v["m1"] == "" else int(v["m1"] != v["m2"]),
               "" if v["conjugate"] == "" else int(v["conjugate"]),
               "" if v["genuine"] == "" else int(v["genuine"]),
               f"{time.time() - t0:.2f}"]
        new = not os.path.exists(out)
        with open(out, "a") as fh:
            if new:
                fh.write(HEADER + "\n")
            fh.write(",".join(map(str, row)) + "\n")
    return 0 if con.status != "BUDGET" else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
