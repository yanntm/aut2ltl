"""genaut/gen/build.py — realise a Shape's combo as a Spot TGBA, and reduce it.

build_aut turns a guard-code tuple (one per slot, from shape.combo_at) into a
twa_graph; reduce_aut runs the single structural postprocess pass the census uses
(see algorithm.md::"Build and reduce"). Needs Spot + BuDDy.
"""
from __future__ import annotations

from typing import List, Tuple

import spot
import buddy

from shape import Shape

# The single reduction pass — same spot.postprocess convenience aut2ltl uses for
# input cleanup (aut2ltl/language.py::_clean): (type, level, pref). Generic keeps
# the acceptance family; Small is the structural reducer. NOT `deterministic`, so
# universality is left undecided -- exactly as the tool sees it (see ../README.md).
POST_ARGS: Tuple[str, str, str] = ("generic", "high", "small")


def _ap_names(naps: int) -> List[str]:
    """AP names a, b, c, ... (the first `naps` lowercase letters)."""
    return [chr(ord("a") + i) for i in range(naps)]


def _minterm_bdds(aps: List[int]) -> List["buddy.bdd"]:
    """The letters of 2^AP as BDDs — one per assignment to `aps`, in minterm order
    (bit i of the index = the value of aps[i]). This is the APBDDIterator idea from
    sogits/libITS: walk 2^AP once. Empty `aps` -> [bddtrue], the single letter of a
    0-AP alphabet (cf. EmptyAPIterator)."""
    letters: List["buddy.bdd"] = []
    for m in range(1 << len(aps)):
        term = buddy.bddtrue
        for i, ap in enumerate(aps):
            term &= buddy.bdd_ithvar(ap) if (m >> i) & 1 else buddy.bdd_nithvar(ap)
        letters.append(term)
    return letters


def _guard_bdd(code: int, letters: List["buddy.bdd"]) -> "buddy.bdd":
    """Guard `code` as a BDD: the union (OR) of the letters whose bit is set in
    `code`. code 0 -> bddfalse (the caller skips it as an absent edge)."""
    acc = buddy.bddfalse
    for m, letter in enumerate(letters):
        if (code >> m) & 1:
            acc |= letter
    return acc


def _set_acceptance(aut: "spot.twa_graph", shape: Shape) -> None:
    """Realise the shape's acceptance condition over its `nacc` colours. The family
    is orthogonal to the slot/markset enumeration — only the acceptance *formula*
    changes, so the combo ids are the same across families.

      "gba"    — generalized Büchi Inf(0) & ... & Inf(nacc-1) (the default; nacc=0
                 is the `t` condition, every run accepting);
      "parity" — parity max even over nacc colours, e.g. nacc=3 gives
                 Inf(2) | (Fin(1) & Inf(0)); the Fin/Inf alternation the
                 generalized-Büchi family cannot express (nacc>=1 required).
    """
    if shape.acc == "gba":
        aut.set_generalized_buchi(shape.nacc)
    elif shape.acc == "parity":
        if shape.nacc < 1:
            raise ValueError("parity acceptance needs nacc >= 1")
        aut.set_acceptance(shape.nacc,
                           spot.acc_code(f"parity max even {shape.nacc}"))
    else:
        raise ValueError(f"unknown acceptance family {shape.acc!r}")


def build_aut(shape: Shape, combo: Tuple[int, ...],
              bdict: "spot.bdd_dict") -> "spot.twa_graph":
    """Build one raw automaton from a guard-code tuple (one code per slot of
    `shape`), under the shape's acceptance family (`_set_acceptance`)."""
    aut = spot.make_twa_graph(bdict)
    aps = [aut.register_ap(name) for name in _ap_names(shape.naps)]
    letters = _minterm_bdds(aps)            # the 2^k letters, built once
    _set_acceptance(aut, shape)
    aut.new_states(shape.nstates)
    aut.set_init_state(0)

    for (src, dst, markset), code in zip(shape.slots, combo):
        if code == 0:                       # all-false guard == edge absent
            continue
        aut.new_edge(src, dst, _guard_bdd(code, letters), list(markset))
    return aut


def reduce_aut(aut: "spot.twa_graph") -> "spot.twa_graph":
    return spot.postprocess(aut, *POST_ARGS)


def aut_at(shape: Shape, index: int, bdict: "spot.bdd_dict") -> "spot.twa_graph":
    """Rebuild the RAW automaton (pre-reduce) for generator id `index`."""
    return build_aut(shape, shape.combo_at(index), bdict)
