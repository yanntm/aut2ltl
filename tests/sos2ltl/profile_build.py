"""Self-bounded timing/profile of the sos2ltl construction on ONE automaton.

    python3 -m tests.sos2ltl.profile_build <det/one.hoa> [--cap S] [--top N]

Loads a single HOA (the canonical `D` of one language), runs the **bare**
sos2ltl construction (no simplifier) on it under a hard `SIGALRM` wall-clock
cap, and prints the elapsed time plus the cProfile top-`N` by internal time.
The cap makes the probe safe on pathological inputs: a blown cap is printed as
a finding (`BLEW CAP`) and the probe exits, never a runaway. One input per
invocation — do not batch (that defeats the per-example cap).
"""
from __future__ import annotations

import cProfile
import io
import pstats
import signal
import sys
import time
from typing import List


class _Cap(Exception):
    pass


def _alarm(signum: int, frame: object) -> None:
    raise _Cap()


def main(argv: List[str]) -> int:
    if not argv or argv[0].startswith("--"):
        print(__doc__)
        return 2
    hoa = argv[0]
    cap = int(argv[argv.index("--cap") + 1]) if "--cap" in argv else 15
    top = int(argv[argv.index("--top") + 1]) if "--top" in argv else 15

    import spot
    from aut2ltl.language import Language
    from aut2ltl.sos2ltl.translator import sos2ltl as bare

    lang = Language.of(next(iter(spot.automata(hoa))))
    pr = cProfile.Profile()
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(cap)
    t0 = time.time()
    try:
        pr.enable()
        res = bare(lang)
        pr.disable()
        signal.alarm(0)
        dt = time.time() - t0
        verdict = "ok" if getattr(res, "ok", False) else \
            getattr(res, "verdict", type(res).__name__)
        print(f"{hoa}: {dt:.2f}s  -> {verdict}")
    except _Cap:
        pr.disable()
        print(f"{hoa}: BLEW CAP at {cap}s (construction did not finish)")

    s = io.StringIO()
    pstats.Stats(pr, stream=s).sort_stats("tottime").print_stats(top)
    print(s.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
