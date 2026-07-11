"""Read-off layer (C sections 7-8) against the C section 9 triptych records.

    python3 -m tests.sosl.classify_readoff

Runs the chain + superchain engines on the three fixtures, feeds the four
integers through ``read_off``, and asserts mu, sign, gamma, the parity/boolean
lengths, and the rung flags against the hand-verified C section 9 table. Also
exercises the ``Ordinal`` arithmetic and rendering directly. Prints one OK line
per case, or raises on the first mismatch.
"""
from __future__ import annotations

import os

from sosl.sos import load_invariant
from sosl.sos.classify.chains import chains
from sosl.sos.classify.readoff import Ordinal, read_off
from sosl.sos.classify.superchains import superchains

_SOS = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir,
                    "samples", "fixtures", "hoa", "sos")

# name -> (mu_str, sign, gamma_str, parity_len, co_parity_len,
#          open, closed, weak, dba, dca)   from C section 9.
EXPECT = {
    "even":       ("1",       "sigma", "1",       1, 1, True,  False, True,  True,  True),
    "gf_aa":      ("omega",   "sigma", "omega",   1, 2, False, False, False, True,  False),
    "evenblocks": ("omega^2", "sigma", "omega^2", 2, 3, False, False, False, False, False),
}


def check_ordinal() -> None:
    assert str(Ordinal.term(2, 1)) == "omega^2"
    assert str(Ordinal.term(1, 3)) == "omega*3"
    assert str(Ordinal.finite(1)) == "1"
    # omega+1, and omega*2 + omega = omega*3 (equal leading exponents merge).
    assert str(Ordinal.term(1, 1) + Ordinal.finite(1)) == "omega+1"
    assert str(Ordinal.term(1, 2) + Ordinal.term(1, 1)) == "omega*3"
    # omega^2+omega (kept, strictly larger exponent survives).
    assert str(Ordinal.term(2, 1) + Ordinal.term(1, 1)) == "omega^2+omega"
    print("OK Ordinal arithmetic + rendering")


def check(name: str) -> None:
    with open(os.path.join(_SOS, name + ".sos")) as f:
        inv = load_invariant(f.read())
    cr = chains(inv)
    sr = superchains(inv, cr)
    r = read_off(cr.m_plus, cr.m_minus, sr.n_plus, sr.n_minus)
    (mu, sign, gamma, plen, colen, op, cl, wk, dba, dca) = EXPECT[name]
    assert str(r.mu) == mu, (name, str(r.mu), mu)
    assert r.sign == sign, (name, r.sign, sign)
    assert r.gamma is not None and str(r.gamma) == gamma, (name, r.gamma)
    assert not r.needs_derivative, name
    assert (r.parity_length, r.co_parity_length) == (plen, colen), (name, r.parity_length, r.co_parity_length)
    assert (r.rungs.open, r.rungs.closed, r.rungs.weak, r.rungs.dba, r.rungs.dca) == (op, cl, wk, dba, dca), name
    print(f"OK {name}: mu={mu} gamma={gamma} sign={sign} "
          f"parity=({plen},{colen}) rungs(o,c,w,dba,dca)=({op},{cl},{wk},{dba},{dca})")


def main() -> int:
    check_ordinal()
    for name in EXPECT:
        check(name)
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
