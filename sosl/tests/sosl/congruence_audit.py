"""Audit: is the no-saturation fixpoint a two-sided congruence?

    python3 -m tests.sosl.congruence_audit <case_id> [budget_s]

The normative test (spec §3.2 step 6, paper Lemma 5.2) is the saturation sweep's
**check phase** on the final table — `find_left_divergence`, zero queries — and
it is what `run_case` itself now computes into the `fixpoint_congruent` field;
this probe reports that field. The letter-level test (`mult[c][class(a)]` vs
`step(c, a)`) is REJECTED as a classifier — `rep(class(a))` is always a letter,
so it is vacuous whenever no two letters share a class (it passes the
non-congruent `a_implies_xa` export) — but it is kept here as a *contrast*
column, to show its under-detection against the full check.

One line per case:

    <case> <verdict> congruent=<full check> classes=<n> \
        letter_bad_cells=<k> letter_reachable=<bool>

Expected on exact-ablation runs (Theorem 5.3): `ACCEPTOR_ONLY` ⟺
`congruent=False`, `SOUND` ⟺ `congruent=True`; `letter_bad_cells` may read 0 on
non-congruent cases — that is the rejected test's blind spot, not a conflict.

One case per invocation (the ablation has a slow tail); drive it from a shell
loop.
"""
from __future__ import annotations

import sys
from typing import Dict, List, Optional, Set

import sosl.experiment.run as run_mod
from sosl.experiment.manifest import NOSAT_EXACT, flat_canon_cases
from sosl.experiment.run import Config, run_case
from sosl.learn.partition import Partition


def letter_report(p: Partition) -> Dict[str, int]:
    """The REJECTED letter-level diagnostic, kept for contrast: `bad_cells` =
    the (class, letter) cells where the algebraic product disagrees with the
    partition's own transition; `reached` = classes the product's BFS from ε
    covers. Vacuously clean whenever no two letters share a class."""
    ab = p.table.alphabet
    letters = ab.letters()
    n = p.n
    letter_class = [p.step(p.start, a) for a in letters]
    mult = [[p.fold_from(c, p.rep[d]) for d in range(n)] for c in range(n)]

    bad = 0
    for c in range(n):
        for a_i, a in enumerate(letters):
            if mult[c][letter_class[a_i]] != p.step(c, a):
                bad += 1

    seen: Set[int] = {p.start}
    frontier = [p.start]
    while frontier:
        c = frontier.pop(0)
        for a_i in range(len(letters)):
            d = mult[c][letter_class[a_i]]
            if d not in seen:
                seen.add(d)
                frontier.append(d)
    return {"n": n, "bad_cells": bad, "reached": len(seen)}


def main(argv: List[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    case_id = argv[0]
    budget = int(argv[1]) if len(argv) > 1 else 30
    case = next((c for c in flat_canon_cases() if c.case_id == case_id), None)
    if case is None:
        raise SystemExit(f"no such case: {case_id}")

    cfg = Config(**{**NOSAT_EXACT.__dict__, "budget_seconds": budget})
    # Capture the final partition at the run's own check-phase call, so the
    # contrast diagnostics see exactly the fixpoint the verdict was read from.
    captured: Dict[str, Partition] = {}
    original = run_mod.find_left_divergence

    def spy(table, p):  # type: ignore[no-untyped-def]
        captured["p"] = p
        return original(table, p)

    run_mod.find_left_divergence = spy  # type: ignore[assignment]
    try:
        r = run_case(case.case_id, case.hoa, cfg, reference_sos=case.sos)
    finally:
        run_mod.find_left_divergence = original  # type: ignore[assignment]

    p: Optional[Partition] = captured.get("p")
    if p is None:
        print(f"{case_id} {r.stats.verdict} fixpoint-not-reached")
        return 0
    rep = letter_report(p)
    print(f"{case_id} {r.stats.verdict} "
          f"congruent={r.stats.fixpoint_congruent == 'true'} "
          f"classes={rep['n']} letter_bad_cells={rep['bad_cells']} "
          f"letter_reachable={rep['reached'] == rep['n']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
