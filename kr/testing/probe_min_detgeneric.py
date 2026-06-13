#!/usr/bin/env python3
"""kr/testing/probe_min_detgeneric.py — automaton-only minimal det-generic form.

CONTRACT: kr input is an automaton (HOA), not an LTL formula. The root AND-split
needs a DETERMINISTIC automaton in conjunctive (generic) acceptance, and kr's
census is acutely sensitive to its state count. This probe checks whether
AUTOMATON-ONLY operations (no formula translation) reach the minimal det-generic
form on the case that exposed the gap: GFa & FGb, where translating the FORMULA
gives 1 state (tree 313) but postprocess(det,generic) of its Büchi automaton
gives 2 states (tree 9.5e15).

We feed each candidate's output straight into reconstruct_decomposed-style
split+reconstruct and report the recombined tree size, so the winner is the
automaton pipeline that both minimizes AND keeps the census small.

    python3 kr/testing/probe_min_detgeneric.py
"""
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import spot
from kr import decompose_aut, reconstruct_ltl_paper_style
from kr.ltl_builders import _tree_size_f

CASES = ["GFa & FGb", "GFa & GFb", "Ga | Fb"]


def split_and_build(det):
    """AND-split det by top_conjuncts, kr each piece, recombine; return tree."""
    conj = det.acc().get_acceptance().top_conjuncts()
    if len(conj) < 2:
        casc = decompose_aut(det)
        return _tree_size_f(reconstruct_ltl_paper_style(casc))
    pieces = []
    for c in conj:
        sub = spot.automaton(det.to_str("hoa"))
        sub.set_acceptance(spot.acc_cond(det.num_sets(), c))
        spot.cleanup_acceptance_here(sub)
        pieces.append(reconstruct_ltl_paper_style(decompose_aut(sub)))
    return _tree_size_f(spot.formula.And(pieces))


def candidates(aut):
    """Automaton-only routes to a deterministic generic form. Each entry:
    (name, automaton-or-None)."""
    out = []
    d1 = spot.postprocess(aut, "deterministic", "generic")
    out.append(("postproc(det,generic)", d1))
    # re-run postprocess on the det form (idempotence / further reduction)
    out.append(("  +re-postproc(generic)", spot.postprocess(d1, "generic")))
    # SAT minimization of the deterministic automaton (state-count optimal for
    # the fixed acceptance), guarded — can be expensive / unavailable.
    try:
        m = spot.sat_minimize(d1)
        out.append(("  sat_minimize(d1)", m))
    except Exception as e:
        out.append((f"  sat_minimize ERR {str(e)[:40]}", None))
    # generic minimization helpers if present
    for fn_name in ("reduce_parity", "minimize_obligation"):
        fn = getattr(spot, fn_name, None)
        if fn is None:
            continue
        try:
            out.append((f"  {fn_name}(d1)", fn(d1)))
        except Exception as e:
            out.append((f"  {fn_name} ERR {str(e)[:40]}", None))
    return out


def main():
    for fs in CASES:
        print(f"=== {fs} ===")
        f = spot.formula(fs)
        aut = f.translate()  # stand-in for the HOA input
        print(f"  input Büchi: {aut.num_states()} st acc={aut.acc()}")
        # formula-translate reference (NOT contract-legal; baseline only)
        ref = spot.translate(f, "deterministic", "generic")
        ref_n = ref.num_states()
        print(f"  [ref] translate(formula,det,generic): {ref_n} st acc={ref.acc()}")

        # Phase 1: state-count census (NO kr build — building a non-minimal form
        # explodes, so we only inspect structure here).
        cands = [("[ref]", ref)] + candidates(aut)
        print("  -- state-count census (automaton-only routes) --")
        buildable = []
        for name, cand in cands:
            if cand is None:
                print(f"     {name}")
                continue
            det = cand.prop_universal().is_true()
            print(f"     {name}: {cand.num_states()} st acc={cand.acc()} det={det}")
            # Only build routes that are minimal (== ref state count) and det.
            if det and cand.num_states() <= ref_n:
                buildable.append((name, cand))

        # Phase 2: build only the minimal det routes (safe).
        print("  -- recombined tree for MINIMAL det routes --")
        for name, cand in buildable:
            try:
                t = time.monotonic()
                tree = split_and_build(cand)
                print(f"     {name}: tree={tree} ({time.monotonic()-t:.2f}s)")
            except Exception as e:
                print(f"     {name}: ERR {str(e)[:60]}")
        print()


if __name__ == "__main__":
    main()
