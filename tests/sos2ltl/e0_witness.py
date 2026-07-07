"""Certificate extraction probe on one `.sos` invariant (E0/E7 sanity).

    python3 -m tests.sos2ltl.e0_witness <file.sos> [--expect gfaa|even|evenblocks]

Extracts the counting family (None on an aperiodic invariant), prints it,
and replays the toggle check against the invariant's own membership
read-off. With ``--expect`` asserts the paper's §4.3 canonical derivations
byte-exactly:

    even        F₁(u = a, v = a, x = (!a)^ω, p′ = 2)  — samples a^{n+1}·(!a)^ω
    evenblocks  F₂(u = ε, v = a, y = a·!a,   p′ = 2)  — samples (a^{n+1}·!a)^ω
    gfaa        no family (aperiodic)
"""
from __future__ import annotations

import sys
from typing import List

from aut2ltl.sos2ltl.witness import extract_family, toggles
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

    fam = extract_family(inv)
    if fam is None:
        print(f"{path}: aperiodic — no family")
        assert expect in (None, "gfaa"), expect
        print("OK")
        return 0

    shape = "omega-power" if fam.omega_power else "linear"
    print(f"{path}: {shape} family, p'={fam.period} pattern={fam.pattern}")
    print(f"  u = {render(inv, fam.u)}   v = {render(inv, fam.v)}")
    if fam.omega_power:
        print(f"  y = {render(inv, fam.y)}")
    else:
        print(f"  x = {render(inv, fam.x_prefix)};({render(inv, fam.x_loop)})^w")
    ok = toggles(fam, inv.member)
    print(f"  toggle check (2p'+1 = {2 * fam.period + 1} lassos): "
          f"{'REPLAYED' if ok else 'FAILED'}")
    assert ok, "family does not replay against the invariant"

    if expect == "even":
        assert not fam.omega_power and fam.period == 2, fam
        assert fam.u == (1,) and fam.v == (1,), fam
        assert fam.x_prefix == () and fam.x_loop == (0,), fam
        assert fam.pattern == (False, True), fam
    elif expect == "evenblocks":
        assert fam.omega_power and fam.period == 2, fam
        assert fam.u == () and fam.v == (1,) and fam.y == (1, 0), fam
        assert fam.pattern == (False, True), fam
    elif expect == "gfaa":
        raise AssertionError("gfaa must be aperiodic")
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
