"""E9 — the worked-example deliverable for one specimen.

    python3 -m tests.sos2ltl.e9_profile <file.sos>
    python3 -m tests.sos2ltl.e9_profile <file.hoa>
    python3 -m tests.sos2ltl.e9_profile --ltl "G(a -> F b)"
    python3 -m tests.sos2ltl.e9_profile ... [--json] [--no-stack]

Prints the tuple `research_notes/sos_toltl_spec.md` E9 asks of every
candidate: the `.sos` id or source, `|𝒞|`, the layer list with `|R|` and entry
classes, letter-kind tables, (A)/(B) widths per layer, the ladder rung,
prefix-independence, the emitted DAG size, and the emitted label stack (raw)
beside the Spot-simplified formula.

Every specimen is keyed by its canonical invariant, whatever seeded it: a
`.sos` loads directly, an automaton or an LTL formula goes through the bridge
(`canonical` determinizes and completes, then the reference closure), so two
presentations of one language profile identically.

The label stack is the engine's own `SOS2LTL_TRACE` dump, captured here — the
bricks are never re-assembled probe-side, since a copy would drift from the
engine and the figure it feeds would stop being checkable.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
from typing import Dict, List, Optional, Tuple

import spot

from aut2ltl.ltl.builders import _simp_f
from aut2ltl.ltl.metrics import dag_metrics
from aut2ltl.sos2ltl import anchoring, engine, windows
from aut2ltl.sos2ltl.cayley import Cayley, build
from aut2ltl.sos2ltl.guards import Guards
from aut2ltl.sos2ltl.readoffs import is_prefix_independent, residual_partition
from sosl.sos import Invariant, load_invariant
from sosl.sos.classify import classify


def _invariant_of(src: str, is_ltl: bool) -> Tuple[Invariant, str]:
    """The canonical invariant of the specimen, and a label for its source."""
    if is_ltl:
        from aut2ltl.language import Language
        from aut2ltl.sos2ltl.bridge import invariant_of_language
        return invariant_of_language(Language.of_ltl(src)), f"ltl:{src}"
    if src.endswith(".sos"):
        with open(src) as f:
            return load_invariant(f.read()), os.path.basename(src)[:-4]
    from aut2ltl.language import Language
    from aut2ltl.sos2ltl.bridge import invariant_of_language
    return invariant_of_language(Language.of(spot.automaton(src))), src


def _entries(cay: Cayley, layer_id: int) -> List[int]:
    """The classes of layer `layer_id` reachable from outside it — where a walk
    can enter. The root layer is entered at the identity."""
    inv = cay.inv
    layer = set(cay.layers[layer_id])
    if layer_id == 0:
        return [inv.identity]
    hit = {d for c in range(inv.n) if c not in layer
           for a in inv.alphabet.letters()
           for d in [cay.step(c, a)] if d in layer}
    return sorted(hit)


def _layer_rows(inv: Invariant, cay: Cayley) -> List[Dict[str, object]]:
    anch = anchoring.analyze(cay)
    lets = Guards(inv.alphabet)
    rows: List[Dict[str, object]] = []
    for i, la in enumerate(anch):
        rep = windows.analyze_layer(cay, i, k_max=3)
        rows.append({
            "layer": i,
            "classes": list(la.layer),
            "size": len(la.layer),
            "entries": _entries(cay, i),
            "kinds": {str(lets.cube(a)): k
                      for a, k in sorted(la.letter_kind.items())},
            "a_width": la.width,
            "b_status": rep.status,
            "b_width": rep.width,
            "b_trivial": rep.trivial,
            "successors": list(cay.successors[i]),
        })
    return rows


def _stack(inv: Invariant) -> Tuple[Optional["spot.formula"], List[str]]:
    """The engine's root label and its brick dump, via the engine's own trace
    hook (`SOS2LTL_TRACE`), captured off stderr."""
    buf = io.StringIO()
    saved = engine._TRACE
    engine._TRACE = True
    try:
        with contextlib.redirect_stderr(buf):
            phi = engine.transcribe(inv)
    finally:
        engine._TRACE = saved
    return phi, [l for l in buf.getvalue().splitlines() if l.startswith("[engine]")]


def profile(src: str, is_ltl: bool, want_stack: bool = True
            ) -> Dict[str, object]:
    inv, name = _invariant_of(src, is_ltl)
    cay = build(inv)
    rec = classify(inv)
    rungs = rec.rungs

    row: Dict[str, object] = {
        "id": name,
        "classes": inv.n,
        "aps": list(inv.alphabet.aps),
        "aperiodic": rec.aperiodic,
        "phi": f"({rec.phi[0]}, {rec.phi[1]})",
        "rungs": [n for n in ("open", "closed", "weak", "dba", "dca")
                  if getattr(rungs, n)],
        "prefix_independent": is_prefix_independent(inv),
        "residuals": len(set(residual_partition(inv))),
        "layers": _layer_rows(inv, cay),
    }
    if not rec.aperiodic:
        row["engine"] = "group (non-LTL)"
        return row

    phi, lines = _stack(inv) if want_stack else (engine.transcribe(inv), [])
    if phi is None:
        row["engine"] = "decline (outside the flat-brick stratum)"
        return row
    m = dag_metrics(phi)
    hi = _simp_f(phi)
    hm = dag_metrics(hi)
    row["engine"] = {
        "dag": m.dag_nodes, "tree": m.tree_nodes, "temporals": m.temporal_nodes,
        "hi_dag": hm.dag_nodes, "hi_tree": hm.tree_nodes,
        "raw": str(phi), "simplified": str(hi),
    }
    if want_stack:
        row["stack"] = lines
    return row


def _print(row: Dict[str, object]) -> None:
    print(f"=== {row['id']}")
    print(f"  |𝒞| = {row['classes']}   AP = {row['aps']}   "
          f"φ = {row['phi']}   rungs = {row['rungs'] or '—'}")
    print(f"  aperiodic = {row['aperiodic']}   prefix-independent = "
          f"{row['prefix_independent']}   residuals = {row['residuals']}")
    print(f"  layers ({len(row['layers'])}), R-order top to bottom:")
    for la in row["layers"]:            # type: ignore[union-attr]
        b = la["b_status"]
        if la["b_trivial"]:
            b += " (trivial)"
        elif la["b_width"] is not None:
            b += f" k'={la['b_width']}"
        print(f"    L{la['layer']}: R={la['classes']} |R|={la['size']} "
              f"entries={la['entries']} A-width={la['a_width']} B={b} "
              f"→ {la['successors'] or '·'}")
        print(f"         kinds: {la['kinds']}")
    eng = row["engine"]
    if isinstance(eng, str):
        print(f"  engine: {eng}")
        return
    print(f"  engine: DAG {eng['dag']} / tree {eng['tree']} "
          f"→ hi DAG {eng['hi_dag']} / tree {eng['hi_tree']}")
    print(f"    raw        : {eng['raw']}")
    print(f"    simplified : {eng['simplified']}")
    if "stack" in row:
        print("  label stack (engine bricks, simplification off):")
        for line in row["stack"]:       # type: ignore[union-attr]
            print("    " + line)


def main(argv: List[str]) -> int:
    is_ltl = "--ltl" in argv
    src = argv[argv.index("--ltl") + 1] if is_ltl else argv[0]
    if "--dump-sos" in argv:
        # The canonical invariant of a specimen seeded by an automaton or a
        # formula — E9 asks every candidate to be keyed by its `.sos`.
        from sosl.sos import dump_invariant
        inv, _ = _invariant_of(src, is_ltl)
        out = argv[argv.index("--dump-sos") + 1]
        with open(out, "w") as f:
            f.write(dump_invariant(inv))
        print(f"wrote {out}")
    row = profile(src, is_ltl, want_stack="--no-stack" not in argv)
    if "--json" in argv:
        print(json.dumps(row))
    else:
        _print(row)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
