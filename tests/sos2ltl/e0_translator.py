"""End-to-end sos2ltl Translator probe on one HOA input (E0 gate).

    python3 -m tests.sos2ltl.e0_translator <file.hoa> [--expect ok:<formula> | notltl:linear | notltl:omega]

Runs `aut2ltl.sos2ltl.translator.sos2ltl` on the Language of the automaton
and prints the result. ``--expect ok:<f>`` asserts an OK status with a
formula Spot-equivalent to ``<f>``; ``--expect notltl:<shape>`` asserts the
absorbing NOT_LTL verdict with a certified witness of that shape.
"""
from __future__ import annotations

import sys
from typing import List

import spot

from aut2ltl.sos2ltl.translator import sos2ltl
from aut2ltl.language import Language


def main(argv: List[str]) -> int:
    path = argv[0]
    expect = argv[2] if len(argv) > 2 and argv[1] == "--expect" else None

    lang = Language.of(spot.automaton(path))
    res = sos2ltl(lang)
    print(f"{path}: {res.status.value}  techniques={sorted(res.technique)}")
    if res.formula is not None:
        f = str(res.formula)
        print(f"  formula: {f if len(f) < 300 else f[:300] + '...'}")
    if res.diagnosis:
        print(f"  diagnosis: {res.diagnosis}")
    if res.witness is not None:
        print(f"  witness: {res.witness.serialize()}")

    if expect is not None:
        kind, _, arg = expect.partition(":")
        if kind == "ok":
            assert res.ok, res.status
            eq = spot.are_equivalent(res.formula, spot.formula(arg))
            print(f"  equivalent to {arg}: {eq}")
            assert eq, "formula not equivalent to the expectation"
        elif kind == "notltl":
            assert res.status.value == "NOT_LTL", res.status
            assert res.witness is not None and res.witness.complete
            got = "omega" if res.witness.omega_power else "linear"
            assert got == arg, f"witness shape {got}, expected {arg}"
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
