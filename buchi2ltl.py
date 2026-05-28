#!/usr/bin/env python3
"""
Thin compatibility / CLI entry point for the BuchiToLTL prototype.

Most of the real code now lives in the `buchi2ltl/` package.
This file keeps backward compatibility for simple usage like:

    python3 buchi2ltl.py
    from buchi2ltl import reconstruct_ltl
"""

import spot

# Re-export the public API so old imports keep working
from buchi2ltl import reconstruct_ltl, try_absorb_size2_nonaccepting_scc

# Also keep the small helper that many experiments still use
def ltl_to_tgba(ltl_str):
    """Translate LTL → TGBA (same settings used by the reconstruction)."""
    f = spot.formula(ltl_str)
    aut = f.translate("GeneralizedBuchi", "Small", "High")
    return aut, f


# Simple manual test entry point (kept for convenience)
if __name__ == "__main__":
    test_cases = [
        "(p U q) & GF r",
        "FG a",
        "a U b",
        "G (p -> X p) & GF q",
        "X(p1 | F(p1 & Xp1))",   # interesting size-2 case
    ]

    for original_str in test_cases:
        print("\n" + "=" * 80)
        aut, _ = ltl_to_tgba(original_str)
        recovered, per_state = reconstruct_ltl(aut)

        print(f"Original LTL : {original_str}")
        print(f"States       : {aut.num_states()}")
        print(f"Recovered    : {recovered}")

        if recovered.startswith("UNSUPPORTED"):
            print("Status       : UNSUPPORTED")
        else:
            orig_f = spot.formula(original_str)
            rec_f = spot.formula(recovered)
            eq = spot.are_equivalent(orig_f, rec_f)
            print(f"Equivalent?  : {eq}")
