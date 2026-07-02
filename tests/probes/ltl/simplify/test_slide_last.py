#!/usr/bin/env python3
"""
tests/probes/ltl/simplify/test_slide_last.py

Validation for the slide-to-last rule in fold_pass (`_slide_last`):

    r U ( h ∧ X(p U q) )  →  r U ( h ∧ Xq )    when p ⊨ h and h ⊨ r
    F ( h ∧ X(p U q) )    →  F ( h ∧ Xq )      (r = ⊤)
    r R ( h ∨ X(p R q) )  →  r R ( h ∨ Xq )    when h ⊨ p and r ⊨ h
    G ( h ∨ X(p R q) )    →  G ( h ∨ Xq )      (r = ⊥)

Harness contract as the other suites: PASS requires Spot-verified language
equivalence; expected shapes when given; must-not-change cases guard against
over-firing (weak inner arms, failed entailments, no eventual head).

Run from project root:
    python3 tests/probes/ltl/simplify/test_slide_last.py
"""

import sys

import spot

from aut2ltl.ltl.simplify.fold_pass import fold_simplify

# (input, expected or None, note)
CASES = [
    # the handoff instance (collapse_example's deep_anchor shape)
    ("F(b & X(b U !a))", "F(b & X!a)", "F head, p = h identity"),
    # generalized conjunct: p ⊨ h by the conjunct tier
    ("F(a & X((a & b) U c))", "F(a & Xc)", "p = a&b entails h = a"),
    # p ⊨ h by the BDD / disjunct tier
    ("F((a | b) & X(a U c))", "F((a | b) & Xc)", "p = a entails h = a|b"),
    # strong-until head, h ⊨ r
    ("(a | b) U (b & X(b U c))", "(a | b) U (b & Xc)",
     "U head: h = b entails r = a|b"),
    # the construction's 1 U spelling of F
    ("1 U (b & X(b U !a))", "1 U (b & X!a)", "U head with r = 1"),
    # duals
    ("G(a | X(a R b))", "G(a | Xb)", "G head, h = p identity"),
    ("(a & b) R (a | X(a R c))", "(a & b) R (a | Xc)",
     "R head: r = a&b entails h = a, h entails p"),
    # fires on the inner F node of a GF shape (DAG walk, no extra case)
    ("GF(b & X(b U c))", "GF(b & Xc)", "GF via the inner F node"),
    # must not change: NOT instances
    ("F(b & X(b W !a))", None, "weak inner arm (must not change)"),
    ("G(a | X(a M b))", None, "weak inner arm, dual (must not change)"),
    ("F(a & X(b U c))", None, "p = b does not entail h = a (must not change)"),
    ("G(a | X(b R c))", None, "h = a does not entail p = b (must not change)"),
    ("d U (b & X(b U c))", None, "h = b does not entail r = d (must not change)"),
    ("b & X(b U !a)", None,
     "no eventual head: the inner rewrite alone is unsound (must not change)"),
]

MUST_NOT_CHANGE = {src for src, exp, _ in CASES if exp is None}


def equiv(f: "spot.formula", g: "spot.formula") -> bool:
    try:
        return spot.are_equivalent(f, g)
    except AttributeError:
        a, b = f.translate(), g.translate()
        return spot.contains(a, b) and spot.contains(b, a)


def main() -> int:
    failures = 0
    for src, expected, note in CASES:
        f = spot.formula(src)
        out = fold_simplify(f)
        ok_equiv = equiv(f, out)
        ok_shape = True
        detail = ""
        if expected is not None:
            ok_shape = (out == spot.formula(expected))
            if not ok_shape:
                detail = f" expected={expected!r}"
        if src in MUST_NOT_CHANGE and out != f:
            ok_shape = False
            detail = " MUST-NOT-CHANGE but changed"
        status = "PASS" if (ok_equiv and ok_shape) else "FAIL"
        if status == "FAIL":
            failures += 1
        print(f"  {status}  [{note}] {src}")
        print(f"        -> {out}"
              f"{'' if ok_equiv else '  ** NOT EQUIVALENT **'}{detail}")
    print(f"\n{'CLEAN' if failures == 0 else f'{failures} FAILURE(S)'} "
          f"({len(CASES)} cases)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
