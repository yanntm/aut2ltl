"""Audit: is the no-saturation fixpoint a congruence for the algebraic product?

    python3 -m tests.sosl.congruence_audit <case_id>

`export` reads the raw algebra off the partition as `mult[c][d] = fold(c, rep(d))`
— folding by a *representative* of `d`. That is only well defined if the partition
is a congruence for the product, i.e. `mult[c][class(a)] == step(c, a)` for every
class `c` and letter `a`. Saturation is what forces this; the ablation
(`--no-saturation`) turns it off.

When the partition is not a congruence, two things can happen, and only one of them
is loud:

  * the product's BFS from ε misses classes -> `canonicalize` asserts (a CRASH);
  * the BFS still covers every class -> **no assertion fires**, and `canonicalize`
    returns an invariant read off an ill-defined multiplication — a silently wrong
    algebra, scored `ACCEPTOR_ONLY` as though export merely byte-differed.

This prints one line per case so a sample can be swept for the silent kind:

    <case> <verdict> congruent=<bool> reachable=<bool> classes=<n> bad_cells=<k>

One case per invocation (the ablation has a slow tail); drive it from a shell loop.
"""
from __future__ import annotations

import sys
from typing import Dict, List, Optional, Set

import sosl.experiment.run as run_mod
from sosl.experiment.manifest import NOSAT_EXACT, flat_canon_cases
from sosl.experiment.run import Config, run_case
from sosl.learn.partition import Partition


def congruence_report(p: Partition) -> Dict[str, int]:
    """`bad_cells` = the (class, letter) cells where the algebraic product disagrees
    with the partition's own transition; `reached` = classes the product's BFS from
    ε covers. A congruence has `bad_cells == 0`, and then `reached == n`."""
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
    captured: Dict[str, Partition] = {}
    original = run_mod.export

    def spy(p: Partition, member):  # type: ignore[no-untyped-def]
        captured["p"] = p
        return original(p, member)

    run_mod.export = spy  # type: ignore[assignment]
    try:
        r = run_case(case.case_id, case.hoa, cfg, reference_sos=case.sos)
    finally:
        run_mod.export = original  # type: ignore[assignment]

    p: Optional[Partition] = captured.get("p")
    if p is None:
        print(f"{case_id} {r.stats.verdict} export-not-reached")
        return 0
    rep = congruence_report(p)
    congruent = rep["bad_cells"] == 0
    reachable = rep["reached"] == rep["n"]
    print(f"{case_id} {r.stats.verdict} congruent={congruent} "
          f"reachable={reachable} classes={rep['n']} bad_cells={rep['bad_cells']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
