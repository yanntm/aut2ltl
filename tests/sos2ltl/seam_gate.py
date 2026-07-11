"""M3 gate — the graded engine's seam bricks are load-bearing (paper §4.3).

    python3 -m tests.sos2ltl.seam_gate [<file.sos>]

On the F8 exhibit `2state1ap0acc_086_c` ("reaches an accepting sink",
the default input) the layer `{2, 5, 8}` is 2-anchored (`a` a partial
constant onto `2`, `!a` acting `2↦5↦8↦8`; operating width `κ = 3`), and
the word `a·a·!a·a·(!a)^ω` from entry class `2` stutters twice, moves,
and exits within `k` steps of the transient's end: its certifying window
`(a, a, !a) ∈ An_3(5)` opens at the entry — too early for `TL_0`'s `U`,
so only the seam disjunct can witness it (paper §4.3, the seam remark).

The probe drives `_layer_graded` directly on that layer, rooted at
class `2` with the exit children stubbed exactly (`Final = ⊤` on the
committed exit targets) — `transcribe` itself would short-circuit the
whole layer to `⊤`, classes `2/5/8` being committed — and asserts:

  - the witness word satisfies `Final(2)` (Theorem 4.13 exactness);
  - with `seam` forced to `⊥` the word fails — the seam disjunct is
    what accepts it, not another brick;
  - full-engine leg: `transcribe` no longer declines on the exhibit,
    and the emitted formula passes the §3 conformance gate (the
    reference invariant of the flat form is byte-equal to the input).
"""
from __future__ import annotations

import sys
from typing import List, Set

import spot

from aut2ltl.sos2ltl import anchoring, engine, windows
from aut2ltl.sos2ltl.cayley import build
from sosl.sos import dump_invariant, load_invariant
from sosl.sos.build.importer import import_ltl
from sosl.sos.core.quotient import invariant_of

DEFAULT = "genaut/corpus/flat_canon/sos/2state1ap0acc_086_c.sos"
LAYER = (2, 5, 8)
ENTRY = 2
WORD = "a; a; !a; a; cycle{!a}"


def accepts(phi: "spot.formula", word: str) -> bool:
    """Membership of an ultimately periodic word in `L(phi)`, via Spot."""
    aut = spot.translate(phi)
    w = spot.parse_word(word, aut.get_dict())
    return aut.intersects(w.as_automaton())


def graded_label(inv, cay, layer_id: int) -> "spot.formula":
    """`Final(ENTRY)` of the layer's graded bricks, exit children stubbed
    with the exact constant `⊤` (every exit target is committed)."""
    la = anchoring.analyze_layer(cay, layer_id)
    assert la.width == 2, f"layer expected 2-anchored, got width {la.width}"
    lets = engine._Letters(inv)
    rep = windows.analyze_layer(cay, layer_id)
    wterm = engine._window_term(cay, layer_id, rep, lets)
    assert wterm is not None, "no window term on the gate layer"

    targets: Set[int] = {
        cay.step(c, a) for c in la.layer for a in la.exits[c]}
    final = {}
    for d in targets:
        assert engine._committed(cay, d), f"exit target {d} not committed"
        final[d] = spot.formula.tt()
    exit_ = engine._Exits(inv, final, residual=False)
    engine._layer_graded(cay, la, layer_id, la.width, lets, final, exit_,
                         engine.Rendering(residual=False), lambda _c: wterm)
    return final[ENTRY]


def main(argv: List[str]) -> int:
    path = argv[0] if argv else DEFAULT
    with open(path) as f:
        inv = load_invariant(f.read())
    cay = build(inv)
    layer_id = next(
        i for i, layer in enumerate(cay.layers) if layer == LAYER)

    phi = graded_label(inv, cay, layer_id)
    print(f"Final({ENTRY}) of layer {LAYER}: {phi}")
    assert accepts(phi, WORD), \
        f"GATE FAILURE: seam witness {WORD} rejected by the graded label"
    print(f"  seam witness {WORD}: accepted")

    real_seam = engine._seam
    engine._seam = lambda arms, c: engine._FF
    try:
        phi_no_seam = graded_label(inv, cay, layer_id)
    finally:
        engine._seam = real_seam
    assert not accepts(phi_no_seam, WORD), \
        "seam not load-bearing: the witness accepts without it"
    print("  without seam: rejected (the seam disjunct carries the word)")

    full = engine.transcribe(inv)
    assert full is not None, "transcribe declines on the exhibit"
    conf = invariant_of(import_ltl(str(full)))
    assert conf is not None, "conformance rebuild blew its cap"
    assert dump_invariant(conf) == dump_invariant(inv), \
        "CONFORMANCE FAILURE: I(L(phi)) differs from the input invariant"
    print(f"  full engine: {full}")
    print("  conformance: I(L(phi)) byte-equal to input")
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
