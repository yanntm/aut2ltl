"""Per-cycle ω-blindness mechanism probe: which tier makes a language H5, and
a soundness check that `dual_scan.h5_hit` (first-group-only) did not overclaim.

    python3 -m tests.sos2ltl.e7_mechanism_probe <file.sos> [--hoa <D.hoa>]

For each period->1 cycle the probe reports, reusing the extractor's own ω scan
around *that* cycle (not just the first group `dual_scan` checks):

  * `ω-scan`   — SEPARATES (an ω-power certificate through this cycle) or
                 ω-constant (ω-blind through this cycle);
  * the mechanism **tier** of an ω-constant cycle — `right-ideal`
    (`C·λ(Σ) ⊆ C`) ⊊ `phase-collapse` (`(c·y)^π` phase-free) ⊊ `P-level`
    (ω-blind only because `P` cannot separate the phase-idempotents); for a
    P-level cycle it prints the witness suffix and the distinct-but-`P`-
    equivalent idempotents (paper F7 addendum's third mechanism).

Verdict: every cycle ω-constant ⟹ genuinely ω-blind (a real H5 hit), tagged
with the language's tier (its weakest cycle). Some cycle SEPARATES ⟹ an
ω-power certificate exists, so `dual_scan.h5_hit` overclaimed — an engine bug;
with `--hoa` the found ω family is replayed against `D` to confirm.
"""
from __future__ import annotations

import sys
from typing import FrozenSet, List, Optional

from aut2ltl.sos2ltl.witness import Family, toggles
from aut2ltl.sos2ltl.witness.extract import _scan_omega
from aut2ltl.sos2ltl.witness.mechanism import is_phase_collapse, is_right_ideal
from aut2ltl.sos2ltl.witness.spot_oracle import oracle_for_hoa
from sosl.sos import Invariant, load_invariant
from sosl.sos.classify.aperiodic import orbit

TIER_ORDER = {"right-ideal": 0, "phase-collapse": 1, "P-level": 2}


def _p_equivalent(inv: Invariant, d0: int, d1: int) -> bool:
    """Whether idempotents `d0`, `d1` are `P`-indistinguishable in every left
    context: `(x·d0, d0) ∈ P ⇔ (x·d1, d1) ∈ P` for all `x`."""
    return all(((inv.mult[x][d0], d0) in inv.accept)
               == ((inv.mult[x][d1], d1) in inv.accept)
               for x in range(inv.n))


def _p_level_witness(inv: Invariant, cyc: FrozenSet[int]) -> Optional[str]:
    """A suffix `y` breaking phase-collapse whose two escape idempotents are
    `P`-equivalent (so the cycle is ω-blind at the `P` level only), rendered,
    or None if the cycle phase-collapses."""
    ip = inv.idempotent_power
    for y in range(inv.n):
        idems = sorted({ip(inv.mult[c][y]) for c in cyc})
        if len(idems) > 1:
            pe = all(_p_equivalent(inv, idems[0], d) for d in idems[1:])
            return (f"y={y}: escape idempotents {idems} "
                    f"P-equivalent={pe}")
    return None


def _tier(inv: Invariant, cyc: FrozenSet[int]) -> str:
    if is_right_ideal(inv, cyc):
        return "right-ideal"
    if is_phase_collapse(inv, cyc):
        return "phase-collapse"
    return "P-level"


def main(argv: List[str]) -> int:
    path = argv[0]
    hoa = argv[argv.index("--hoa") + 1] if "--hoa" in argv else None
    with open(path) as f:
        inv = load_invariant(f.read())

    seen: set = set()
    any_sep: Optional[Family] = None
    worst = "right-ideal"
    print(f"{path}: |𝒞|={inv.n}  letters={list(inv.letter_class)}")
    for c in range(inv.n):
        o = orbit(inv, c)
        if o.period <= 1:
            continue
        cyc = frozenset(o.cycle)
        if cyc in seen:
            continue
        seen.add(cyc)
        fam = _scan_omega(inv, o)
        if fam is not None:
            any_sep = any_sep or fam
            print(f"  cycle {sorted(cyc)}  period={o.period}  ω-scan=SEPARATES")
            continue
        tier = _tier(inv, cyc)
        worst = max(worst, tier, key=lambda t: TIER_ORDER[t])
        line = f"  cycle {sorted(cyc)}  period={o.period}  ω-constant  tier={tier}"
        if tier == "P-level":
            line += f"  [{_p_level_witness(inv, cyc)}]"
        print(line)

    if any_sep is None:
        print(f"VERDICT: genuinely ω-blind (every group ω-constant) — real H5, "
              f"tier={worst}")
        return 0

    print("VERDICT: ω-power certificate EXISTS via a group — "
          "dual_scan.h5_hit OVERCLAIMED (first-group only)")
    if hoa is not None:
        ok = toggles(any_sep, oracle_for_hoa(hoa, inv.alphabet))
        print(f"  found ω family replays against D: "
              f"{'YES (confirms not ω-blind)' if ok else 'NO'}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
