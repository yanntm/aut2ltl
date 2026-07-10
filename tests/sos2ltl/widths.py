"""Per-example anchoring-width census over a validation folder.

One line per input: the multiset of per-layer condition-(A) widths (None = a
layer anchoring at no width, the scoped-fallback stratum). The tail line
reports the corpus maximum, which is the reachability answer for the graded
engine (Theorem 4.13 fires only where some layer needs width ≥ 2).

    python3 -m tests.sos2ltl.widths samples/validation/hoa
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import List, Optional

import spot

from aut2ltl.language import Language
from aut2ltl.sos2ltl import anchoring
from aut2ltl.sos2ltl.bridge import invariant_of_language
from aut2ltl.sos2ltl.cayley import build


def _widths(path: Path) -> List[Optional[int]]:
    lang = Language.of(spot.automaton(str(path)))
    inv = invariant_of_language(lang)
    cay = build(inv)
    return [la.width for la in anchoring.analyze(cay)]


def main(argv: List[str]) -> int:
    folder = Path(argv[0])
    files = sorted(folder.glob("*.hoa"))
    overall: Counter = Counter()
    worst = 0
    for f in files:
        try:
            ws = _widths(f)
        except Exception as e:  # bridge/aperiodicity decline is data, not a crash
            print(f"{f.name}: SKIP ({type(e).__name__})")
            continue
        overall.update("None" if w is None else w for w in ws)
        finite = [w for w in ws if w is not None]
        worst = max([worst] + finite)
        print(f"{f.name}: widths={ws}")
    print(f"--- width histogram: {dict(overall)}  MAXFINITE={worst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
