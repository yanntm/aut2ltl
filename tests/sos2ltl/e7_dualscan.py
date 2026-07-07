"""E7 dual-scan + presentation-agnostic replay probe on one invariant.

    python3 -m tests.sos2ltl.e7_dualscan <file.sos> [--hoa <input.hoa>]
                                          [--expect gfaa|even|evenblocks]

Runs both certificate scans to completion (`dual_scan`) and reports, per
shape, the first separating family or `all-constant` — the E7 datum for H5
(ω-power all-constant ⇒ a linear-only certificate). Then replays the
*canonical* family (`extract_family`) two ways: against the invariant's own
read-off (a labelled self-check), and — when `--hoa` is given — against the
input automaton by Spot membership only (`spot_oracle`), the portable check
that needs no algebra on the verifier side.

`--expect` asserts the paper's §4.3 split byte-exactly: `even` is
linear-separating / ω-all-constant (an H5 shape), `evenblocks` is
linear-all-constant / ω-separating, `gfaa` is aperiodic (no family).
"""
from __future__ import annotations

import sys
from typing import List, Optional

from aut2ltl.sos2ltl.witness import Family, dual_scan, extract_family, toggles
from aut2ltl.sos2ltl.witness.spot_oracle import oracle_for_hoa
from sosl.sos import load_invariant


def render(inv, word) -> str:
    parts = []
    for a in word:
        trues = inv.alphabet.true_aps(a)
        parts.append("&".join(p if p in trues else "!" + p
                              for p in inv.alphabet.aps))
    return ";".join(parts) or "eps"


def show(inv, fam: Optional[Family], shape: str) -> None:
    if fam is None:
        tag = "  [H5: linear-only certificate]" if shape == "omega" else ""
        print(f"    {shape:7s}: all-constant{tag}")
        return
    body = (f"y={render(inv, fam.y)}" if fam.omega_power
            else f"x={render(inv, fam.x_prefix)};({render(inv, fam.x_loop)})^w")
    print(f"    {shape:7s}: p'={fam.period} pattern={fam.pattern} "
          f"u={render(inv, fam.u)} v={render(inv, fam.v)} {body}  [SEPARATES]")


def main(argv: List[str]) -> int:
    path = argv[0]
    hoa: Optional[str] = None
    expect: Optional[str] = None
    i = 1
    while i < len(argv):
        if argv[i] == "--hoa":
            hoa = argv[i + 1]; i += 2
        elif argv[i] == "--expect":
            expect = argv[i + 1]; i += 2
        else:
            i += 1

    with open(path) as f:
        inv = load_invariant(f.read())

    ds = dual_scan(inv)
    if ds is None:
        print(f"{path}: aperiodic — no family")
        assert expect in (None, "gfaa"), expect
        print("OK")
        return 0

    print(f"{path}: group found; dual scan:")
    show(inv, ds.linear, "linear")
    show(inv, ds.omega, "omega")
    print(f"  h5_hit (ω all-constant) = {ds.h5_hit}")

    canon = extract_family(inv)
    assert canon is not None
    print(f"  canonical family (extract_family): "
          f"{'omega' if canon.omega_power else 'linear'}")

    member = oracle_for_hoa(hoa, inv.alphabet) if hoa is not None else None
    hoa_tag = hoa.split("/")[-1] if hoa is not None else None

    # Every separating family the dual scan reports must be a genuine
    # certificate — replay each against the read-off and (if given) the
    # input automaton by membership only.
    for shape, fam in (("linear", ds.linear), ("omega", ds.omega)):
        if fam is None:
            continue
        n = 2 * fam.period + 1
        ok_self = toggles(fam, inv.member)
        print(f"  replay {shape:7s} · read-off self-check      : "
              f"{'REPLAYED' if ok_self else 'FAILED'} ({n} lassos)")
        assert ok_self, f"{shape} family fails the read-off replay"
        if member is not None:
            ok_hoa = toggles(fam, member)
            print(f"  replay {shape:7s} · input-HOA ({hoa_tag}) : "
                  f"{'REPLAYED' if ok_hoa else 'FAILED'} ({n} lassos)")
            assert ok_hoa, f"{shape} family fails the input-automaton replay"

    if expect == "even":
        assert ds.linear is not None, ds
        assert ds.linear.u == (1,) and ds.linear.v == (1,), ds.linear
        assert ds.linear.x_prefix == () and ds.linear.x_loop == (0,), ds.linear
        assert ds.linear.pattern == (False, True), ds.linear
    elif expect == "evenblocks":
        assert ds.omega is not None, ds
        assert ds.omega.u == () and ds.omega.v == (1,) and ds.omega.y == (1, 0), ds.omega
        assert ds.omega.pattern == (False, True), ds.omega
    elif expect == "gfaa":
        raise AssertionError("gfaa must be aperiodic")
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
