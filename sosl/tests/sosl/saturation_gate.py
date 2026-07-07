"""M3 saturation gate: with the two-sided sweep on, every census language reaches
its canonical invariant — including the two proven-permanent stalls, which M2
(no saturation) cannot.

    python3 -m tests.sosl.saturation_gate [name ...]

With no arguments runs the whole set; with names runs just those (one HOA source
stem per argument, e.g. ``even``). Default equivalence mode (bounded). Each case:
learn with saturation ON, assert the exported `.sos` is byte-equal to the
reference builder's. The two specimens (`a_implies_xa`, `a_once`) are the sharp
cases — byte-equal ONLY because saturation recovers the left-context class.
"""
from __future__ import annotations

import sys
from typing import List

from sosl.learn import learn
from sosl.sos import dump_invariant
from sosl.sos.build import reference_of_hoa
from sosl.teacher import HoaTeacher

SOURCES = "samples"
CASES = ["gf_aa_parity", "gf_aa_reset", "even", "evenblocks", "a_implies_xa", "a_once"]


def check(name: str) -> None:
    path = f"{SOURCES}/{name}.hoa"
    ref = reference_of_hoa(path)
    t = HoaTeacher.of_hoa(path)
    stats: dict = {}
    learned = learn(t, t.alphabet, stats=stats, saturation=True)
    ok = dump_invariant(learned) == dump_invariant(ref)
    tag = "byte-equal" if ok else "MISMATCH"
    print(f"{name:14s} ref={ref.n} learned={learned.n} "
          f"cex={stats['n_cex']} sat={stats['n_saturation']}  {tag}")
    assert ok, (f"{name}: saturated export not byte-equal to reference\n"
                f"--- learned ---\n{dump_invariant(learned)}\n"
                f"--- reference ---\n{dump_invariant(ref)}")


def main(argv: List[str]) -> int:
    for name in (argv or CASES):
        check(name)
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
