"""The canonical form D is transition-based, whatever the input form.

    python3 -m tests.sos.transition_based

A state-based input (HOA declaring ``state-acc``, e.g. ``a_once.hoa``) or a
Spot product that happens to be state-based must come out of the import layer
(`sos.build.importer.canonical`) reading as transition-based: the
``state-acc`` property cleared, so Spot's renderer draws marks on transitions,
never accepting states (``peripheries=2``). Note Spot's HOA *printer*
re-detects structural state-acc on its own — serializations of D must use the
``"t"`` option (as `builder.reference_of_ltl`'s scratch dump does).
"""
from __future__ import annotations

import spot

from sosl.sos.build import import_hoa, import_ltl

A_ONCE = "research_notes/sos_figs/sources/a_once.hoa"


def check(aut: "spot.twa_graph", name: str) -> None:
    assert not aut.prop_state_acc().is_true(), f"{name}: D reads state-based"
    assert "peripheries=2" not in aut.to_str("dot"), \
        f"{name}: dot draws accepting states"
    assert "state-acc" not in aut.to_str("hoa", "t"), \
        f"{name}: HOA 't' dump declares state-acc"
    print(f"OK {name}: transition-based D")


def main() -> None:
    check(import_hoa(A_ONCE), "a_once.hoa (state-based Buchi input)")
    check(import_ltl("F a"), "F a")
    check(import_ltl("GF a"), "GF a")
    print("ALL OK")


if __name__ == "__main__":
    main()
