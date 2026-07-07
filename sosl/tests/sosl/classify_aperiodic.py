"""Band-1 (aperiodicity) read-off on one `.sos` invariant.

    python3 -m tests.sosl.classify_aperiodic <file.sos> [--expect ltl|group:<key>,<m>,<p>]

Loads the invariant, runs `sosl.sos.classify.aperiodic`, prints the verdict —
and, on a group, the carrier's key, index, period, and cycle keys. With
``--expect`` the run asserts the verdict and exits non-zero on mismatch.

Triptych expectations (research_notes/sos_classification.md §4):

    gf_aa.sos       --expect ltl
    even.sos        --expect group:a,1,2
    evenblocks.sos  --expect group:a,1,2
"""
from __future__ import annotations

import sys

from sosl.sos import load_invariant
from sosl.sos.classify.aperiodic import first_group


def render_key(inv, c: int) -> str:
    """Class ``c``'s key as `letter;letter;...` over AP names, `eps` if empty."""
    parts = []
    for a in inv.keys[c]:
        trues = inv.alphabet.true_aps(a)
        names = [p if p in trues else "!" + p for p in inv.alphabet.aps]
        parts.append("&".join(names))
    return ";".join(parts) or "eps"


def main(argv: list) -> int:
    path = argv[0]
    expect = None
    if len(argv) > 2 and argv[1] == "--expect":
        expect = argv[2]
    with open(path) as f:
        inv = load_invariant(f.read())
    g = first_group(inv)
    if g is None:
        print(f"{path}: APERIODIC (LTL) — {inv.n} classes")
        got = "ltl"
    else:
        key = render_key(inv, g.cls)
        cyc = " ".join(render_key(inv, c) for c in g.cycle)
        print(f"{path}: GROUP — carrier [{key}] index {g.index} "
              f"period {g.period} cycle {{{cyc}}}")
        got = f"group:{key},{g.index},{g.period}"
    if expect is not None and got != expect:
        print(f"FAIL: expected {expect}, got {got}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
