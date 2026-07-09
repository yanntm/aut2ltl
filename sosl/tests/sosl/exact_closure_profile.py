"""Where does a fired query's closure fallback spend its time — build or scan?

    python3 -m tests.sosl.exact_closure_profile <case_id> [--nosat]

The discriminator theory named for the incremental-reuse question (item 12's
successor). On a fired, non-capped query the closure oracle does two things:

  - **build** — close the monoid of ``(D-profile, H-transformation)`` pairs under
    the letters (`exact._loop_elements`), plus the stem-config BFS. This is where
    `ExactTooLarge` fires, and the `D`-profile factor is *constant across a
    case's successive queries* — only the hypothesis side changes;
  - **scan** — walk ``configs x elements``, comparing the hypothesis's prediction
    against the teacher on each representative lasso.

If build dominates, incremental reuse of the profile monoid across a run's
queries is the lever. If scan dominates, the residue numbers of
`exact_ref_residue` already bound the best case of any cell-level restriction
(18–73%), and the honest conclusion is that the fallback is simply expensive.

Reports one line per fired query, plus the totals over the run.
"""
from __future__ import annotations

import sys
import time
from typing import List, Optional, Tuple

from sosl.contract import Counterexample, EquivResult
from sosl.experiment.manifest import flat_canon_cases
from sosl.learn import learn
from sosl.sos import load_invariant
from sosl.sos.hypothesis import Hypothesis, loop_reps
from sosl.sos.lasso import Lasso
from sosl.teacher import HoaTeacher
from sosl.teacher.equiv import resolve_prediction
from sosl.teacher.exact import ExactTooLarge, _loop_elements, _stem_configs
from sosl.teacher.exact_ref import NotFunctional, exact_ref_counterexample


class Profiler:
    """A teacher proxy that times the closure's two phases on every query the
    functionality guard rejects, then delegates the real answer to the teacher."""

    def __init__(self, teacher: HoaTeacher) -> None:
        self.teacher = teacher
        self.alphabet = teacher.alphabet
        self.rows: List[Tuple[int, int, float, float]] = []

    def member(self, lasso: Lasso) -> bool:
        return self.teacher.member(lasso)

    def _profile(self, h: Hypothesis) -> None:
        t = self.teacher
        letters = t.alphabet.letters()
        t0 = time.perf_counter()
        configs = _stem_configs(h, t._dst, t.init, letters)
        elements = _loop_elements(h, t._dst, t._mark, t.aut.num_states(), letters,
                                  200_000)
        t1 = time.perf_counter()
        loops = loop_reps(h)
        for _cfg, u in configs:
            for _elt, v in elements:
                la = Lasso(u, v)
                resolve_prediction(self.member, h, la, loops) != self.member(la)
        t2 = time.perf_counter()
        self.rows.append((len(configs), len(elements), t1 - t0, t2 - t1))

    def equiv(self, h: Hypothesis) -> EquivResult:
        ref = self.teacher.reference()
        assert ref is not None
        try:
            exact_ref_counterexample(self.member, self.alphabet, h, *ref)
        except NotFunctional:
            try:
                self._profile(h)
            except ExactTooLarge:
                print("  (query capped in build — no scan timing possible)")
        return self.teacher.equiv(h)


def main(argv: List[str]) -> int:
    case_id = argv[1]
    saturation = "--nosat" not in argv
    case = next(c for c in flat_canon_cases() if c.case_id == case_id)
    with open(case.sos, encoding="utf-8") as fh:
        ref = load_invariant(fh.read())

    teacher = HoaTeacher.of_hoa(case.hoa, eq_mode="exact", reference=ref)
    teacher.cap_escape = saturation
    proxy = Profiler(teacher)
    learn(proxy, teacher.alphabet, saturation=saturation)

    leg = "default" if saturation else "no-saturation"
    print(f"{case_id} [{leg}]: reference {ref.n} classes, "
          f"{len(proxy.rows)} fired non-capped queries profiled")
    if not proxy.rows:
        print("  nothing to profile")
        return 0
    tb = ts = 0.0
    for i, (nc, ne, build, scan) in enumerate(proxy.rows, 1):
        tb += build
        ts += scan
        total = build + scan
        print(f"  query {i}: {nc} configs x {ne} elements; "
              f"build {build * 1e3:.1f} ms ({build / total:.0%}), "
              f"scan {scan * 1e3:.1f} ms ({scan / total:.0%})")
    total = tb + ts
    print(f"  totals: build {tb * 1e3:.1f} ms ({tb / total:.0%}), "
          f"scan {ts * 1e3:.1f} ms ({ts / total:.0%})")
    print(f"  => {'BUILD' if tb > ts else 'SCAN'}-dominant: "
          + ("incremental reuse of the profile monoid is the lever"
             if tb > ts else
             "cell-level restriction bounds the win; the fallback is just expensive"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
