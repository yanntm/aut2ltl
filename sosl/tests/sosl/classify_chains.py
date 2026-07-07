"""Chain numbers (C section 5) on the triptych, against the C section 9 values.

    python3 -m tests.sosl.classify_chains

Asserts ``(m_plus, m_minus)`` for each fixture, the internal law
``|m_plus - m_minus| <= 1``, the duality ``m_plus(L) == m_minus(Lbar)`` under
the complement flip of ``P``, and the internal consistency of each emitted
witness (linkage ``s.e_i = s``, strict H-descent, alternating bits, sign).
Prints one OK line per fixture, or raises on the first mismatch.
"""
from __future__ import annotations

import os
from typing import Optional

from sosl.sos import Invariant, load_invariant
from sosl.sos.classify.chains import Chain, chains
from sosl.sos.classify.primitives import lt_h_idem

_SOS = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir,
                    "samples", "fixtures", "hoa", "sos")

# (m_plus, m_minus) from research_notes/sos_classification.md section 9.
EXPECT = {"even": (0, 0), "gf_aa": (0, 1), "evenblocks": (1, 2)}


def _load(name: str) -> Invariant:
    with open(os.path.join(_SOS, name + ".sos")) as f:
        return load_invariant(f.read())


def _complement(inv: Invariant) -> Invariant:
    """The invariant of the complement: ``P`` flipped within the linked pairs."""
    linked = inv.linked_pairs()
    return Invariant(inv.alphabet, inv.keys, inv.letter_class, inv.mult,
                     accept=frozenset(linked - inv.accept), identity=inv.identity)


def _check_witness(inv: Invariant, w: Optional[Chain], sign_positive: bool) -> None:
    if w is None:
        return
    mult, accept = inv.mult, inv.accept
    for e in w.idems:
        assert mult[w.stem][e] == w.stem, (w.stem, e)          # linkage
        assert mult[e][e] == e, e                              # idempotent
    for a, b in zip(w.idems, w.idems[1:]):
        assert lt_h_idem(inv, b, a), (a, b)                    # strict H-descent
    for e, b in zip(w.idems, w.bits):
        assert ((w.stem, e) in accept) == b, (w.stem, e)       # bits match P
    for x, y in zip(w.bits, w.bits[1:]):
        assert x != y, w.bits                                  # alternation
    assert w.positive == w.bits[0] == sign_positive, w.bits    # sign is the top


def check(name: str) -> None:
    inv = _load(name)
    res = chains(inv)
    assert (res.m_plus, res.m_minus) == EXPECT[name], (name, res.m_plus, res.m_minus)
    assert abs(res.m_plus - res.m_minus) <= 1, (name, res.m_plus, res.m_minus)
    _check_witness(inv, res.witness_plus, True)
    _check_witness(inv, res.witness_minus, False)

    dual = chains(_complement(inv))
    assert (dual.m_plus, dual.m_minus) == (res.m_minus, res.m_plus), (name, dual.m_plus, dual.m_minus)
    print(f"OK {name}: (m+, m-)=({res.m_plus}, {res.m_minus})  dual OK")


def main() -> int:
    for name in EXPECT:
        check(name)
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
