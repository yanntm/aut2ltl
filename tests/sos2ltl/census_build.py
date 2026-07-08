"""E1/E2 language-keyed census records over a genaut `corpus/sos` shape.

    python3 -m tests.sos2ltl.census_build <corpus/sos/TAG> [--out <file.jsonl>]

Iterates the shape's `.sos` files — one per distinct language, so §3b's "the
unit is the language" is structural here — and writes, per language, the
normative per-layer condition-(A)/(B) census record built by
`census.census_line` (the same builder the survey side channel uses). No
survey and no construction: a `corpus/sos` file already *is* the invariant.
Feed the output to `tests.sos2ltl.census_report` for the E1/E2 tables.

Aperiodicity (the LTL/non-LTL split E1/E2 restrict on) is the group scan —
`first_group(inv) is None`, the same predicate the certificate extractor uses.
"""
from __future__ import annotations

import os
import sys
from typing import List

from aut2ltl.sos2ltl.census import census_line
from sosl.sos import load_invariant
from sosl.sos.classify.aperiodic import first_group


def main(argv: List[str]) -> int:
    sos_dir = argv[0].rstrip("/")
    tag = os.path.basename(sos_dir)
    out = argv[argv.index("--out") + 1] if "--out" in argv \
        else f"tests/sos2ltl/logs/e12_{tag}.jsonl"
    os.makedirs(os.path.dirname(out), exist_ok=True)

    files = sorted(f for f in os.listdir(sos_dir) if f.endswith(".sos"))
    n_ltl = 0
    with open(out, "w") as fh:
        for fn in files:
            with open(os.path.join(sos_dir, fn)) as f:
                inv = load_invariant(f.read())
            aperiodic = first_group(inv) is None
            n_ltl += aperiodic
            fh.write(census_line(inv, aperiodic) + "\n")

    print(f"census_build [{tag}]: {len(files)} languages "
          f"({n_ltl} LTL, {len(files) - n_ltl} non-LTL) -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
