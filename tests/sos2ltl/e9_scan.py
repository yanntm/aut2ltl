"""E9 — scan a `corpus/sos` folder for the gallery's structural strata.

    python3 -m tests.sos2ltl.e9_scan <corpus/sos/DIR> [--out <file.jsonl>]

One streamed JSON record per language, carrying the three structural questions
the E9 gallery asks of the catalogue (`research_notes/sos_toltl_spec.md`):

  * **`peel`** (candidate 1) — every layer a singleton, R-depth ≥ 3, not
    prefix-independent: the `leave` chain and the reach shape both survive.
  * **`live`** (candidate 2) — a final layer that is accepting *and* moving
    *and* (B)-determined, with exits: `STAY∞` is live and a `LEAVE` chain
    appears in the same layer. `GF(aa)` misses this stratum (its moving layers
    are all-rejecting) and `G(a → F b)` misses it the other way (its moving
    accepting layer fails (B) — report F13).
  * **`graded`** (candidate 4) — some layer anchored only at width `k ≥ 2`.

Each is reported with `|𝒞|` so the smallest specimen of a stratum is a sort,
not a hunt. Only languages the engine actually renders can serve as worked
examples, so `rendered` gates every row.

Feed the winners to `tests.sos2ltl.e9_profile` for the full deliverable.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Dict, List, Optional, Set, Tuple

from aut2ltl.sos2ltl import anchoring, engine, windows
from aut2ltl.sos2ltl.cayley import Cayley, build
from aut2ltl.sos2ltl.readoffs import is_prefix_independent
from sosl.sos import Invariant, load_invariant
from sosl.sos.classify.aperiodic import first_group


def _depth(cay: Cayley) -> int:
    """The longest chain of the R-order DAG, in layers."""
    best = [0] * len(cay.layers)
    for i in reversed(range(len(cay.layers))):
        best[i] = 1 + max((best[j] for j in cay.successors[i]), default=0)
    return max(best)


def _moving(la: anchoring.LayerAnchoring) -> bool:
    """A layer with within-layer movement — some letter resets or is mixed.
    A frozen layer's letters are all neutral or exiting."""
    return any(k.startswith("reset") or k == "mixed"
               for k in la.letter_kind.values())


def _accepting(cay: Cayley, i: int, rep: windows.WindowReport,
               lets: "engine._Letters") -> bool:
    """Whether the layer's window term is satisfiable — `STAY∞` can be live."""
    term = engine._window_term(cay, i, rep, lets)
    return term is not None and term != engine._FF


def record(path: str) -> Dict[str, object]:
    with open(path) as f:
        inv: Invariant = load_invariant(f.read())
    key = os.path.basename(path)[:-4]
    row: Dict[str, object] = {"id": key, "classes": inv.n,
                              "aps": len(inv.alphabet.aps)}
    if first_group(inv) is not None:
        row["status"] = "group"
        return row

    cay = build(inv)
    anch = anchoring.analyze(cay)
    lets = engine._Letters(inv)
    pfxind = is_prefix_independent(inv)

    row["status"] = "ok"
    row["layers"] = len(cay.layers)
    row["depth"] = _depth(cay)
    row["prefix_independent"] = pfxind
    row["rendered"] = engine.transcribe(inv) is not None
    row["graded"] = [i for i, la in enumerate(anch)
                     if la.width is not None and la.width >= 2]
    row["a_fail"] = [i for i, la in enumerate(anch) if la.width is None]

    live: List[int] = []
    b_fail: List[int] = []
    for i, la in enumerate(anch):
        rep = windows.analyze_layer(cay, i, k_max=3)
        if rep.status == windows.FAIL:
            b_fail.append(i)
        if rep.status != windows.PASS or len(la.layer) < 2:
            continue
        if not _moving(la) or not any(la.exits[c] for c in la.layer):
            continue
        if _accepting(cay, i, rep, lets):
            live.append(i)
    row["live"] = live
    row["b_fail"] = b_fail
    row["peel"] = (all(len(l) == 1 for l in cay.layers)
                   and row["depth"] >= 3 and not pfxind)
    return row


def main(argv: List[str]) -> int:
    src = argv[0]
    out = argv[argv.index("--out") + 1] if "--out" in argv else \
        "tests/sos2ltl/logs/e9_scan.jsonl"
    paths = sorted(os.path.join(src, f) for f in os.listdir(src)
                   if f.endswith(".sos"))
    with open(out, "w", buffering=1) as sink:
        for p in paths:
            print(json.dumps(record(p)), file=sink)
            sink.flush()
    print(f"{len(paths)} languages -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
