"""Exact-by-reference vs the transformation closure: the two oracles agree (spec item 10).

    python3 -m tests.sosl.exact_ref_gate [case]

Both oracles decide the same question — does the hypothesis denote L — and both
return the shortlex-least disagreeing lasso, so on any case they must drive the
learner along the *same* run. The gate replays each named case twice, once with
the teacher's default exact mode (exact-by-reference, `sosl.teacher.exact_ref`)
and once with the reference suppressed so the teacher takes the referenceless
fallback (the closure oracle, `sosl.teacher.exact`), and demands byte-equality of

  - the counterexample sequence (each lasso rendered),
  - the run ledger (per-phase query counters, splits, equivalence queries),
  - the exported invariant.

Any drift convicts one of the two oracles. Each case runs under both saturation
settings: with it off, `a_implies_xa` and `a_once` certify their proven-permanent
stalls (spec row P4) — the demanding half of the gate, since certification is
where an incomplete scan would silently succeed.
"""
from __future__ import annotations

import sys
from typing import Dict, List, Optional, Tuple

from sosl.contract import Counterexample, EquivResult
from sosl.sos import dump_invariant
from sosl.sos.alphabet import Alphabet
from sosl.sos.hypothesis import Hypothesis
from sosl.sos.invariant import Invariant
from sosl.sos.io.serialize import render_word
from sosl.sos.lasso import Lasso
from sosl.learn import learn
from sosl.teacher import HoaTeacher

SOURCES = "samples"

CASES: Tuple[str, ...] = (
    "gf_a", "gf_aa_parity", "even", "evenblocks", "a_implies_xa", "a_once",
)
"""The E0 named cases: the triptych's automata plus the two proven-permanent
stall specimens; ``gf_a`` is the LTL-built smoke case."""


class Recorder:
    """A teacher proxy that records the counterexample sequence. Delegates both
    queries verbatim, so the learner cannot tell it apart from the teacher."""

    def __init__(self, teacher: HoaTeacher) -> None:
        self.teacher = teacher
        self.cex: List[str] = []
        self.certified: List[str] = []

    def member(self, lasso: Lasso) -> bool:
        return self.teacher.member(lasso)

    def equiv(self, hypothesis: Hypothesis) -> EquivResult:
        result = self.teacher.equiv(hypothesis)
        if isinstance(result, Counterexample):
            self.cex.append(_render(self.teacher.alphabet, result.lasso))
        else:
            self.certified.append(result.strategy)
        return result


def _render(alphabet: Alphabet, lasso: Lasso) -> str:
    """The canonical one-line form of a counterexample lasso."""
    return (f"stem={render_word(alphabet, lasso.stem)} "
            f"loop={render_word(alphabet, lasso.loop)}")


def _teacher(case: str) -> HoaTeacher:
    if case == "gf_a":
        return HoaTeacher.of_ltl("GF a", eq_mode="exact")
    return HoaTeacher.of_hoa(f"{SOURCES}/{case}.hoa", eq_mode="exact")


def _suppress_reference(teacher: HoaTeacher) -> None:
    """Present the teacher as a referenceless target (the E6 path), so exact mode
    takes the transformation-closure oracle."""
    teacher._reference = None
    teacher._ref_built = True


def _run(case: str, saturation: bool, closure: bool) -> Tuple[Invariant, Dict[str, int], List[str], List[str]]:
    teacher = _teacher(case)
    if closure:
        _suppress_reference(teacher)
    recorder = Recorder(teacher)
    stats: Dict[str, int] = {}
    learned = learn(recorder, teacher.alphabet, stats=stats, saturation=saturation)
    return learned, stats, recorder.cex, recorder.certified


def check(case: str, saturation: bool) -> None:
    """One case under one saturation setting: the two oracles agree on
    counterexamples, ledger and export."""
    ref_inv, ref_stats, ref_cex, ref_cert = _run(case, saturation, closure=False)
    cl_inv, cl_stats, cl_cex, cl_cert = _run(case, saturation, closure=True)
    tag = f"{case} (saturation={'on' if saturation else 'off'})"

    assert ref_cex == cl_cex, (
        f"{tag}: counterexample sequences differ\n"
        f"  by-reference: {ref_cex}\n  closure:      {cl_cex}"
    )
    assert ref_cert == cl_cert, f"{tag}: certifications differ {ref_cert} vs {cl_cert}"
    assert ref_stats == cl_stats, (
        f"{tag}: ledgers differ\n  by-reference: {ref_stats}\n  closure:      {cl_stats}"
    )
    assert dump_invariant(ref_inv) == dump_invariant(cl_inv), (
        f"{tag}: exported invariants differ\n" + dump_invariant(ref_inv)
    )
    print(f"OK {tag}: {len(ref_cex)} cex, {ref_inv.n} classes, "
          f"ledger {ref_stats}")


def main(argv: List[str]) -> int:
    cases = (argv[1],) if len(argv) > 1 else CASES
    for case in cases:
        for saturation in (True, False):
            check(case, saturation)
    print("SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
