"""EvenBlocks paper-trace conformance gate (spec §8, M4.a; paper Table 8).

    python3 -m tests.sosl.evenblocks_conformance

Drives the saturated learner on EvenBlocks and asserts the run reproduces the
paper's §4.1/§5 trace — the split ledger of Table 8 — exactly:

  - initial stabilized table of 3 classes, day-one sweep clean;
  - exactly ONE equivalence counterexample, the lasso ``(eps, !a;a;a)``,
    processed by the LOOP chain, minting the omega column ``(a, a)`` and
    pulling ``!a;a`` out of ``[a]`` (3 -> 4);
  - two saturation escalations, both frozen chains, minting the omega columns
    ``(a, !a;a)`` (4 -> 6: ``a;a`` out of ``[a]``, ``a;!a`` out of ``[!a;a]``)
    then ``(eps, !a)`` (6 -> 8: ``a;!a;a`` out of ``[!a]``, ``!a;a;!a`` out of
    ``[a;a]``), in that order;
  - all four columns of the omega sort (prefix-independence: no linear column
    is ever minted);
  - the per-phase query ledger at its M3 baseline (fill 67 / harvest 4 /
    saturation 14 / P-cache 14), two equivalence queries;
  - the exported invariant byte-equal to the reference builder's (8 classes).

A drift in any of these is a paper regression (the ledger is printed in
`sos_learning.md` §5): reconcile the run against the paper before touching
either. The letters are masks over AP ``a``: ``!a = 0``, ``a = 1``.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from sosl.contract import Counterexample
from sosl.learn.columns import Column, OmCol
from sosl.learn.chains import process_counterexample
from sosl.learn.export import export
from sosl.learn.learner import _build_hypothesis, _stabilize
from sosl.learn.partition import Partition
from sosl.learn.saturate import saturate
from sosl.learn.table import Table
from sosl.sos import dump_invariant
from sosl.sos.build import reference_of_hoa
from sosl.sos.lasso import Lasso
from sosl.teacher import HoaTeacher

from tests.sosl.m3_ledgers import _describe_split

EVENBLOCKS = "samples/evenblocks.hoa"

# expected trace artifacts (masks: !a=0, a=1)
CEX = Lasso((), (0, 1, 1))                       # (eps, !a;a;a)
EXPECTED_EVENTS: List[Tuple[str, str, Column, int, int, str]] = [
    ("cex", "loop", OmCol((1,), (1,)), 3, 4,      # (a, a)
     "a -> a, !a;a"),
    ("saturation", "frozen", OmCol((1,), (0, 1)), 4, 6,   # (a, !a;a)
     "a -> a, a;a ; !a;a -> !a;a, a;!a"),
    ("saturation", "frozen", OmCol((), (0,)), 6, 8,       # (eps, !a)
     "!a -> !a, a;!a;a ; a;a -> a;a, !a;a;!a"),
]
BASELINE = {"fill": 67, "harvest": 4, "saturation": 14, "pcache": 14}


def drive(teacher: HoaTeacher):
    """Learn EvenBlocks with saturation, recording the split ledger (trigger,
    chain, minted column, class counts, split description), the counterexamples,
    the per-phase query counts, and the exported invariant."""
    phase = ["fill"]
    counts: Dict[str, int] = defaultdict(int)

    def member(la: Lasso) -> bool:
        counts[phase[0]] += 1
        return teacher.member(la)

    table = Table(teacher.alphabet, member)
    events: List[Tuple[str, str, Column, int, int, str]] = []
    cexes: List[Lasso] = []
    pending: Optional[Tuple[str, str, Column, Partition]] = None
    n_equiv = 0
    initial_n: Optional[int] = None
    day_one_clean: Optional[bool] = None

    while True:
        phase[0] = "fill"
        p = _stabilize(table)
        if initial_n is None:
            initial_n = p.n
        if pending is not None:
            trig, chain, col, before = pending
            events.append((trig, chain, col, before.n, p.n,
                           _describe_split(teacher.alphabet, before, p)))
            pending = None

        phase[0] = "saturation"
        lbl = saturate(table, p)
        if day_one_clean is None:
            day_one_clean = lbl is None
        if lbl is not None:
            pending = ("saturation", lbl, table.columns[-1], p)
            continue

        n_equiv += 1
        res = teacher.equiv(_build_hypothesis(table, p))
        if not isinstance(res, Counterexample):
            break
        cexes.append(res.lasso)
        phase[0] = "harvest"
        chain = process_counterexample(table, p, res.lasso)
        pending = ("cex", chain, table.columns[-1], p)

    phase[0] = "pcache"
    inv = export(p, member)
    return events, cexes, dict(counts), n_equiv, initial_n, day_one_clean, \
        list(table.columns), inv


def main() -> int:
    t = HoaTeacher.of_hoa(EVENBLOCKS)
    (events, cexes, counts, n_equiv, initial_n, day_one_clean,
     columns, inv) = drive(t)

    assert initial_n == 3, f"initial stabilized classes {initial_n} != 3"
    assert day_one_clean, "day-one sweep not clean"
    assert cexes == [CEX], f"counterexamples {cexes} != [{CEX}]"
    assert events == EXPECTED_EVENTS, (
        "split ledger drifted from the paper's Table 8:\n"
        f"  got      {events}\n  expected {EXPECTED_EVENTS}")
    assert n_equiv == 2, f"equivalence queries {n_equiv} != 2"
    assert len(columns) == 4 and all(isinstance(c, OmCol) for c in columns), (
        f"expected 4 omega columns (prefix-independence), got {columns}")
    assert counts == BASELINE, (
        f"query ledger drifted from the M3 baseline: {counts} != {BASELINE}; "
        "if intentional, re-baseline sos_learning_report.md and the paper's §5 ledger")

    ref = reference_of_hoa(EVENBLOCKS)
    assert inv.n == 8 and dump_invariant(inv) == dump_invariant(ref), (
        f"export not byte-equal to reference (learned {inv.n}, ref {ref.n})")

    print("OK EvenBlocks conformance: 3 classes, clean day-one sweep; one cex "
          "(eps, !a;a;a) via the loop chain -> (a, a); two frozen escalations "
          "-> (a, !a;a), (eps, !a); 3->4->6->8; ledger 67/4/14/14; byte-equal")
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
