"""K-E3: one-sidedness statistics and the Cor C.9 guaranteed-Π₂ count.

    python3 -m tests.cascade.k_e3_sweep <census.jsonl> <corpus/sos DIR> [--out CSV]

Over every language whose final layer is (C)-decided at k≤3, classifies the
accepting family among collected F spanning ≥2 classes as
`upward | downward | both | neither` (Cor C.8), and counts the Cor C.9 stratum:
prefix-independent AND terminal, 1-anchored, non-frozen (has anchors) final
layer AND upward-closed AND every parked verdict rejecting — the languages the
draft emits as a bare `Π₂` formula. The draft predicts this count is 0
(prefix-independence forces the final layer frozen); a non-zero count settles
C.3's ⟨TBD⟩ negatively and hands C.9 its first instance.
"""
from __future__ import annotations

import json
import os
import sys
from typing import FrozenSet, List, Optional, Set, Tuple

from aut2ltl.sos2ltl.cayley import build  # noqa: F401 (puts sosl on sys.path)
from aut2ltl.sos2ltl.anchoring import analyze_layer
from aut2ltl.sos2ltl.readoffs import is_prefix_independent
from sosl.sos import load_invariant

from tests.cascade.config_machine import Edge, decide

BUDGET = 120000


def source_classes(F: FrozenSet[Edge]) -> FrozenSet[int]:
    return frozenset(q for (q, _m), _a in F)


def one_sidedness(accepting: Set[FrozenSet[Edge]],
                  collected: Set[FrozenSet[Edge]]) -> str:
    """Classify the accepting family among ≥2-class collected F under ⊆."""
    up = down = True
    coll = list(collected)
    for A in coll:
        for B in coll:
            if A < B:
                if A in accepting and B not in accepting:
                    up = False
                if B in accepting and A not in accepting:
                    down = False
    if up and down:
        return "both"
    if up:
        return "upward"
    if down:
        return "downward"
    return "neither"


def analyze(inv, cay) -> Optional[dict]:
    """Decide the final layer and read off the one-sidedness row; None if the
    layer is not (C)-decided within budget at k≤3."""
    fid = len(cay.layers) - 1
    R = frozenset(cay.layers[fid])
    anc = analyze_layer(cay, fid)
    frozen = all(kd == "neutral" for kd in anc.letter_kind.values())
    has_anchors = any(anc.anchors[q] for q in R)
    terminal = not cay.successors[fid]

    for k in range(4):
        dec = decide(inv, R, k, budget=BUDGET, assert_sc=False)
        if dec.budget:
            return None
        if dec.c_holds:
            break
    else:
        return None
    if not dec.c_holds:
        return None

    multi = {F for F in dec.verdicts if len(source_classes(F)) >= 2}
    accepting = {F for F in multi if dec.verdicts[F] == {True}}
    side = one_sidedness(accepting, multi) if multi else "none(<2cls)"
    return {
        "k": k, "R": len(R), "frozen": frozen, "has_anchors": has_anchors,
        "terminal": terminal, "pfxind": is_prefix_independent(inv),
        "side": side, "n_multi": len(multi), "n_acc": len(accepting),
    }


def main(argv: List[str]) -> int:
    census, sos_dir = argv[0], argv[1].rstrip("/")
    out = argv[argv.index("--out") + 1] if "--out" in argv \
        else "tests/cascade/logs/k_e3.csv"
    ids = [json.loads(l)["id"] for l in open(census) if '"id"' in l]
    os.makedirs(os.path.dirname(out), exist_ok=True)

    from collections import Counter
    side_by_pi: Counter = Counter()
    c9 = []
    n_ok = n_skip = 0
    header = "id,k,R,frozen,has_anchors,terminal,pfxind,side,n_multi,n_acc"
    with open(out, "w") as fh:
        fh.write(header + "\n")
        for lang_id in ids:
            with open(os.path.join(sos_dir, lang_id + ".sos")) as sf:
                inv = load_invariant(sf.read())
            r = analyze(inv, build(inv))
            if r is None:
                n_skip += 1
                continue
            n_ok += 1
            fh.write(f"{lang_id},{r['k']},{r['R']},{int(r['frozen'])},"
                     f"{int(r['has_anchors'])},{int(r['terminal'])},"
                     f"{int(r['pfxind'])},{r['side']},{r['n_multi']},{r['n_acc']}\n")
            side_by_pi[(r["pfxind"], r["frozen"], r["side"])] += 1
            # Cor C.9 gating combo (upward + parked-rejecting refinement deferred
            # to a hit): prefix-independent, terminal, 1-anchored non-frozen.
            if (r["pfxind"] and r["terminal"] and not r["frozen"]
                    and r["has_anchors"] and r["side"] in ("upward", "both")):
                c9.append(lang_id)

    print(f"K-E3: decided {n_ok}, skipped {n_skip} -> {out}")
    print("  side x (pfxind,frozen):")
    for (pi, fr, side), n in sorted(side_by_pi.items()):
        print(f"    pfxind={pi} frozen={fr} {side}: {n}")
    print(f"  Cor C.9 gating stratum (pfxind & terminal & non-frozen anchored "
          f"& upward): {len(c9)}")
    if c9:
        print(f"    FIRST INSTANCES: {c9[:8]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
