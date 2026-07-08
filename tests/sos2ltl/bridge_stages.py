"""Per-stage timing of the `Language → 𝓘(L)` bridge on ONE automaton.

    python3 -m tests.sos2ltl.bridge_stages <det/one.hoa> [--cap S]

Times each stage of the bridge separately, under a hard `SIGALRM` cap, and
prints elapsed + automaton/closure sizes as it goes (flushed, so a blown cap
still shows the last stage reached):

  * `det_generic()`          — Spot deterministic generic form (no SAT min);
  * `det_generic_minimal()`  — the above + `spot.sat_minimize` (NP, gated);
  * `invariant_of(canonical(det_generic()))`          — 𝓘(L) the light way;
  * `invariant_of(canonical(det_generic_minimal()))`  — 𝓘(L) the current way.

This isolates whether the survey timeouts are the SAT minimization itself or
the invariant closure on its output, and whether skipping SAT min (which the
invariant does not need — a language property) is both correct and fast.
One input per invocation.
"""
from __future__ import annotations

import signal
import sys
import time
from typing import List


class _Cap(Exception):
    pass


def _alarm(signum: int, frame: object) -> None:
    raise _Cap()


def _t(label: str, fn):  # type: ignore[no-untyped-def]
    t0 = time.time()
    r = fn()
    print(f"  {label:48s} {time.time() - t0:7.2f}s", flush=True)
    return r


def main(argv: List[str]) -> int:
    if not argv or argv[0].startswith("--"):
        print(__doc__)
        return 2
    hoa = argv[0]
    cap = int(argv[argv.index("--cap") + 1]) if "--cap" in argv else 30

    import spot
    import aut2ltl.sos2ltl  # noqa: F401 — puts the sibling `sosl` subtree on sys.path
    from aut2ltl.language import Language
    from sosl.sos.build.importer import canonical
    from sosl.sos.core.quotient import invariant_of

    lang = Language.of(next(iter(spot.automata(hoa))))
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(cap)
    try:
        dg = _t("det_generic()", lambda: lang.det_generic())
        print(f"    det_generic states: {dg.num_states()}", flush=True)
        dm = _t("det_generic_minimal() [+ sat_minimize]",
                lambda: lang.det_generic_minimal())
        print(f"    det_generic_minimal states: {dm.num_states()}", flush=True)
        inv1 = _t("invariant_of(canonical(det_generic))",
                  lambda: invariant_of(canonical(dg), 20000))
        print(f"    𝓘 classes (from det_generic): "
              f"{inv1.n if inv1 else 'DECLINE'}", flush=True)
        inv2 = _t("invariant_of(canonical(det_generic_minimal))",
                  lambda: invariant_of(canonical(dm), 20000))
        print(f"    𝓘 classes (from det_generic_minimal): "
              f"{inv2.n if inv2 else 'DECLINE'}", flush=True)
    except _Cap:
        print(f"  BLEW CAP at {cap}s (see last stage above)", flush=True)
    finally:
        signal.alarm(0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
