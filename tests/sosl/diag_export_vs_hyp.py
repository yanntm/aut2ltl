"""Diagnostic: does export preserve the hypothesis's acceptance read-off?

    python3 -m tests.sosl.diag_export_vs_hyp "F (a & X a)"

Learns to the equivalence fixpoint, then on the same partition compares, per
lasso up to a small bound, three read-offs: the internal Hypothesis (via
resolve_prediction, the path the teacher's equiv trusts), the exported Invariant
(Invariant.member), and the teacher. Prints the first lasso where the exported
invariant diverges from the hypothesis (an export bug) or from the teacher.
"""
from __future__ import annotations

import itertools
import sys

from sosl.learn.export import export
from sosl.learn.learner import _build_hypothesis, _stabilize
from sosl.learn.table import Table
from sosl.sos import Lasso
from sosl.sos.hypothesis import loop_reps
from sosl.teacher import HoaTeacher
from sosl.teacher.equiv import resolve_prediction


def run(formula: str) -> int:
    t = HoaTeacher.of_ltl(formula)
    # Drive the learner to the fixpoint the same way learn() does.
    from sosl.learn.learner import process_counterexample
    from sosl.contract import Counterexample
    table = Table(t.alphabet, t.member)
    while True:
        p = _stabilize(table)
        res = t.equiv(_build_hypothesis(table, p))
        if not isinstance(res, Counterexample):
            break
        process_counterexample(table, p, res.lasso)

    hyp = _build_hypothesis(table, p)
    loops = loop_reps(hyp)
    inv = export(p, t.member)

    letters = t.alphabet.letters()
    n_hyp_vs_teacher = n_inv_vs_hyp = n_inv_vs_teacher = 0
    first_inv_vs_hyp = None
    for slen in range(4):
        for stem in itertools.product(letters, repeat=slen):
            for llen in range(1, 4):
                for loop in itertools.product(letters, repeat=llen):
                    la = Lasso(tuple(stem), tuple(loop))
                    hp = resolve_prediction(t.member, hyp, la, loops)
                    iv = inv.member(la)
                    te = t.member(la)
                    if hp != te:
                        n_hyp_vs_teacher += 1
                    if iv != hp:
                        n_inv_vs_hyp += 1
                        if first_inv_vs_hyp is None:
                            first_inv_vs_hyp = (la, iv, hp, te)
                    if iv != te:
                        n_inv_vs_teacher += 1

    print(f"formula: {formula!r}  classes={p.n}")
    print(f"hyp vs teacher disagreements: {n_hyp_vs_teacher}  "
          f"(0 => equiv correctly certified the hypothesis)")
    print(f"exported-inv vs hyp disagreements: {n_inv_vs_hyp}  "
          f"(>0 => EXPORT is lossy)")
    print(f"exported-inv vs teacher disagreements: {n_inv_vs_teacher}")
    if first_inv_vs_hyp:
        la, iv, hp, te = first_inv_vs_hyp
        print(f"first export divergence: {la}  inv={iv} hyp={hp} teacher={te}")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: diag_export_vs_hyp <ltl-formula>", file=sys.stderr)
        return 2
    return run(sys.argv[1])


if __name__ == "__main__":
    raise SystemExit(main())
