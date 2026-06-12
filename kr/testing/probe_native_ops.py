#!/usr/bin/env python3
"""
kr/testing/probe_native_ops.py

Pre-implementation probe for TODO item 1b (native G/R/W/X operator basis).
Answers, with evidence, BEFORE any builder change:

A. What do Spot's formula constructors already rewrite trivially?
   (U(1,x) -> F? Not(Not(x)) -> x? Not(U(..)) stays raw? Not(X(..))?)
B. Does the CURRENT per-node simplifier (_simp_f, hybrid policy) already
   convert the G-sugar !(1 U !x) into native G on small nodes? Same question
   for the basics-only simplifier (what big nodes get under hybrid).
C. Census on real reconstruct outputs: how many Not nodes sit over a
   U-rooted (or And/Or-of-U) child — the population an NNF-pushing _Not
   would rewrite into native R/G/W — and how many distinct U eventualities
   (the Couvreur acc-set driver) the output carries today.

Run from project root:
    python3 kr/testing/probe_native_ops.py            # default case list
    python3 kr/testing/probe_native_ops.py "GFa" ...  # specific cases
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import spot

from kr.ltl_builders import _simp_f, _get_tl_simp, _tt, _ap, _Not, _U, _X


def part_a():
    print("=== A. constructor trivial-rewrite behavior ===")
    a, b = _ap("a"), _ap("b")
    checks = [
        ("U(1, a)", _U(_tt(), a)),
        ("Not(U(a, b))", _Not(_U(a, b))),
        ("Not(U(1, Not(a)))  [the G-sugar]", _Not(_U(_tt(), _Not(a)))),
        ("Not(Not(a))", _Not(_Not(a))),
        ("Not(X(a))", _Not(_X(a))),
        ("formula.F(a) native", spot.formula.F(a)),
        ("formula.G(a) native", spot.formula.G(a)),
        ("formula.R(a, b) native", spot.formula.R(a, b)),
        ("formula.W(a, b) native", spot.formula.W(a, b)),
    ]
    for label, f in checks:
        print(f"  {label:38s} -> kind={f.kindstr():6s} str={f}")


def part_b():
    print("\n=== B. does the current simplifier already de-sugar? ===")
    a = _ap("a")
    g_sugar = _Not(_U(_tt(), _Not(a)))          # !(1 U !a) == Ga
    r_sugar = _Not(_U(_ap("b"), _Not(a)))        # !(b U !a) == !b R a
    for label, f in (("G-sugar !(1 U !a)", g_sugar), ("R-sugar !(b U !a)", r_sugar)):
        full = _get_tl_simp(True).simplify(f)
        basic = _get_tl_simp(False).simplify(f)
        via_simp_f = _simp_f(f)
        print(f"  {label}:")
        print(f"    full simplifier   -> kind={full.kindstr():6s} str={full}")
        print(f"    basics simplifier -> kind={basic.kindstr():6s} str={basic}")
        print(f"    _simp_f (hybrid)  -> kind={via_simp_f.kindstr():6s} str={via_simp_f}")


def census(f: "spot.formula") -> dict:
    """Sharing-aware walk: node kinds, Not-children kinds, distinct eventualities."""
    seen = set()
    stack = [f]
    kinds = {}
    not_child_kinds = {}
    n_u_evt = 0          # distinct U/M nodes = Couvreur acc-set proxy
    g_sugar = 0          # Not whose child is U(1, Not-or-other) — would become G/R
    while stack:
        g = stack.pop()
        gid = g.id()
        if gid in seen:
            continue
        seen.add(gid)
        k = g.kindstr()
        kinds[k] = kinds.get(k, 0) + 1
        if k in ("U", "M"):
            n_u_evt += 1
        if k == "Not":
            ck = g[0].kindstr()
            not_child_kinds[ck] = not_child_kinds.get(ck, 0) + 1
            if ck == "U" and g[0][0].is_tt():
                g_sugar += 1
        for child in g:
            stack.append(child)
    return {"kinds": kinds, "not_child_kinds": not_child_kinds,
            "distinct_U_or_M": n_u_evt, "not_over_F_shaped_U": g_sugar,
            "unique_nodes": len(seen)}


def part_c(cases):
    print("\n=== C. census of real reconstruct outputs ===")
    from kr import decompose_aut
    from kr.reachability import reconstruct_ltl_paper_style
    for case in cases:
        f = spot.formula(case)
        casc = decompose_aut(f.translate())
        res = reconstruct_ltl_paper_style(casc)
        st = census(res)
        print(f"  case '{case}' ({casc.num_levels}L, {st['unique_nodes']} DAG nodes):")
        print(f"    node kinds          : {dict(sorted(st['kinds'].items(), key=lambda kv: -kv[1]))}")
        print(f"    Not-over-child kinds: {dict(sorted(st['not_child_kinds'].items(), key=lambda kv: -kv[1]))}")
        print(f"    distinct U/M (acc-set proxy): {st['distinct_U_or_M']}")
        print(f"    Not over F-shaped U (pure G-sugar): {st['not_over_F_shaped_U']}")


if __name__ == "__main__":
    cases = sys.argv[1:] or ["Fa", "GFa", "a U b", "G(a -> Xb)"]
    part_a()
    part_b()
    part_c(cases)
