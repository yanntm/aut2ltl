"""K-E1 shard driver: sweep ONE language's C3-undecided layers (cluster unit).

    python3 -m tests.cascade.k_e1_one <lang_id> [--out CSV]

The per-language unit of the K-E1 sweep, shaped for the cluster contract
(`cluster/README.md`): one command per language, each writing its own CSV —
default `$OARRUN_OUT.csv` when that variable is set — so a `cmds.txt` of
these lines shards the sweep and the reap concatenates the shards into the
K-E1 table. The census record is recomputed in-process (`census_line`), so
no pre-built census file is needed on the executing side. Rows and columns
are exactly `k_e1_sweep`'s (shared `HEADER`); a language with no undecided
layer writes only the header. Regenerate the command list with:

    awk '{print "python3 -m tests.cascade.k_e1_one " $0}' <ids-with-undecided>
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import List

from aut2ltl.sos2ltl.cayley import build
from aut2ltl.sos2ltl.census import census_line
from sosl.sos import load_invariant
from sosl.sos.classify.aperiodic import is_aperiodic

from tests.cascade.config_machine import quotient_letters
from tests.cascade.k_e1_sweep import HEADER, sweep_layer

CORPUS = "genaut/corpus/flat_canon/sos"


def main(argv: List[str]) -> int:
    lang_id = argv[0]
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    elif os.environ.get("OARRUN_OUT"):
        out = os.environ["OARRUN_OUT"] + ".csv"
    else:
        out = f"tests/cascade/logs/k_e1_one_{lang_id}.csv"
    with open(f"{CORPUS}/{lang_id}.sos") as f:
        inv = load_invariant(f.read())
    ap = is_aperiodic(inv)
    rec = json.loads(census_line(inv, ap))
    cay = build(inv)
    n_rows = 0
    with open(out, "w") as fh:
        fh.write(HEADER + "\n")
        for i, lay in enumerate(rec["layers"]):
            if lay.get("b_status") != "UNDECIDED":
                continue
            R = frozenset(cay.layers[i])
            t0 = time.time()
            r = sweep_layer(inv, R, ap)
            dt = time.time() - t0
            m = r["mech"]
            row = [lang_id, i, inv.n, len(R), len(quotient_letters(inv)),
                   int(ap), "UNDECIDED", r["result"], r["pass_k"],
                   *r["per_k"], r["collectedF"], r["max_states"],
                   m["absorption"], m["group"], m["other"], r["other_split"],
                   m["BUG"], f"{dt:.2f}"]
            fh.write(",".join(map(str, row)) + "\n")
            fh.flush()
            n_rows += 1
    print(f"{lang_id}: {n_rows} undecided layer(s) swept -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
