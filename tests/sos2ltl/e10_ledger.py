"""E10 branch-factoring ledger — the two sharings priced per language.

    python3 -m tests.sos2ltl.e10_ledger <file.sos | corpus/sos/DIR>
                                        [--out <file.jsonl>]

One JSON record per language (the `.sos` basename is the key, the unit being
the language per §3b). Each record carries the structural counts the sharings
act on — distinct exit children keyed by class vs by residual, the exit fans
whose letters all agree on one child, the `⊤`-guard fans — and the emitted
sizes under five renderings of the same bricks, twice over: `dag`/`tree` on the
raw label, and `hi_dag`/`hi_tree` after the `hi` simplifier the `sos2ltl`
recipe ships (`Simplify(sos2ltl, "hi")`). A size claim is about the `hi_`
columns; the raw ones exist so a small example can be traced back to the
bricks that produced it. Spot rewrites the cosmetic residue (`X GF φ ≡ GF φ`)
on its own — the renderings are there to keep the DAG small enough that it
can, not to finish its job.

The five renderings:

    plain            cube-union guards, one fan arm per letter, class children
    guards           + minimized AP guards (`guards.Guards`, item 0)
    guards+group     + exit fans grouped by child (item 1)
    guards+residual  + exit children keyed by residual (item 2)
    all              both sharings

Every rendering is exact by the label contract, so all five must define the
same language; the survey gate is what checks that, not this probe. A language
outside the engine's stratum records `decline` and no sizes.

Feed the output to `tests.sos2ltl.e10_report`.
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import Dict, List, Optional, Tuple

import spot

from aut2ltl.ltl.builders import _simp_f
from aut2ltl.ltl.metrics import dag_metrics
from aut2ltl.sos2ltl import anchoring
from aut2ltl.sos2ltl.cayley import Cayley, build
from aut2ltl.sos2ltl.engine import Rendering, transcribe
from aut2ltl.sos2ltl.guards import Guards
from aut2ltl.sos2ltl.readoffs import is_prefix_independent, residual_partition
from sosl.sos import Invariant, load_invariant
from sosl.sos.classify.aperiodic import first_group

VARIANTS: Tuple[Tuple[str, Rendering], ...] = (
    ("plain", Rendering(guards=False, group=False, residual=False)),
    ("guards", Rendering(guards=True, group=False, residual=False)),
    ("guards+group", Rendering(guards=True, group=True, residual=False)),
    ("guards+residual", Rendering(guards=True, group=False, residual=True)),
    ("all", Rendering(guards=True, group=True, residual=True)),
)


def _fan_counts(inv: Invariant, cay: Cayley) -> Dict[str, int]:
    """The structure the sharings exploit, counted over the exit fans of every
    class: how many distinct children each fan sees when its arrows are keyed
    by target class and when they are keyed by target residual, how many fans
    collapse to a single child either way, and how many of those single-child
    fans carry a `⊤` guard (every letter of the alphabet exits to it)."""
    residual = residual_partition(inv)
    guards = Guards(inv.alphabet)
    anch = anchoring.analyze(cay)
    out = dict(fans=0, child_class=0, child_residual=0,
               one_class=0, one_residual=0, top_guard=0)
    for la in anch:
        for c in la.layer:
            exits = la.exits[c]
            if not exits:
                continue
            targets = {cay.step(c, a) for a in exits}
            residuals = {residual[d] for d in targets}
            out["fans"] += 1
            out["child_class"] += len(targets)
            out["child_residual"] += len(residuals)
            out["one_class"] += len(targets) == 1
            out["one_residual"] += len(residuals) == 1
            out["top_guard"] += (len(residuals) == 1
                                 and guards.render(exits).is_tt())
    return out


def _trailer_residuals(text: str) -> Optional[int]:
    """The residual count of the `.sos` file's optional residuals trailer —
    computed on the automaton side, dropped by the loader. Cross-checks the
    `P`-derived `residual_partition` on every input that carries one; a
    mismatch is a stop-the-line bug in one of the two computations."""
    for line in text.splitlines():
        if line.startswith("residuals:"):
            return int(line.split(":", 1)[1])
    return None


def record(path: str) -> Dict[str, object]:
    """The ledger line of one `.sos` file."""
    with open(path) as f:
        text = f.read()
    inv = load_invariant(text)
    key = os.path.basename(path)[:-4]

    blocks = len(set(residual_partition(inv)))
    trailer = _trailer_residuals(text)
    assert trailer is None or trailer == blocks, (
        f"{key}: residuals trailer says {trailer}, P says {blocks}")
    row: Dict[str, object] = {
        "id": key,
        "classes": inv.n,
        "aps": len(inv.alphabet.aps),
        "residuals": blocks,
        "prefix_independent": is_prefix_independent(inv),
    }
    if first_group(inv) is not None:
        row["status"] = "group"          # non-LTL: no formula to render
        return row

    cay = build(inv)
    row["layers"] = len(cay.layers)
    row.update(_fan_counts(inv, cay))

    sizes: Dict[str, object] = {}
    for name, rend in VARIANTS:
        t0 = time.time()
        phi: Optional["spot.formula"] = transcribe(inv, rend=rend)
        if phi is None:
            row["status"] = "decline"
            return row
        m = dag_metrics(phi)
        # The shipped size: the `sos2ltl` recipe is `Simplify(sos2ltl, "hi")`,
        # so the raw label is a traceability artefact and the post-simplifier
        # DAG is what a size claim is about.
        hi = dag_metrics(_simp_f(phi))
        sizes[name] = {"dag": m.dag_nodes, "tree": m.tree_nodes,
                       "temporals": m.temporal_nodes,
                       "hi_dag": hi.dag_nodes, "hi_tree": hi.tree_nodes,
                       "hi_temporals": hi.temporal_nodes,
                       "s": round(time.time() - t0, 3)}
    row["status"] = "ok"
    row["sizes"] = sizes
    return row


def main(argv: List[str]) -> int:
    src = argv[0]
    out = argv[argv.index("--out") + 1] if "--out" in argv else None
    if os.path.isdir(src):
        paths = sorted(os.path.join(src, f) for f in os.listdir(src)
                       if f.endswith(".sos"))
        if out is None:
            out = "tests/sos2ltl/logs/e10_ledger.jsonl"
    else:
        paths = [src]

    # Line-buffered and flushed per language: a blown cap leaves every record
    # computed so far on disk, as with the other census ledgers.
    sink = open(out, "w", buffering=1) if out else sys.stdout
    done = 0
    try:
        for p in paths:
            print(json.dumps(record(p)), file=sink)
            sink.flush()
            done += 1
    finally:
        if out:
            sink.close()
            print(f"{done}/{len(paths)} languages -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
