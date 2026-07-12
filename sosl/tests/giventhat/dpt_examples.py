"""The two worked examples of [DPT25], on the invariant — the paper's §6 numbers.

Derives, for each of the two `(¬φ, K)` pairs that [DPT25] draws as figures, every
number the paper states: the class counts of the two inputs, of the aligned
product, and of the reduced endpoints; the freedom `|F|`; the endpoint verdicts;
the Manna–Pnueli rung and the stutter bit of `¬φ`; and — since `|F|` is small on
the second pair — the class count of every member of the `2^F` lattice, hence the
true minimum.

`python3 -m tests.giventhat.dpt_examples` (from `sosl/`), no arguments.
"""
from __future__ import annotations

from itertools import combinations
from typing import Dict, List, Tuple

from sosl.sos.build import reference_of_ltl
from sosl.sos.calculus import Table
from sosl.sos.calculus.reduce import reduce
from tests.giventhat.ladder_gate import _extend
from sosl.sos.calculus.surgery import (
    complement,
    interior,
    is_cosafety,
    is_obligation,
    is_safety,
    safety_closure,
)
from sosl.sos.classify.stutter import is_stutter_invariant
from sosl.sos.giventhat import given_that, k_settles_phi, k_refutes_phi
from sosl.sos.giventhat.interval import Interval, choose
from sosl.sos.giventhat.ladder import is_persistence, is_recurrence

# The paper's §6. `fairness` is the headline: `¬φ` is the canonical generalized
# Büchi (two acceptance sets), `K` is [DPT25]'s own cheapest knowledge — the AP
# implication `a = [x>2]`, `b = [x>3]` (§7.2 there), which an SMT check on the
# proposition definitions settles without looking at the system at all. The other
# two are the instances [DPT25] draw as figures: Fig. 2/3 is their running
# example, Fig. 4 the stutter one (`A_XFa` given `K = ā`), whose lattice is small
# enough to enumerate whole.
EXAMPLES: List[Tuple[str, str, str]] = [
    ("fairness", "G F a & G F b", "G(b -> a)"),
    ("fig2-3", "F(a & c) | (G F b & G F !b)", "(F G b) & G c"),
    ("fig4", "X F a", "!a"),
]


def rung_of(table: Table, pairs: frozenset) -> str:
    """The Manna–Pnueli class of `L(pairs)`, lowest rung first."""
    if is_safety(table, pairs) and is_cosafety(table, pairs):
        return "clopen"
    if is_cosafety(table, pairs):
        return "guarantee"
    if is_safety(table, pairs):
        return "safety"
    if is_obligation(table, pairs):
        return "obligation"
    rec, per = is_recurrence(table, pairs), is_persistence(table, pairs)
    if rec and per:
        return "obligation"
    if rec:
        return "recurrence"
    if per:
        return "persistence"
    return "reactivity"


def classes_of(iv: Interval, pairs: frozenset) -> int:
    """`|𝒞|` of the language of `pairs` — the objective (paper §4.1)."""
    return reduce(iv.table, pairs, check=False).n


def lattice_census(iv: Interval, cap: int = 12) -> Dict[str, object]:
    """Class count of every member of the `2^F` lattice, when `|F| <= cap`."""
    if iv.bits > cap:
        return {"enumerated": False}
    counts: Dict[int, int] = {}
    best, best_at = None, None
    for size in range(iv.bits + 1):
        for pick in combinations(range(iv.bits), size):
            n = classes_of(iv, choose(iv, pick, check=False))
            counts[n] = counts.get(n, 0) + 1
            if best is None or n < best:
                best, best_at = n, pick
    return {"enumerated": True, "histogram": dict(sorted(counts.items())),
            "min": best, "argmin": best_at}


def report(tag: str, neg_phi_ltl: str, k_ltl: str) -> None:
    neg_phi = reference_of_ltl(neg_phi_ltl)
    k = reference_of_ltl(k_ltl)
    # Spot keeps only the APs a formula mentions; K may know fewer than ¬φ.
    # `_extend` is the sanctioned adapter (inverse_substitution + reduce).
    k = _extend(k, neg_phi.alphabet)
    iv = given_that(neg_phi, k)

    t_phi = Table.of(neg_phi)
    settles, w_settles = k_settles_phi(iv)
    refutes, w_refutes = k_refutes_phi(iv)

    print(f"\n=== [DPT25] {tag} ===")
    print(f"  ¬φ = {neg_phi_ltl}")
    print(f"  K  = {k_ltl}")
    print(f"  |𝒞(¬φ)| = {neg_phi.n}   linked {len(t_phi.linked)}   "
          f"rung {rung_of(t_phi, neg_phi.accept)}   "
          f"stutter-invariant {is_stutter_invariant(neg_phi)}")
    print(f"  |𝒞(K)|  = {k.n}   stutter-invariant {is_stutter_invariant(k)}")
    print(f"  |𝒞(T)|  = {iv.table.n}   linked {len(iv.table.linked)}   "
          f"bits |F| = {iv.bits}")
    print(f"  K settles φ: {settles}"
          + (f"   witness {w_settles.stem!r}.{w_settles.loop!r}^ω" if w_settles else ""))
    print(f"  K refutes φ: {refutes}"
          + (f"   witness {w_refutes.stem!r}.{w_refutes.loop!r}^ω" if w_refutes else ""))

    # The three reference points of paper §4.1: the input and the two endpoints.
    for name, pairs in (("P_¬φ (the input)", iv.p_neg_phi),
                        ("P_min = min|K", iv.p_min),
                        ("P_max = max|K", iv.p_max)):
        print(f"  |𝒞({name})| = {classes_of(iv, pairs)}   "
              f"rung {rung_of(iv.table, pairs)}   "
              f"stutter {is_stutter_invariant(reduce(iv.table, pairs, check=False))}")

    # The two topological hulls — the interior is the least guarantee member.
    hull = safety_closure(iv.table, iv.p_min)
    kern = interior(iv.table, iv.p_max)
    print(f"  ∃ safety B:    {hull <= iv.p_max}")
    print(f"  ∃ guarantee B: {iv.p_min <= kern}"
          + (f"   greatest = {classes_of(iv, kern)} classes" if iv.p_min <= kern else ""))

    census = lattice_census(iv)
    if census["enumerated"]:
        print(f"  2^F census ({2 ** iv.bits} members): "
              f"|𝒞| histogram {census['histogram']}   MIN = {census['min']}")
        best = choose(iv, census["argmin"], check=False)  # type: ignore[arg-type]
        print(f"  the minimum is rung {rung_of(iv.table, best)}, "
              f"stutter {is_stutter_invariant(reduce(iv.table, best, check=False))}, "
              f"= P_max: {best == iv.p_max}, = P_¬φ: {best == iv.p_neg_phi}")
    else:
        print(f"  2^F census: skipped ({2 ** iv.bits} members — beyond the cap)")
    # The three-class floor (paper Lemma 4.6): no member is ∅ or Σ^ω unless an
    # endpoint check fires, so every member has at least 3 classes.
    print(f"  three-class floor applies: {not settles and not refutes}")


def main() -> None:
    import sys
    argv = sys.argv[1:]
    if len(argv) == 3 and argv[0] == "--pair":
        report("adhoc", argv[1], argv[2])
        return
    for tag, neg_phi, k in EXAMPLES:
        report(tag, neg_phi, k)


if __name__ == "__main__":
    main()
