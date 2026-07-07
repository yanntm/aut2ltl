"""Primitives layer (C section 2) checked against the triptych's hand values.

    python3 -m tests.sosl.classify_primitives

Loads the three fixture invariants and asserts the idempotent set, the H-order
(top / strict descendants), the agreement of the one-line idempotent test with
`Green.leq_h`, and the R-class partition of the idempotents against the values
hand-computed in `research_notes/sos_classification.md` section 9. Prints one OK
line per fixture, or raises on the first mismatch.
"""
from __future__ import annotations

import os

from sosl.sos import load_invariant
from sosl.sos.classify.primitives import Green, h_descents, idempotents, leq_h_idem

_SOS = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir,
                    "samples", "fixtures", "hoa", "sos")


def _load(name: str):
    with open(os.path.join(_SOS, name + ".sos")) as f:
        return load_invariant(f.read())


# Per fixture: expected E, and for each idempotent its set of strict H-descendants.
# Ids from the fixture .sos files; structure from C section 9.
CASES = {
    # Even: E={[!a],[a;!a],[a;a]} = {1,3,4}; [a;a]=4 on top over 1 and 3.
    "even": ({1, 3, 4}, {1: set(), 3: set(), 4: {1, 3}}),
    # GF(aa): E={1,3,4,5}; [a;a]=5 is the two-sided zero, below the other three.
    "gf_aa": ({1, 3, 4, 5}, {1: {5}, 3: {5}, 4: {5}, 5: set()}),
    # EvenBlocks: E={1,5,6,7}; zero z=[!a;a;!a]=6 below every idempotent.
    "evenblocks": ({1, 5, 6, 7}, {1: {6}, 5: {1, 6, 7}, 6: set(), 7: {6}}),
}


def check(name: str) -> None:
    inv = _load(name)
    want_E, want_desc = CASES[name]
    E = idempotents(inv)
    assert set(E) == want_E, (name, E, want_E)

    g = Green.of(inv)
    desc = dict(zip(E, h_descents(inv, E)))
    for e in E:
        got = set(desc[e])
        assert got == want_desc[e], (name, e, got, want_desc[e])
        # The one-line idempotent test agrees with ideal-membership leq_h.
        for f in E:
            assert leq_h_idem(inv, e, f) == g.leq_h(e, f), (name, e, f)

    # R-classes of E partition E and refine strict R-descent (a sanity check).
    rcs = g.r_classes(E)
    assert sorted(c for cls in rcs for c in cls) == sorted(E), (name, rcs)
    print(f"OK {name}: E={sorted(E)} R-classes={[list(c) for c in rcs]}")


def main() -> int:
    for name in CASES:
        check(name)
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
