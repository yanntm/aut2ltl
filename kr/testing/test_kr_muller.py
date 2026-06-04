#!/usr/bin/env python3
"""
kr/testing/test_kr_muller.py

Diagnostic for Muller acceptance handling vs current parity/SCC proxy.

Run from kr/ subdir or project:
  cd kr/testing
  python3 test_kr_muller.py

Explores:
- What Spot gives for get_acceptance() after different postprocess (parity, muller, etc.).
- Behavior of scc_info.is_rejecting_scc for different acc (including pure Muller).
- What our accepting_configs and _compute_good_muller_sets return.
- Whether we can support alpha that is general Muller (not just "SCC with acc" ).

This helps answer "what is stopping us from computing Muller ? for alpha not SCC"

All in kr/testing/ path, no /tmp, no long -c.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import spot

from kr import decompose_aut
from kr.reachability import _compute_good_muller_sets

def show_acc(aut, label):
    print(f"\n=== {label} ===")
    print("num_states:", aut.num_states())
    print("prop_deterministic:", aut.prop_deterministic())
    acc = aut.get_acceptance()
    print("get_acceptance():", acc)
    print("str(acc):", str(acc))
    try:
        print("acc.is_muller():", acc.is_muller())
    except:
        pass
    try:
        print("acc.is_parity():", acc.is_parity())
    except:
        pass
    try:
        si = spot.scc_info(aut)
        print("scc_count:", si.scc_count())
        for scci in range(si.scc_count()):
            rej = si.is_rejecting_scc(scci)
            states = [s for s in range(aut.num_states()) if si.scc_of(s) == scci]
            print(f"  SCC {scci}: rejecting={rej}, states={states}")
            # For Muller, may have more info?
    except Exception as e:
        print("scc_info err:", e)

def main():
    print("=== Muller diagnostic (pure kr path) ===")
    print("Project root:", PROJECT_ROOT)

    # Use a formula whose aut has interesting acc
    formulas = ["a", "Fa", "Ga", "G(p -> X q)", "F G a"]

    for fs in formulas:
        print(f"\n\n========== Formula: {fs} ==========")
        f = spot.formula(fs)

        # Loose translate (Buchi by default)
        aut_b = f.translate()
        show_acc(aut_b, "translate() default (Buchi-ish)")

        # Postprocess parity (what we force in decompose)
        aut_p = spot.postprocess(aut_b, "parity min even", "deterministic", "complete")
        show_acc(aut_p, "postprocess parity min even det complete (current kr norm)")

        # Try Muller postprocess (note: may not be supported as option in this Spot; try variants)
        for opt in ["Muller", "muller", "gen. Muller", "Muller,deterministic,complete"]:
            try:
                aut_m = spot.postprocess(aut_b, opt)
                show_acc(aut_m, f"postprocess {opt}")
                break
            except Exception as e:
                print(f"postprocess {opt} failed: {e}")

        # Try explicit Muller translate (Spot may use different)
        for t_opt in ["Muller", "muller"]:
            try:
                aut_mt = f.translate(t_opt)
                show_acc(aut_mt, f"translate({t_opt})")
                break
            except Exception as e:
                print(f"translate {t_opt} failed: {e}")

        # Other common postprocess to see resulting acc without forcing parity
        try:
            aut_dc = spot.postprocess(aut_b, "deterministic", "complete")
            show_acc(aut_dc, "postprocess deterministic complete (no parity)")
        except Exception as e:
            print("det complete post failed:", e)

        # Now, what our code does: decompose forces parity, then see good ms
        try:
            casc = decompose_aut(aut_b)  # will norm internally to parity
            print("\n--- After kr decompose_aut (internal parity norm) ---")
            print("casc num_levels:", casc.num_levels)
            acc_cfgs = casc.accepting_configs()
            print("accepting_configs():", acc_cfgs)
            good = _compute_good_muller_sets(casc)
            print("good_muller_sets (from _compute):", [set(m) for m in good])
        except Exception as e:
            print("decompose or good_ms err:", type(e).__name__, e)

    print("\n=== Observations / what stops Muller for non-SCC alpha ===")
    print("See code in cascade.py:accepting_configs and reachability.py:_compute_good_muller_sets")
    print(" - Always forces parity norm in decompose_aut -> loses original alpha structure.")
    print(" - Only special-cases 't'/'f' strings; else relies on scc_info.is_rejecting_scc + has_acc_on_cycle.")
    print(" - is_rejecting_scc is defined for parity/Buchi/Rabin etc.; for general Muller (inf sets of sets) it may not directly give the exact Muller family.")
    print(" - No code to take original aut.get_acceptance() as Muller sets and lift via h to configs.")
    print(" - good_Ms are always 'full non-rejecting SCCs as sets', not arbitrary subsets or exact Muller condition on configs.")
    print(" - For alpha that is 'not SCC' (general Muller where accepting depends on exact i.o. set, not just which SCC), scc-based is insufficient; need the full collection of good subsets of configs whose image under h is accepting in original alpha.")
    print(" - Paper requires Muller on *identical* semiautomaton (same Q/delta); Spot postprocess to parity can add states for completion/det.")

if __name__ == "__main__":
    main()
