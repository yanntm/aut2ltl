"""The functionality guard: does it fire, and does firing explain the divergence?

    python3 -m tests.sosl.exact_ref_guard <case_id> [--nosat]

Spec §3.2 point (iii) / §9 row F10: exact-by-reference certifies only when the
aligned graph is functional (non-identity node count `= N_R`). Theory predicts
the guard never fires on learner-reachable tables — the *factoring conjecture*.
The census is the experiment.

For one flat_canon case this runs the ablation (or default) leg to a fixpoint and
reports, per equivalence query, whether the guard fired and how large the aligned
graph was against `N_R`. A firing is a counterexample to the factoring
conjecture: `fold_H` does not factor through `≈_L` beyond the table words, so the
closure oracle — which tracks each loop word's full action on hypothesis classes
— decides that query instead.
"""
from __future__ import annotations

import sys
from typing import List

from sosl.experiment.manifest import flat_canon_cases
from sosl.learn import learn
from sosl.sos import dump_invariant, load_invariant
from sosl.teacher import HoaTeacher


def main(argv: List[str]) -> int:
    case_id = argv[1]
    saturation = "--nosat" not in argv
    case = next(c for c in flat_canon_cases() if c.case_id == case_id)
    with open(case.sos, encoding="utf-8") as fh:
        ref = load_invariant(fh.read())

    teacher = HoaTeacher.of_hoa(case.hoa, eq_mode="exact", reference=ref)
    learned = learn(teacher, teacher.alphabet, saturation=saturation)

    leg = "default" if saturation else "no-saturation"
    fired = teacher.guard_firings
    print(f"{case_id} [{leg}]: reference {ref.n} classes, learned {learned.n}")
    print(f"  byte-equal to reference: {dump_invariant(learned) == dump_invariant(ref)}")
    print(f"  functionality guard fired on {len(fired)} equivalence "
          f"{'query' if len(fired) == 1 else 'queries'}")
    for exc in fired:
        print(f"    {exc.n_nodes} aligned nodes over {exc.n_ref} reference classes; "
              f"nodes {exc.collision[0]} and {exc.collision[1]} share an R-class")
    if fired:
        print("  => the factoring conjecture FAILS on a learner-reachable table "
              "(spec §9 F10); the closure oracle decided those queries")
    else:
        print("  => guard green on every query; certification is unconditional here")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
