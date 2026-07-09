"""C4 engine probe on one `.sos` invariant (E0 gate, M2).

    python3 -m tests.sos2ltl.e0_engine <file.sos> [--expect <ltl>|decline]

Transcribes the invariant on the flat-brick stratum and runs the
conformance gate of `research_notes/sos_toltl_experiments.md` §3: the
reference invariant of the emitted formula must be byte-equal to the
input. With ``--expect <ltl>`` additionally asserts Spot-equivalence to
the expected formula; ``--expect decline`` asserts the stratum
precondition fails (transcribe returns None).
"""
from __future__ import annotations

import sys
from typing import List, Optional

from aut2ltl.ltl.metrics import dag_metrics
from aut2ltl.sos2ltl.engine import transcribe
from sosl.sos import dump_invariant, load_invariant
from sosl.sos.build.importer import import_ltl
from sosl.sos.core.quotient import invariant_of


def main(argv: List[str]) -> int:
    path = argv[0]
    expect = argv[2] if len(argv) > 2 and argv[1] == "--expect" else None
    with open(path) as f:
        inv = load_invariant(f.read())

    phi: Optional["spot.formula"] = transcribe(inv)
    if phi is None:
        print(f"{path}: DECLINE (outside the flat-brick stratum)")
        assert expect in (None, "decline"), expect
        print("OK")
        return 0
    assert expect != "decline", f"expected decline, got a formula: {phi}"

    m = dag_metrics(phi)
    print(f"{path}: DAG {m.dag_nodes} / tree {m.tree_nodes}")
    flat = str(phi)
    print(f"  formula: {flat if len(flat) < 500 else flat[:500] + '...'}")

    conf = invariant_of(import_ltl(flat))
    assert conf is not None, "conformance rebuild blew its cap"
    assert dump_invariant(conf) == dump_invariant(inv), \
        "CONFORMANCE FAILURE: I(L(phi)) differs from the input invariant"
    print("  conformance: I(L(phi)) byte-equal to input")

    if expect is not None:
        import spot
        eq = spot.are_equivalent(phi, spot.formula(expect))
        print(f"  equivalent to {expect}: {eq}")
        assert eq
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
