"""SoS pairsplit anatomy for one LTL input.

    python3 -m tests.sos2ltl.pairsplit_probe '<ltl formula>'

Prints the split plan (atom counts both sides, chosen side), then per piece:
class count, alphabet, and the engine/dg outcome with wall time — each line
flushed, so an external timeout localizes the hanging piece. Construction
only; no oracle.
"""
from __future__ import annotations

import sys
import time

from aut2ltl.language import Language
from aut2ltl.ltl.metrics import dag_node_count
from aut2ltl.sos2ltl.bridge import invariant_of_language
from aut2ltl.sos2ltl.dg import DgDecline, synthesize
from aut2ltl.sos2ltl.engine import transcribe
from aut2ltl.sos2ltl.pairsplit.decompose import atoms_of, split_plan
from sosl.sos.calculus.surgery import complement
from sosl.sos.calculus.table import Table


def main(phi: str) -> int:
    inv = invariant_of_language(Language.of_ltl(phi))
    table = Table.of(inv)
    p_atoms = atoms_of(table, inv.accept)
    n_atoms = atoms_of(table, complement(table, inv.accept))
    print(f"{phi}: |C|={inv.n} |P atoms|={len(p_atoms)} "
          f"|P̄ atoms|={len(n_atoms)}", flush=True)
    plan = split_plan(inv)
    if plan is None:
        print("  no split (pass-through)")
        return 0
    print(f"  side={'P̄ (negated)' if plan.negate else 'P'} "
          f"pieces={len(plan.pieces)}", flush=True)
    for i, piece in enumerate(plan.pieces):
        print(f"  piece {i}: |C|={piece.n} aps={list(piece.alphabet.aps)}",
              flush=True)
        t0 = time.monotonic()
        phi_f = transcribe(piece, fallback=None)
        dt = time.monotonic() - t0
        if phi_f is not None:
            print(f"    engine: {dt:.2f}s dag={dag_node_count(phi_f)}", flush=True)
            continue
        print(f"    engine: {dt:.2f}s DECLINED -> dg", flush=True)
        t0 = time.monotonic()
        try:
            ast, root, _ = synthesize(piece)
            print(f"    dg: {time.monotonic() - t0:.2f}s ok", flush=True)
        except DgDecline as e:
            print(f"    dg: {time.monotonic() - t0:.2f}s DECLINED ({e})", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
