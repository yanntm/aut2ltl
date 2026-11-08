"""One-input boundary control: native historical teacher versus stamp adapter."""
from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import json
from pathlib import Path
from typing import Protocol

from atlas_search.one import experiment
from atlas_search.adapter import read_reference
from sosl.contract import Counterexample, EquivResult, Teacher
from sosl.experiment.manifest import NOSAT_EXACT
from sosl.experiment.run import _drive
from sosl.experiment.stats import RunStats
from sosl.learn.learner import _build_hypothesis
from sosl.sos import Alphabet
from sosl.sos.hypothesis import Hypothesis
from sosl.sos.lasso import Lasso
from sosl.teacher import HoaTeacher


class AlphabetTeacher(Teacher, Protocol):
    """Historical query interface plus its explicitly supplied alphabet."""

    alphabet: Alphabet


class Recorder:
    """Forward unchanged native queries and retain its counterexamples."""

    def __init__(self, teacher: AlphabetTeacher) -> None:
        self.teacher = teacher
        self.alphabet = teacher.alphabet
        self.counterexamples: list[Lasso] = []

    def member(self, lasso: Lasso) -> bool:
        """Native simulation membership."""
        return self.teacher.member(lasso)

    def equiv(self, hypothesis: Hypothesis) -> EquivResult:
        """Native guarded-reference/closure decision without altered scheduling."""
        decision = self.teacher.equiv(hypothesis)
        if isinstance(decision, Counterexample):
            self.counterexamples.append(decision.lasso)
        return decision


def main() -> None:
    """Compare one known witness, including its full final action and contexts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("referent", type=Path)
    parser.add_argument("hoa", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    _, reference = read_reference(args.referent, reverse=True)
    native_reference = replace(reference, alphabet=Alphabet.of(["a"]))
    native = HoaTeacher.of_hoa(str(args.hoa), eq_mode="exact", reference=native_reference)
    native.cap_escape = False
    recorder = Recorder(native)
    stats = RunStats(case_id="nine-class-control", config_id="no-sat-exact")
    table, partition, exported, _, certification = _drive(recorder, NOSAT_EXACT, stats)
    hypothesis = _build_hypothesis(table, partition)
    adapted = experiment(args.referent, reverse=True)
    # Round-trip JSON normalizes tuple/list representation for structural checks.
    expected = json.loads(json.dumps(dict(
        hypothesis=dict(keys=hypothesis.keys, step=hypothesis.step, start=hypothesis.start),
        columns=[dict(kind=type(column).__name__, **asdict(column)) for column in table.columns],
        counterexamples=[asdict(lasso) for lasso in recorder.counterexamples],
    )))
    for field, value in expected.items():
        assert json.loads(json.dumps(adapted[field])) == value, field
    assert certification == adapted["certification"] == "exact"
    assert reference.n - 1 == adapted["reference_classes"] == 9
    assert partition.n - 1 == adapted["learned_classes"] == 7
    assert exported is None and adapted["verdict"] == "STALL"
    assert len(native.guard_firings) == adapted["guard_firings"]
    # Force every query through the complete closure as an independent route.
    closure = experiment(args.referent, reverse=True, closure_only=True)
    for field in ("hypothesis", "columns", "counterexamples", "verdict"):
        assert closure[field] == adapted[field], field
    report = dict(schema="atlas.historical-control.v1", matched=True,
        reference_classes=9, learned_classes=7, certification=certification,
        comparisons=["native-vs-stamp", "guarded-vs-closure-only"],
        native_counterexamples=expected["counterexamples"],
        guard_firings=len(native.guard_firings), adapter=adapted)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print("PASS native/stamp and guarded/closure-only: exact nine-to-seven stall")


if __name__ == "__main__":
    main()
