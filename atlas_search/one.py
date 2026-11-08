"""Run one atlas referent through the unchanged historical relaxed learner."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
import time
from typing import Any

# This executable explicitly selects the historical package in its own clone.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sosl"))

from sosl.contract import Counterexample, Equivalent
from sosl.learn.export import export
from sosl.learn.learner import _build_hypothesis, _stabilize
from sosl.learn.chains import process_counterexample
from sosl.learn.saturate import find_left_divergence
from sosl.learn.table import Table
from sosl.teacher.exact import ExactTooLarge
from synomega.calculus import residual_count
from synomega.sosio import dump_sos_id

from .adapter import StampTeacher, read_reference


def experiment(path: Path, *, reverse: bool = False,
               closure_only: bool = False, saturation: bool = False) -> dict[str, Any]:
    """Keep historical refinement and bootstrap; return a replayable outcome."""
    obj, reference = read_reference(path, reverse=reverse)
    teacher = StampTeacher(reference, closure_only=closure_only)
    table = Table(reference.alphabet, teacher.member)
    rounds: list[dict[str, int]] = []
    while True:
        partition = _stabilize(table)
        if saturation:
            from sosl.learn.saturate import saturate
            if saturate(table, partition):
                continue
        hypothesis = _build_hypothesis(table, partition)
        rounds.append(dict(classes=partition.n - 1, rows=len(table.rows),
                           columns=len(table.columns)))
        decision = teacher.equiv(hypothesis)
        if isinstance(decision, Equivalent):
            break
        assert isinstance(decision, Counterexample)
        process_counterexample(table, partition, decision.lasso)

    divergence = find_left_divergence(table, partition)
    congruent = divergence is None
    if congruent:
        learned = export(partition, teacher.member)
        if learned != reference:
            raise AssertionError("Exact congruent fixpoint differs from reference")
    groups: dict[int, list[list[int]]] = {}
    for word in reference.keys[1:]:
        groups.setdefault(partition.fold(word), []).append(list(word))
    first_divergence = None
    if divergence is not None:
        subject, key, left, before, after = divergence
        first_divergence = dict(subject=subject, key=key,
            left=partition.rep[left], subject_result=partition.rep[before],
            key_result=partition.rep[after])
    return dict(
        schema="atlas.historical-stall.v1", input=str(path.resolve()),
        key=dump_sos_id(obj), symbol_order=reference.alphabet.aps,
        mode="saturated" if saturation else "relaxed", closure_only=closure_only,
        reference_classes=reference.n - 1, learned_classes=partition.n - 1,
        residual_states=residual_count(obj),
        certification=decision.strategy, congruent=congruent,
        verdict="CANONICAL" if congruent else "STALL",
        first_divergence=first_divergence,
        reference_key_collisions=[dict(learned_key=partition.rep[c], reference_keys=words)
                                  for c, words in groups.items() if len(words) > 1],
        counterexamples=[asdict(lasso) for lasso in teacher.counterexamples],
        n_equiv=teacher.n_equiv, member_calls_including_oracle=teacher.member_calls,
        guard_firings=teacher.guard_firings, final_guard_fired=teacher.last_query_fired,
        closure_calls=teacher.closure_calls, rounds=rounds,
        hypothesis=dict(keys=hypothesis.keys, step=hypothesis.step,
                        start=hypothesis.start),
        columns=[dict(kind=type(column).__name__, **asdict(column))
                 for column in table.columns],
    )


def main() -> int:
    """Run one input; the invoking campaign owns its hard wall-clock bound."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--reverse", action="store_true")
    parser.add_argument("--closure-only", action="store_true")
    parser.add_argument("--saturated", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    try:
        result = experiment(args.input, reverse=args.reverse,
                            closure_only=args.closure_only, saturation=args.saturated)
        code = 0
    except ExactTooLarge as exc:
        result = dict(verdict="ORACLE_LIMIT", detail=str(exc))
        code = 2
    except Exception as exc:
        result = dict(verdict="CRASH", detail=f"{type(exc).__name__}: {exc}")
        code = 1
        import traceback
        traceback.print_exc()
    result["elapsed_seconds"] = time.monotonic() - started
    encoded = json.dumps(result, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    print(encoded, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
