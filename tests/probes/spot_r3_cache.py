"""Probe: does Spot's tl_simplifier (our `_simp_f`, ~`ltlfilt -r3`) give a DIFFERENT
answer for the SAME formula depending on whether that formula's automaton was already
translated in-process? Reproduces the A/B leading-X divergence in ONE call, with no
reconstruction in the loop — the red-handed catch.

Hypothesis (from the trace): `-r3`'s semantic (language-containment) rules only fire
when the subformula's translation is already available in process-global Spot state;
cold they are skipped, so the leading `X` survives. A warm `f.translate()` primes that
state and the same `_simp_f` call then drops the `X`.

Usage (one process per case, so `cold` is truly cold):
    python3 -m tests.probes.spot_r3_cache cold   # _simp_f alone
    python3 -m tests.probes.spot_r3_cache warm   # f.translate() first, then _simp_f
"""
import sys

import spot

# The exact divergent node from term030 (X(a | FG(!b | X(!b M !c)))).
_F = "X(GF!b & F((!b & X(!b & XG(!b | X!c))) | (b & X(!c & G(!b | X!c)))))"


def _r3() -> "spot.tl_simplifier":
    """A tl_simplifier at ltlfilt -r3: basics + synt_impl + event_univ +
    containment_checks (the semantic language-inclusion rules that translate
    subformulas). A FRESH instance, so no accumulated cache of its own."""
    return spot.tl_simplifier(spot.tl_simplifier_options(True, True, True, True))


def main(mode: str) -> None:
    f = spot.formula(_F)
    print(f"[{mode}] built          : {f}")
    if mode == "warm":
        f.translate()                    # prime process-global Spot state; result discarded
        print(f"[{mode}] after translate: {f}")
    out = _r3().simplify(f)
    print(f"[{mode}] after -r3 simp  : {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "cold")
