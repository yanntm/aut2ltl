"""Run the syntactic ω-semigroup oracle (`aut2ltl.bls.definability.oracle.decide`)
on ONE HOA file and print the verdict.

Usage:  python3 tests/probes/oracle_probe.py <file.hoa>

Prints one block: the answer (LTL / NOT_LTL / INCONCLUSIVE), the reason, the
serialized witness line when present, and the wall time. Exit code 0 on LTL,
3 on NOT_LTL, 2 on INCONCLUSIVE (mirroring the front end's convention).
"""
from __future__ import annotations

import sys
import time

import spot

from aut2ltl.language import Language
from aut2ltl.bls.definability.oracle import decide, LTL, NOT_LTL


def main(path: str) -> int:
    aut = spot.automaton(path)
    lang = Language.of(aut)
    t0 = time.time()
    v = decide(lang)
    dt = time.time() - t0
    print(f"answer : {v.answer}")
    print(f"reason : {v.reason}")
    if v.witness is not None:
        print(f"witness: {v.witness.serialize()}")
    print(f"time   : {dt:.2f}s")
    if v.answer == LTL:
        return 0
    if v.answer == NOT_LTL:
        return 3
    return 2


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
