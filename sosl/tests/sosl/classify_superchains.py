"""Superchain numbers (C section 6) on the triptych, against C section 9.

    python3 -m tests.sosl.classify_superchains

Asserts ``(n_plus, n_minus)`` for each fixture, the internal laws
``|n_plus - n_minus| <= 1`` and ``n >= 1 => m_plus == m_minus``, the duality
``n_plus(L) == n_minus(Lbar)``, and the witness consistency: strict R-descent of
stems, alternating signs, and each stem carrying a maximal chain of its level's
sign. Prints one OK line per fixture, or raises on the first mismatch.
"""
from __future__ import annotations

import os
from typing import Optional

from sosl.sos import Invariant, load_invariant
from sosl.sos.classify.chains import chains
from sosl.sos.classify.primitives import Green
from sosl.sos.classify.superchains import Superchain, superchains

_SOS = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir,
                    "samples", "fixtures", "hoa", "sos")

# (n_plus, n_minus) from research_notes/sos_classification.md section 9.
EXPECT = {"even": (0, 1), "gf_aa": (-1, 0), "evenblocks": (-1, 0)}


def _load(name: str) -> Invariant:
    with open(os.path.join(_SOS, name + ".sos")) as f:
        return load_invariant(f.read())


def _complement(inv: Invariant) -> Invariant:
    linked = inv.linked_pairs()
    return Invariant(inv.alphabet, inv.keys, inv.letter_class, inv.mult,
                     accept=frozenset(linked - inv.accept), identity=inv.identity)


def _check_witness(inv: Invariant, w: Optional[Superchain], m: int) -> None:
    if w is None:
        return
    g = Green.of(inv)
    cr = chains(inv)
    for a, b in zip(w.stems, w.stems[1:]):
        assert g.lt_r(b, a), (a, b)                       # strict R-descent
    for x, y in zip(w.signs, w.signs[1:]):
        assert x != y, w.signs                            # alternation
    for stem, sign in zip(w.stems, w.signs):
        bp, bn = cr.stem_best[stem]
        assert (bp if sign else bn) == m, (stem, sign, bp, bn, m)  # maximal chain


def check(name: str) -> None:
    inv = _load(name)
    cr = chains(inv)
    m = max(cr.m_plus, cr.m_minus)
    res = superchains(inv, cr)
    assert (res.n_plus, res.n_minus) == EXPECT[name], (name, res.n_plus, res.n_minus)
    assert abs(res.n_plus - res.n_minus) <= 1, (name, res.n_plus, res.n_minus)
    if max(res.n_plus, res.n_minus) >= 1:
        assert cr.m_plus == cr.m_minus, (name, cr.m_plus, cr.m_minus)
    _check_witness(inv, res.witness_plus, m)
    _check_witness(inv, res.witness_minus, m)

    dual = superchains(_complement(inv))
    assert (dual.n_plus, dual.n_minus) == (res.n_minus, res.n_plus), (name, dual.n_plus, dual.n_minus)
    print(f"OK {name}: (n+, n-)=({res.n_plus}, {res.n_minus})  dual OK")


def main() -> int:
    for name in EXPECT:
        check(name)
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
