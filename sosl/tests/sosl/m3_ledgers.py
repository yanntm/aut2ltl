"""M3 deliverables to the theory thread: the split ledger and the per-phase query
ledger of a saturated learner run.

    python3 -m tests.sosl.m3_ledgers <hoa> [<hoa> ...]
    python3 -m tests.sosl.m3_ledgers            # default: even, evenblocks

For each input it drives the saturated learner (default bounded equivalence) and
prints two tables:

  - **split ledger** — one row per top-level split (counterexample or saturation
    escalation; the routine close/consist splits that reach the first stabilized
    table are folded into the initial class count): its trigger, the chain that
    minted the column, the minted column, and the class that split;
  - **query ledger** — membership queries by phase (fill / harvest / saturation /
    P-cache), equivalence queries, counterexamples, saturation escalations, and
    the final column counts.

This is a prototype of the campaign's audit renderer (spec §7 stats, experiment
E4 transcripts): the learner procedures are reused unchanged, with a phase-tagged
counting `member` wrapper and a partition diff to name each split.
"""
from __future__ import annotations

import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from sosl.contract import Counterexample
from sosl.learn.chains import process_counterexample
from sosl.learn.columns import Column, LinCol
from sosl.learn.export import export
from sosl.learn.learner import _build_hypothesis, _stabilize
from sosl.learn.partition import Partition
from sosl.learn.saturate import saturate
from sosl.learn.table import Table
from sosl.sos.alphabet import Alphabet, Word, shortlex_key
from sosl.sos.io.serialize import render_word
from sosl.sos.lasso import Lasso
from sosl.teacher import HoaTeacher


def _render_col(ab: Alphabet, col: Column) -> str:
    """A column as the context it drops a candidate ``[]`` into."""
    def w(word: Word) -> str:
        return render_word(ab, word)
    if isinstance(col, LinCol):
        return f"{w(col.x)}·[]·{w(col.y)} , ({w(col.t)})^ω"
    return f"{w(col.x)}·([]·{w(col.y)})^ω"


def _render_lasso(ab: Alphabet, la: Lasso) -> str:
    return f"({render_word(ab, la.stem)}, {render_word(ab, la.loop)})"


def _describe_split(ab: Alphabet, before: Partition, after: Partition) -> str:
    """Each class of ``before`` that ``after`` tore apart, as ``src -> a, b`` in
    shortlex reps, ``;``-joined (one mint can split several classes at once) — or
    ``(no split)`` if the class count did not grow."""
    parts: List[str] = []
    for c in range(before.n):
        words = before.members[c]
        buckets: Dict[int, List[Word]] = {}
        for wd in words:
            ac = after.class_of.get(wd)
            if ac is not None:
                buckets.setdefault(ac, []).append(wd)
        if len(buckets) > 1:
            src = min(words, key=shortlex_key)
            pieces = sorted((min(ws, key=shortlex_key) for ws in buckets.values()),
                            key=shortlex_key)
            parts.append(f"{render_word(ab, src)} -> "
                         + ", ".join(render_word(ab, p) for p in pieces))
    return " ; ".join(parts) if parts else "(no split)"


@dataclass
class Row:
    trigger: str
    chain: str
    column: Column
    before: Partition


def build_ledger(path: str) -> None:
    teacher = HoaTeacher.of_hoa(path)
    ab = teacher.alphabet
    phase = ["fill"]
    counts: Dict[str, int] = defaultdict(int)

    def counting_member(la: Lasso) -> bool:
        counts[phase[0]] += 1
        return teacher.member(la)

    table = Table(ab, counting_member)
    ledger: List[Tuple[Row, int, str]] = []   # (row, after_n, split description)
    pending: Optional[Row] = None
    n_equiv = n_cex = n_sat = 0

    while True:
        phase[0] = "fill"
        p = _stabilize(table)
        if pending is not None:
            ledger.append((pending, p.n, _describe_split(ab, pending.before, p)))
            pending = None

        phase[0] = "saturation"
        lbl = saturate(table, p)
        if lbl is not None:
            n_sat += 1
            pending = Row("saturation", lbl, table.columns[-1], p)
            continue

        n_equiv += 1
        res = teacher.equiv(_build_hypothesis(table, p))
        if not isinstance(res, Counterexample):
            break
        n_cex += 1
        phase[0] = "harvest"
        chain = process_counterexample(table, p, res.lasso)
        pending = Row(f"cex {_render_lasso(ab, res.lasso)}", chain,
                      table.columns[-1], p)

    phase[0] = "pcache"
    inv = export(p, counting_member)

    n_lin = sum(isinstance(c, LinCol) for c in table.columns)
    n_om = len(table.columns) - n_lin

    print(f"=== {path} ===")
    print(f"final classes: {inv.n}   (initial stabilized: "
          f"{ledger[0][0].before.n if ledger else p.n})")
    print("\nsplit ledger:")
    print(f"  {'#':>2}  {'trigger':<22} {'chain':<8} {'n':<7} {'split':<20} column")
    for i, (row, after_n, split) in enumerate(ledger, 1):
        print(f"  {i:>2}  {row.trigger:<22} {row.chain:<8} "
              f"{row.before.n}->{after_n:<4} {split:<20} {_render_col(ab, row.column)}")

    print("\nquery ledger:")
    for ph in ("fill", "harvest", "saturation", "pcache"):
        print(f"  member/{ph:<11} {counts.get(ph, 0)}")
    print(f"  member/total      {sum(counts.values())}")
    print(f"  equiv             {n_equiv}")
    print(f"  counterexamples   {n_cex}")
    print(f"  sat escalations   {n_sat}")
    print(f"  columns lin/om    {n_lin}/{n_om}")
    print()


def main(argv: List[str]) -> int:
    cases = argv or ["samples/even.hoa",
                     "samples/evenblocks.hoa"]
    for path in cases:
        build_ledger(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
