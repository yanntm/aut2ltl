"""C3 condition-(B) probe on one `.sos` invariant (E0 sanity).

    python3 -m tests.sos2ltl.e0_windows <file.sos> [--expect gfaa]

Per layer: the (B) status, smallest conflict-free width, and for each
conflicting width a witness lasso pair — replayed against the invariant's
own membership read-off (equal recurring windows, opposite verdicts). With
``--expect gfaa`` asserts the E0 predictions: transient root, the two
all-rejecting final-candidate layers trivially (B)-determined at width 1,
and layer {5} passing at k' = 2 with a replayable k' = 1 failure.
"""
from __future__ import annotations

import sys
from typing import List

from aut2ltl.sos2ltl.cayley import build
from aut2ltl.sos2ltl.windows import FAIL, PASS, TRANSIENT, analyze
from sosl.sos import load_invariant


def render(inv, word) -> str:
    parts = []
    for a in word:
        trues = inv.alphabet.true_aps(a)
        parts.append("&".join(p if p in trues else "!" + p
                              for p in inv.alphabet.aps))
    return ";".join(parts) or "eps"


def main(argv: List[str]) -> int:
    path = argv[0]
    expect = argv[2] if len(argv) > 2 and argv[1] == "--expect" else None
    with open(path) as f:
        inv = load_invariant(f.read())

    cay = build(inv)
    reports = analyze(cay)
    for i, rep in enumerate(reports):
        extra = " (trivial)" if rep.trivial else ""
        print(f"  layer {i} {{{' '.join(map(str, rep.layer))}}}: "
              f"{rep.status} width {rep.width}{extra}")
        for k, (l1, l2) in sorted(rep.fail_witness.items()):
            v1, v2 = inv.member(l1), inv.member(l2)
            print(f"    k'={k} witness: ({render(inv, l1.stem)}, "
                  f"{render(inv, l1.loop)})^w [{v1}]  vs  "
                  f"({render(inv, l2.stem)}, {render(inv, l2.loop)})^w [{v2}]")
            assert v1 != v2, "witness pair does not toggle on replay"

    if expect == "gfaa":
        by_layer = {tuple(r.layer): r for r in reports}
        assert by_layer[(0,)].status == TRANSIENT
        assert by_layer[(1, 3)].status == PASS and by_layer[(1, 3)].width == 1
        assert by_layer[(1, 3)].trivial and by_layer[(2, 4)].trivial
        assert by_layer[(2, 4)].status == PASS and by_layer[(2, 4)].width == 1
        r5 = by_layer[(5,)]
        assert r5.status == PASS and r5.width == 2 and 1 in r5.fail_witness, r5
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
