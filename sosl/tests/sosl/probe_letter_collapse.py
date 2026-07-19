"""Probe: how far does λ collapse the alphabet, per AP count?

    python3 -m tests.sosl.probe_letter_collapse [--limit N]

`Invariant.letter_class` is λ restricted to letters: the class of each
single-letter word, indexed by letter mask. Distinct letters may share a class,
and at the two-sided fixpoint sharing a class makes them interchangeable in
every context — so a frontier built over letter *classes* rather than over Σ
would carry the same information.

The learner does not do that: `Table.domain` builds `rows · Σ` in full and
`fill` queries every cell of it, so a row costs `|Σ|` extensions whatever λ
does. This probe measures the ceiling on what collapsing could save, from the
committed reference invariants — the effective alphabet `|λ(Σ)|` against `|Σ|`,
bucketed by AP count. The saving is a *ceiling*, not a promise: the learner only
knows the collapse once it has separated the letters, so a real implementation
would use the current classes speculatively and let the existing legality and
coherence checks catch a premature merge.
"""
from __future__ import annotations

import statistics
import sys
from collections import defaultdict
from typing import Dict, List

from sosl.experiment.manifest import flat_canon_cases
from sosl.sos.io import load_invariant


def main(argv: List[str]) -> int:
    limit = 0
    if "--limit" in argv:
        limit = int(argv[argv.index("--limit") + 1])
    cases = flat_canon_cases()
    if limit:
        cases = cases[:limit]

    # ap -> list of (alphabet size, distinct letter classes)
    buckets: Dict[int, List[tuple]] = defaultdict(list)
    skipped = 0
    for case in cases:
        try:
            with open(case.sos, encoding="utf-8") as fh:
                inv = load_invariant(fh.read())
        except Exception:  # noqa: BLE001 -- a missing reference is not this probe's business
            skipped += 1
            continue
        sigma = len(inv.letter_class)
        buckets[sigma.bit_length() - 1].append((sigma, len(set(inv.letter_class))))

    print(f"{sum(len(v) for v in buckets.values())} languages"
          + (f" ({skipped} skipped)" if skipped else ""))
    print("| AP | \\|Σ\\| | languages | median \\|λ(Σ)\\| | mean \\|λ(Σ)\\| | "
          "full collapse | no collapse | median saving |")
    print("|--:|--:|--:|--:|--:|--:|--:|--:|")
    for ap in sorted(buckets):
        rows = buckets[ap]
        sigma = rows[0][0]
        eff = [e for _, e in rows]
        full = sum(1 for e in eff if e == 1)
        none = sum(1 for e in eff if e == sigma)
        saving = statistics.median(sigma / e for e in eff)
        print(f"| {ap} | {sigma} | {len(rows)} | {statistics.median(eff):.0f} | "
              f"{statistics.mean(eff):.2f} | {full} | {none} | {saving:.2f}x |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
