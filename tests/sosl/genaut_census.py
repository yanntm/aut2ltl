"""Run the SoS learner over a folder of automata and surface surviving stalls.

    python3 -m tests.sosl.genaut_census <folder> [per_example_timeout_s]

A prototype of the eventual campaign driver (spec §8 M4): it is the shape the
"main" census will take — build the reference, learn against the automaton as
teacher, and classify the outcome against the spec's expected-failure table
(§9). Written as a template, not a throwaway.

For every automaton discovered under the folder (reusing ``survey.discovery`` for
recursion / content detection / pruning) it records, within a per-example
wall-clock bound:

  - ``ref``   canonical class count ``|S(L)+1|`` of the reference invariant;
  - ``stall`` the learner's first closed/consistent fixpoint size, before any
    equivalence query — a *stall* when coarser than ``ref``;
  - ``gap``   ``ref - stall``; ``cex`` counterexamples consumed to reach the
    learned fixpoint (each breaks a stall);
  - ``P1``    the Cayley **hypothesis** acceptor vs the teacher (spec §9 P1 —
    MUST be green; a red here is a genuine learner-core bug);
  - ``F2``    the exported ``.sos`` **invariant** acceptor vs the teacher (spec
    §9 F2 — MAY be red at M2, since export presumes a two-sided congruence);
  - ``byte``  whether the exported ``.sos`` is byte-equal to the reference.

Statuses: ``CANONICAL`` (byte-equal), ``STALL`` (byte differs but the hypothesis
is sound — a surviving, non-transient stall under the default equivalence mode,
the specimen this census hunts), ``BUG`` (P1 red — must never happen),
``NONDEF`` (Spot cannot present the language as a SoS reference), ``TIMEOUT``.
Nondeterministic or partial inputs are determinized by the sos import layer, so
no input is skipped. The smallest stalls (fewest reference classes) are listed
first, so the census doubles as a minimal-specimen search.
"""
from __future__ import annotations

import itertools
import signal
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from sosl.contract import Counterexample
from sosl.learn.export import export
from sosl.learn.learner import _build_hypothesis, _stabilize, process_counterexample
from sosl.learn.table import Table
from sosl.sos import Lasso, dump_invariant
from sosl.sos.build import ReferenceError, reference_of_hoa
from sosl.sos.hypothesis import Hypothesis, loop_reps
from sosl.teacher import HoaTeacher
from sosl.teacher.equiv import resolve_prediction
from survey.discovery import discover


class _Timeout(Exception):
    pass


def _alarm(_sig: int, _frame: object) -> None:
    raise _Timeout()


@dataclass
class Row:
    """One automaton's census outcome: a status plus the stall / acceptor
    metrics (``None`` on any field the run did not reach)."""

    tag: str
    status: str = "CANONICAL"
    ref: Optional[int] = None
    stall: Optional[int] = None
    cex: Optional[int] = None
    p1: Optional[bool] = None
    f2: Optional[bool] = None
    byte: Optional[bool] = None
    detail: str = ""

    @property
    def gap(self) -> Optional[int]:
        if self.ref is None or self.stall is None:
            return None
        return self.ref - self.stall


def _learn_to_fixpoint(
    teacher: HoaTeacher,
) -> Tuple[int, int, "Hypothesis", object, object]:
    """Drive the learner to the equivalence fixpoint the way ``learn`` does,
    returning ``(stall_n, cex, hypothesis, partition, exported_invariant)`` — the
    census needs the hypothesis and the export as separate objects, which the
    plain ``learn`` entry point does not expose."""
    table = Table(teacher.alphabet, teacher.member)
    stall_n: Optional[int] = None
    cex = 0
    while True:
        p = _stabilize(table)
        if stall_n is None:
            stall_n = p.n
        res = teacher.equiv(_build_hypothesis(table, p))
        if not isinstance(res, Counterexample):
            break
        process_counterexample(table, p, res.lasso)
        cex += 1
    hyp = _build_hypothesis(table, p)
    inv = export(p, teacher.member)
    assert stall_n is not None
    return stall_n, cex, hyp, p, inv


def _hyp_acc(teacher: HoaTeacher, hyp: "Hypothesis",
             stem_max: int = 3, loop_max: int = 3) -> bool:
    """The hypothesis acceptor check (spec §9 P1): the hypothesis' own lasso
    predictions agree with the teacher over ``|stem|, |loop| <= bounds``."""
    loops = loop_reps(hyp)
    letters = teacher.alphabet.letters()
    for slen in range(stem_max + 1):
        for stem in itertools.product(letters, repeat=slen):
            for llen in range(1, loop_max + 1):
                for loop in itertools.product(letters, repeat=llen):
                    la = Lasso(tuple(stem), tuple(loop))
                    if resolve_prediction(teacher.member, hyp, la, loops) \
                            != teacher.member(la):
                        return False
    return True


def _inv_acc(inv: object, teacher: HoaTeacher,
             stem_max: int = 3, loop_max: int = 3) -> bool:
    """The exported-invariant acceptor check (spec §9 F2): ``inv.member`` agrees
    with the teacher over the same lasso bound."""
    letters = teacher.alphabet.letters()
    for slen in range(stem_max + 1):
        for stem in itertools.product(letters, repeat=slen):
            for llen in range(1, loop_max + 1):
                for loop in itertools.product(letters, repeat=llen):
                    la = Lasso(tuple(stem), tuple(loop))
                    if inv.member(la) != teacher.member(la):
                        return False
    return True


def _run_one(path: str, tag: str, timeout_s: int) -> Row:
    row = Row(tag)
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(timeout_s)
    try:
        ref = reference_of_hoa(path)
        teacher = HoaTeacher.of_hoa(path)
        stall_n, cex, hyp, _p, inv = _learn_to_fixpoint(teacher)
        row.ref = ref.n
        row.stall = stall_n
        row.cex = cex
        row.p1 = _hyp_acc(teacher, hyp)
        row.f2 = _inv_acc(inv, teacher)
        row.byte = dump_invariant(ref) == dump_invariant(inv)
        if not row.p1:
            row.status = "BUG"          # P1 red: learner-core defect, must not happen
        elif not row.byte:
            row.status = "STALL"        # surviving stall (F2 red is then expected)
    except _Timeout:
        row.status = "TIMEOUT"
    except ReferenceError:
        row.status = "NONDEF"
    except Exception as exc:  # noqa: BLE001 -- census records, never aborts
        row.status = f"ERROR:{type(exc).__name__}"
        row.detail = str(exc)
    finally:
        signal.alarm(0)
    return row


def _fmt(x: object) -> str:
    return "-" if x is None else str(x)


def run(folder: str, timeout_s: int = 15) -> int:
    examples = [ex for ex in discover([Path(folder)]) if ex.is_hoa]
    rows: List[Row] = [
        _run_one(ex.value, Path(ex.value).stem, timeout_s)
        for ex in sorted(examples, key=lambda e: e.value)
    ]

    print(f"{'automaton':<28} {'status':<12} {'ref':>3} {'stall':>5} "
          f"{'gap':>3} {'cex':>3} {'byte':>5} {'P1':>2} {'F2':>2}")
    for r in sorted(rows, key=lambda r: r.tag):
        print(f"{r.tag:<28} {r.status:<12} {_fmt(r.ref):>3} {_fmt(r.stall):>5} "
              f"{_fmt(r.gap):>3} {_fmt(r.cex):>3} {_fmt(r.byte):>5} "
              f"{_fmt(r.p1):>2} {_fmt(r.f2):>2}")

    canonical = [r for r in rows if r.status == "CANONICAL"]
    stalls = [r for r in rows if r.status == "STALL"]
    bugs = [r for r in rows if r.status == "BUG"]
    nondef = [r for r in rows if r.status == "NONDEF"]
    other = [r for r in rows if r.status.startswith(("ERROR", "TIMEOUT"))]
    transient = [r for r in canonical if (r.gap or 0) > 0]

    print()
    print(f"total {len(rows)}: {len(canonical)} CANONICAL "
          f"({len(transient)} via a transient stall), {len(stalls)} STALL, "
          f"{len(bugs)} BUG, {len(nondef)} NONDEF, {len(other)} timeout/error")
    if bugs:
        print(f"  BUG (P1 red — learner-core defect): {[r.tag for r in bugs]}")
    if other:
        for r in other:
            print(f"  {r.tag}: {r.status} {r.detail}")

    if stalls:
        print("\nsurviving stalls, smallest first (ref, then tag):")
        for r in sorted(stalls, key=lambda r: (r.ref or 0, r.tag)):
            print(f"  {r.tag}: ref={r.ref} stall={r.stall} gap={r.gap} "
                  f"cex={r.cex} P1={r.p1} F2={r.f2}")
    else:
        print("\nno surviving stalls: every learned fixpoint is byte-canonical")

    return 1 if (bugs or other) else 0


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: genaut_census <folder> [per_example_timeout_s]",
              file=sys.stderr)
        return 2
    folder = sys.argv[1]
    timeout_s = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    return run(folder, timeout_s)


if __name__ == "__main__":
    raise SystemExit(main())
