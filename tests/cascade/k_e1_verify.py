"""K-E1 conflict triage: ALG-7-verify a raw (C)-conflict on one corpus layer.

    python3 -m tests.cascade.k_e1_verify <id> <layer-id> <k> [budget]

Loads `genaut/corpus/flat_canon/sos/<id>.sos`, resolves `<layer-id>` to its
class set through the Cayley SCC decomposition, and runs the early-exit
conflict finder (`find_c_conflict`) at width `<k>`. On CONFLICT it replays
ALG-7 on the reconstruction: the two loop words share their base and their
recurring edge set; membership of the two lassos is re-checked with
`inv.member` (independent of the closure) and the induced linked pairs are
tested for conjugacy (Lemma C.11). GENUINE = the verdict toggles and the
pairs are non-conjugate; anything else is flagged for inspection.

Exit code: 0 = CONFLICT verified or CLEAN; 2 = BUDGET (nothing established).
"""
from __future__ import annotations

import sys
from typing import List

from aut2ltl.sos2ltl.cayley import build
from sosl.sos import load_invariant
from sosl.sos.classify.aperiodic import is_aperiodic

from tests.cascade.config_machine import find_c_conflict
from tests.cascade.k_e2_transfer import verify_conflict

CORPUS = "genaut/corpus/flat_canon/sos"


def main(argv: List[str]) -> int:
    lang_id, layer_id, k = argv[0], int(argv[1]), int(argv[2])
    budget = int(argv[3]) if len(argv) > 3 else 10 ** 6
    with open(f"{CORPUS}/{lang_id}.sos") as f:
        inv = load_invariant(f.read())
    cay = build(inv)
    R = frozenset(cay.layers[layer_id])
    print(f"# {lang_id} layer {layer_id} R={{{','.join(map(str, sorted(R)))}}} "
          f"k={k} aperiodic={is_aperiodic(inv)} nC={inv.n}")
    con = find_c_conflict(inv, R, k, budget=budget)
    print(f"  find_c_conflict: {con.status} (states={con.states})")
    if con.status != "CONFLICT":
        return 0 if con.status == "CLEAN" else 2
    print(f"  shared recurring edge set |F|={len(con.F)}")
    verify_conflict(inv, con)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
