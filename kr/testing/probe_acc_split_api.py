#!/usr/bin/env python3
"""kr/testing/probe_acc_split_api.py — pin the Spot API for AND-by-acceptance-set.

One-shot: confirm (a) we can get a deterministic generalized-Büchi form of
GFa&GFb, (b) its acceptance is a top-level conjunction we can split with
top_conjuncts(), (c) we can rebuild per-conjunct sub-automata via
set_acceptance + cleanup. Prints what it finds; deletes itself from history
after the finding is recorded in STATUS/TODO.

    python3 kr/testing/probe_acc_split_api.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import spot


def show(tag, aut):
    print(f"--- {tag} ---")
    print(f"  acc        = {aut.acc()}")
    print(f"  num_sets   = {aut.num_sets()}")
    print(f"  num_states = {aut.num_states()}")
    print(f"  det?       = {aut.prop_universal().is_true()} (universal/det)")
    print(f"  is_gen_buchi = {aut.acc().is_generalized_buchi()}")


def main():
    f = spot.formula("GFa & GFb")

    # Route 1: default translate (gen Büchi, possibly nondeterministic)
    a1 = f.translate()
    show("translate() default", a1)

    # Route 2: deterministic generic
    a2 = spot.translate(f, "deterministic", "generic")
    show("translate(deterministic,generic)", a2)

    # Route 3: deterministic + force generalized Büchi acceptance if possible
    try:
        a3 = spot.translate(f, "deterministic", "tgba")
        show("translate(deterministic,tgba)", a3)
    except Exception as e:
        print(f"  tgba route err: {e}")
        a3 = None

    # top_conjuncts on the most promising deterministic one
    for tag, aut in [("a2", a2), ("a3", a3)]:
        if aut is None:
            continue
        print(f"=== top_conjuncts on {tag} ===")
        try:
            code = aut.acc().get_acceptance()
            conj = code.top_conjuncts()
            print(f"  top_conjuncts count = {len(conj)}")
            for i, c in enumerate(conj):
                print(f"    [{i}] {c}")
        except Exception as e:
            print(f"  top_conjuncts err: {repr(e)}")

    # Rebuild a per-conjunct sub-automaton from a2 (if it split)
    print("=== rebuild per-conjunct sub-automata (from a2) ===")
    try:
        conj = a2.acc().get_acceptance().top_conjuncts()
        for i, c in enumerate(conj):
            sub = spot.automaton(a2.to_str("hoa"))  # independent clone (HOA round-trip)
            sub.set_acceptance(spot.acc_cond(a2.num_sets(), c))
            spot.cleanup_acceptance_here(sub)
            print(f"  piece[{i}]: acc={sub.acc()} num_sets={sub.num_sets()} "
                  f"states={sub.num_states()}")
            # language check: piece i should equal GF(a) or GF(b)
            for probe in ("GFa", "GFb"):
                eq = spot.are_equivalent(sub, spot.translate(spot.formula(probe)))
                if eq:
                    print(f"      == {probe}")
    except Exception as e:
        import traceback
        print(f"  rebuild err: {repr(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
