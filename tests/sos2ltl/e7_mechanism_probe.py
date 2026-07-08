"""Soundness probe for an H5 verdict: scan ω-power contexts around EVERY
period->1 group, not just the first (which is all `dual_scan` checks).

    python3 -m tests.sos2ltl.e7_mechanism_probe <file.sos> [--hoa <D.hoa>]

For each period->1 cycle: its right-ideal status (Prop 4.5) and whether an
ω-power context separates *that* group (reusing the extractor's own ω scan).
Verdict:
  * every cycle ω-constant ⟹ genuinely ω-blind — a real H5 hit; if some cycle
    is NOT a right ideal, that is a second ω-blindness mechanism (bring back);
  * some cycle ω-separates ⟹ an ω-power certificate exists after all, so the
    language is NOT ω-blind and `dual_scan.h5_hit` (first-group-only) overclaimed
    — an engine bug. With `--hoa`, the found ω family is replayed against D.
"""
from __future__ import annotations

import sys
from typing import List, Optional

from aut2ltl.sos2ltl.witness import Family, toggles
from aut2ltl.sos2ltl.witness.extract import _scan_omega
from aut2ltl.sos2ltl.witness.mechanism import is_right_ideal
from aut2ltl.sos2ltl.witness.spot_oracle import oracle_for_hoa
from sosl.sos import load_invariant
from sosl.sos.classify.aperiodic import orbit


def main(argv: List[str]) -> int:
    path = argv[0]
    hoa = argv[argv.index("--hoa") + 1] if "--hoa" in argv else None
    with open(path) as f:
        inv = load_invariant(f.read())

    seen = set()
    any_sep: Optional[Family] = None
    print(f"{path}: |𝒞|={inv.n}  letters={list(inv.letter_class)}")
    for c in range(inv.n):
        o = orbit(inv, c)
        if o.period <= 1:
            continue
        cyc = frozenset(o.cycle)
        if cyc in seen:
            continue
        seen.add(cyc)
        ri = is_right_ideal(inv, cyc)
        fam = _scan_omega(inv, o)
        sep = "SEPARATES" if fam is not None else "ω-constant"
        print(f"  cycle {sorted(cyc)}  period={o.period}  "
              f"right-ideal={ri}  ω-scan={sep}")
        if fam is not None and any_sep is None:
            any_sep = fam

    if any_sep is None:
        print("VERDICT: genuinely ω-blind (every group ω-constant) — real H5")
        return 0

    print("VERDICT: ω-power certificate EXISTS via a later group — "
          "dual_scan.h5_hit OVERCLAIMED (first-group only)")
    if hoa is not None:
        ok = toggles(any_sep, oracle_for_hoa(hoa, inv.alphabet))
        print(f"  found ω family replays against D: "
              f"{'YES (confirms not ω-blind)' if ok else 'NO'}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
