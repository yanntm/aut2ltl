"""Diagnose `raw algebra has classes unreachable from eps` (canonical.py assertion).

    python3 -m tests.sosl.crash_unreachable <case_id> [budget_s] [--sat]

Runs one language under the ablation config (`--no-saturation --eq-mode exact`),
intercepting `export` to capture the partition it is about to canonicalize, and
reports:

  * which classes the shortlex BFS from ε reaches through the *algebraic* product
    `mult[c][letter_class[a]]` — the map `canonicalize` re-keys by — and which it
    misses;
  * where that product disagrees with the learner's own transition `step(c, a)`,
    which is the reason a class can go unreachable: `mult[c][d] = fold(c, rep(d))`
    folds by the *representative* of `d`, so the two agree only if the partition is
    a congruence for the product.

`--sat` reruns the same language with saturation on, for contrast. One case per
invocation, by design.
"""
from __future__ import annotations

import sys
from typing import Dict, List, Optional, Set, Tuple

import sosl.experiment.run as run_mod
from sosl.experiment.manifest import DEFAULT, NOSAT_EXACT, flat_canon_cases
from sosl.experiment.run import Config, run_case
from sosl.learn.partition import Partition


def _find(case_id: str):
    for c in flat_canon_cases():
        if c.case_id == case_id:
            return c
    raise SystemExit(f"no such case: {case_id}")


def _analyse(p: Partition) -> None:
    """Print the reachability + congruence diagnosis of the partition's raw algebra."""
    ab = p.table.alphabet
    letters = ab.letters()
    n = p.n

    letter_class = [p.step(p.start, a) for a in letters]
    mult = [[p.fold_from(c, p.rep[d]) for d in range(n)] for c in range(n)]

    # The BFS canonicalize runs: from ε, multiply by each letter's *class*.
    seen: Set[int] = {p.start}
    frontier = [p.start]
    while frontier:
        c = frontier.pop(0)
        for a_i, _a in enumerate(letters):
            d = mult[c][letter_class[a_i]]
            if d not in seen:
                seen.add(d)
                frontier.append(d)

    missing = sorted(set(range(n)) - seen)
    print(f"classes: {n} | reached from eps via mult: {len(seen)} | "
          f"UNREACHABLE: {len(missing)} {missing}")

    # Where the algebraic product and the learner's transition disagree.
    bad: List[Tuple[int, str, int, int]] = []
    for c in range(n):
        for a_i, a in enumerate(letters):
            via_mult = mult[c][letter_class[a_i]]
            via_step = p.step(c, a)
            if via_mult != via_step:
                bad.append((c, str(a), via_step, via_mult))
    print(f"product vs transition: {len(bad)} disagreement(s) "
          f"of {n * len(letters)} (c, a) cells"
          + (" -- the partition is NOT a congruence for the product" if bad else ""))
    for c, a, st, mu in bad[:12]:
        print(f"    class {c} . {a}:  step -> {st}   but  mult[c][class(a)] -> {mu}")

    # Are the unreachable classes reachable by `step`? (i.e. the learner can name them)
    if missing:
        seen_step: Set[int] = {p.start}
        frontier = [p.start]
        while frontier:
            c = frontier.pop(0)
            for a in letters:
                d = p.step(c, a)
                if d not in seen_step:
                    seen_step.add(d)
                    frontier.append(d)
        still = sorted(set(missing) - seen_step)
        print(f"of the unreachable, reachable by step(): "
              f"{len(set(missing) & seen_step)} | by neither: {len(still)} {still}")


def main(argv: List[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__, file=sys.stderr)
        return 2
    case = _find(args[0])
    budget = int(args[1]) if len(args) > 1 else 60
    base = DEFAULT if "--sat" in argv else NOSAT_EXACT
    cfg = Config(**{**base.__dict__, "budget_seconds": budget})
    print(f"case: {case.case_id}\nconfig: {cfg.config_id}  budget={budget}s\n")

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

    print(f"verdict: {r.stats.verdict}  {r.stats.detail}")
    print(f"ref_classes: {r.stats.ref_classes}\n")
    p: Optional[Partition] = captured.get("p")
    if p is None:
        print("export was never reached — nothing to diagnose")
        return 1
    _analyse(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
