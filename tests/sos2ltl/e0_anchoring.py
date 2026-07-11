"""C2 condition-(A) probe on one `.sos` invariant (E0 sanity).

    python3 -m tests.sos2ltl.e0_anchoring <file.sos> [--expect gfaa|even|evenblocks]

Per layer: the smallest anchoring width (or FAIL), the width-1 letter
classification, the anchor sets, and |𝒜_R|. With ``--expect gfaa`` asserts
the E0 predictions of `research_notes/sos_toltl_spec.md`: layers
{1,3} and {2,4} pass at k = 1 with the predicted reset tables, layer {5} is
frozen (both letters neutral). With ``--expect even|evenblocks`` asserts the
group's layer fails (A) at every width — the E1 denominator record.
"""
from __future__ import annotations

import sys
from typing import List

from aut2ltl.sos2ltl.anchoring import analyze
from aut2ltl.sos2ltl.cayley import build
from sosl.sos import load_invariant


def letter_name(inv, a: int) -> str:
    trues = inv.alphabet.true_aps(a)
    return "&".join(p if p in trues else "!" + p for p in inv.alphabet.aps)


def main(argv: List[str]) -> int:
    path = argv[0]
    expect = argv[2] if len(argv) > 2 and argv[1] == "--expect" else None
    with open(path) as f:
        inv = load_invariant(f.read())

    cay = build(inv)
    result = analyze(cay)
    for i, la in enumerate(result):
        w = "FAIL" if la.width is None else str(la.width)
        kinds = "  ".join(
            f"{letter_name(inv, a)}:{k}" for a, k in sorted(la.letter_kind.items()))
        anch = {c: [letter_name(inv, a) for a in v]
                for c, v in sorted(la.anchors.items()) if v}
        print(f"  layer {i} {{{' '.join(map(str, la.layer))}}}: width {w}"
              f"  [{kinds}]  anchors {anch}  |A_R|={len(la.monoid)}")

    widths = {tuple(la.layer): la.width for la in result}
    kinds = {tuple(la.layer): la.letter_kind for la in result}
    if expect == "gfaa":
        assert widths == {(0,): 1, (1, 3): 1, (2, 4): 1, (5,): 1}, widths
        assert kinds[(1, 3)] == {0: "reset(1)", 1: "reset(3)"}, kinds[(1, 3)]
        assert kinds[(2, 4)] == {0: "reset(4)", 1: "reset(2)"}, kinds[(2, 4)]
        assert kinds[(5,)] == {0: "neutral", 1: "neutral"}, kinds[(5,)]
        assert kinds[(0,)] == {0: "exit", 1: "exit"}, kinds[(0,)]
    elif expect in ("even", "evenblocks"):
        assert None in widths.values(), widths  # the group layer anchors nowhere
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
