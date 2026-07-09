"""The functionality guard: does it fire, and what does a firing exhibit?

    python3 -m tests.sosl.exact_ref_guard <case_id> [--nosat]

Spec §3.2 point (iii) / §9 row F10: exact-by-reference certifies only when the
aligned graph is functional (node count `= N_R`). Theory conjectured the guard
never fires on learner-reachable tables — *factoring*, that the hypothesis fold
coarsens the syntactic congruence beyond its table words. The census is the
experiment, and this probe is the instrument.

For one flat_canon case it runs a leg to a fixpoint and reports, per firing, the
graph size against `N_R` **and the two witness words** the collision names: `y`
and `y'` key two aligned nodes sharing an `R`-class, so `y ≈_L y'` while
`psi_H(y) != psi_H(y')`. Both claims are re-verified here against the reference
invariant and the hypothesis's own fold, so the exhibit stands on checked facts
rather than on the guard's word. A firing on the FINAL certifying query of a
byte-equal run is a defect (that table is canonical) and is called out.
"""
from __future__ import annotations

import sys
from typing import List

from sosl.experiment.manifest import flat_canon_cases
from sosl.learn import learn
from sosl.sos import dump_invariant, load_invariant
from sosl.sos.invariant import Invariant
from sosl.sos.io.serialize import render_word
from sosl.teacher import HoaTeacher
from sosl.teacher.exact_ref import NotFunctional


def _exhibit(teacher: HoaTeacher, ref: Invariant, exc: NotFunctional) -> str:
    """One firing, with its witness pair verified on both sides."""
    y, yp = exc.witnesses
    ab = teacher.alphabet
    assert ref.fold(y) == ref.fold(yp) == exc.ref_class, \
        "witness words do not share the reference class the guard reported"
    (h_y, _), (h_yp, _) = exc.collision
    assert h_y != h_yp, "colliding nodes share their hypothesis class too"
    return (f"    {exc.n_nodes} nodes over {exc.n_ref} R-classes; "
            f"y={render_word(ab, y) or 'eps'} y'={render_word(ab, yp) or 'eps'}: "
            f"both in R-class {exc.ref_class}, folds {h_y} != {h_yp}")


def main(argv: List[str]) -> int:
    case_id = argv[1]
    saturation = "--nosat" not in argv
    case = next(c for c in flat_canon_cases() if c.case_id == case_id)
    with open(case.sos, encoding="utf-8") as fh:
        ref = load_invariant(fh.read())

    teacher = HoaTeacher.of_hoa(case.hoa, eq_mode="exact", reference=ref)
    teacher.cap_escape = saturation
    learned = learn(teacher, teacher.alphabet, saturation=saturation)

    leg = "default" if saturation else "no-saturation"
    fired = teacher.guard_firings
    byte_equal = dump_invariant(learned) == dump_invariant(ref)
    print(f"{case_id} [{leg}]: reference {ref.n} classes, learned {learned.n}")
    print(f"  byte-equal to reference: {byte_equal}")
    print(f"  functionality guard fired on {len(fired)} equivalence "
          f"{'query' if len(fired) == 1 else 'queries'}"
          f"; final query fired: {teacher.last_query_fired}")
    for exc in fired:
        print(_exhibit(teacher, ref, exc))
    if byte_equal and teacher.last_query_fired:
        print("  DEFECT: a SOUND run fired on its final, certifying query — that "
              "table is canonical, so its fold is the syntactic morphism (F10)")
        return 1
    if fired:
        print("  => the factoring conjecture FAILS on a learner-reachable table "
              "(spec §9 F10): the fold splits a syntactic class beyond its table "
              "words; the closure oracle decided those queries")
    else:
        print("  => guard green on every query; certification is unconditional here")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
