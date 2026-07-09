"""The full classification record on the triptych + the duality gate (4.2).

    python3 -m tests.sosl.classify_record

For each fixture: assert the flat record (coordinates, rungs, phi) against the
C section 9 values, replay each chain witness lasso through ``Invariant.member``,
and run the duality gate — classify ``L`` and its complement, asserting the
coordinate/sign/rung swaps of spec section 4.2. Also smoke-tests the CLI entry
point. Prints one OK line per fixture, or raises on the first mismatch.
"""
from __future__ import annotations

import os

from sosl.sos import Invariant, load_invariant
from sosl.sos.classify import classify
from sosl.sos.classify.__main__ import main as cli_main
from sosl.sos.classify.witness import chain_lassos

_SOS = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir,
                    "samples", "fixtures", "hoa", "sos")

# name -> (aperiodic, stutter_invariant, phi_gamma, sign, (m+,m-,n+,n-))
# from C section 9; the triptych is stutter-sensitive throughout (an a/aa
# separation exists in each).
EXPECT = {
    "even":       (False, False, "1",       "sigma", (0, 0, 0, 1)),
    "gf_aa":      (True,  False, "omega",   "sigma", (0, 1, -1, 0)),
    "evenblocks": (False, False, "omega^2", "sigma", (1, 2, -1, 0)),
}


def _load(name: str) -> Invariant:
    with open(os.path.join(_SOS, name + ".sos")) as f:
        return load_invariant(f.read())


def _complement(inv: Invariant) -> Invariant:
    linked = inv.linked_pairs()
    return Invariant(inv.alphabet, inv.keys, inv.letter_class, inv.mult,
                     accept=frozenset(linked - inv.accept), identity=inv.identity)


_FLIP = {"sigma": "pi", "pi": "sigma", "delta": "delta"}


def _duality(inv: Invariant) -> None:
    a = classify(inv)
    b = classify(_complement(inv))
    assert (a.m_plus, a.m_minus) == (b.m_minus, b.m_plus)
    assert (a.n_plus, a.n_minus) == (b.n_minus, b.n_plus)
    assert b.sign == _FLIP[a.sign], (a.sign, b.sign)
    assert (a.rungs.open, a.rungs.dba) == (b.rungs.closed, b.rungs.dca)
    assert (a.rungs.closed, a.rungs.dca) == (b.rungs.open, b.rungs.dba)
    assert a.rungs.weak == b.rungs.weak
    assert str(a.gamma) == str(b.gamma), (a.gamma, b.gamma)  # gamma is self-dual


def check(name: str) -> None:
    inv = _load(name)
    rec = classify(inv)
    aper, stutter, gamma, sign, coords = EXPECT[name]
    assert rec.aperiodic == aper, (name, rec.aperiodic)
    assert rec.stutter_invariant == stutter, (name, rec.stutter_invariant)
    assert (rec.m_plus, rec.m_minus, rec.n_plus, rec.n_minus) == coords, (name, coords)
    assert rec.phi == (gamma, sign), (name, rec.phi)
    # Non-aperiodic cases ship a group witness (chain witness replay is already
    # asserted inside classify()).
    assert ("group" in rec.witnesses) == (not aper), name
    _duality(inv)
    print(f"OK {name}: phi=({gamma}, {sign})  aperiodic={aper}  "
          f"stutter_invariant={stutter}  duality OK")


def check_cli() -> int:
    rc = cli_main([os.path.join(_SOS, "even.sos")])
    assert rc == 0, rc
    print("OK cli exit 0 on even.sos")
    return 0


def main() -> int:
    for name in EXPECT:
        check(name)
    check_cli()
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
