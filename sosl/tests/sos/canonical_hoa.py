"""dump_hoa is a normal form: forced transition-based, AP order canonical.

Three properties, each the negation of a way `to_str("hoa")` failed the corpus:

1. transition-based — `F a` is terminal, and the plain printer declares
   `state-acc` on it even after `prop_state_acc` was cleared.
2. AP-order invariant — the same automaton, with its atomic propositions
   registered in either order, serializes to the same bytes. This is what made
   `corpus/det/` differ between two Spot builds.
3. idempotent — reparsing a canonical dump and dumping it again is a fixpoint.

    python3 sosl/tests/sos/canonical_hoa.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

import spot  # noqa: E402
import buddy  # noqa: E402

from sosl.sos.io import dump_hoa  # noqa: E402


def _loop(order: "list[str]") -> "spot.twa_graph":
    """`G(a & !b)` as a one-state automaton, its APs registered in `order`.

    Each call gets a fresh bdd dict, because the registration order the HOA
    printer indexes lives in the dict, not in the automaton — which is why two
    Spot builds wrote different bytes for one automaton, and why a single parse
    inside one process cannot reproduce it (the dict is already populated).
    """
    res = spot.make_twa_graph(spot.make_bdd_dict())
    var = {name: res.register_ap(name) for name in order}
    res.new_states(1)
    res.set_init_state(0)
    res.set_acceptance(spot.acc_cond(1, "Inf(0)"))
    cond = buddy.bdd_ithvar(var["a"]) & -buddy.bdd_ithvar(var["b"])
    res.new_edge(0, 0, cond, [0])
    return res


def _canonical(formula: str) -> "spot.twa_graph":
    """What importer.canonical() hands the corpus writers."""
    d = spot.translate(formula, "generic", "deterministic", "complete")
    d.prop_state_acc(spot.trival_maybe())
    return d


def main() -> int:
    bad = 0

    # 1. transition-based, always.
    for f in ("F a", "G a", "F a & G b", "GF a & GF b", "a U (b & X c)"):
        d = _canonical(f)
        plain, canon = d.to_str("hoa"), dump_hoa(d)
        if "state-acc" in canon:
            print(f"FAIL [t] {f}: canonical dump declares state-acc"); bad += 1
        if "state-acc" in plain and "state-acc" not in canon:
            print(f"  ok  [t] {f}: plain printer said state-acc, canonical does not")
        elif "state-acc" not in plain:
            print(f"  ok  [t] {f}: neither declares state-acc")

    # 2. AP declaration order cannot be observed.
    ab, ba = _loop(["a", "b"]), _loop(["b", "a"])
    # The fixtures hold distinct bdd dicts by construction, so they cannot be
    # compared to each other directly; reparse each canonical dump into the
    # default dict and check both denote G(a & !b).
    ref = spot.translate("G(a & !b)")
    for tag, aut in (("a,b", ab), ("b,a", ba)):
        if not spot.are_equivalent(spot.automaton(dump_hoa(aut)), ref):
            print(f"FAIL [ap] fixture {tag} is not G(a & !b) — bad test"); bad += 1
    if ab.to_str("hoa") == ba.to_str("hoa"):
        print("  ??  [ap] plain printer already agrees — fixture no longer bites")
    else:
        print("  ok  [ap] plain bytes differ (the corpus's divergence)")
    if dump_hoa(ab) != dump_hoa(ba):
        print("FAIL [ap] canonical dump depends on AP declaration order"); bad += 1
    else:
        print("  ok  [ap] canonical bytes agree")

    # 3. fixpoint.
    for f in ("F a", "F a & G b", "a U (b & X c)"):
        once = dump_hoa(_canonical(f))
        twice = dump_hoa(spot.automaton(once))
        if once != twice:
            print(f"FAIL [idem] {f}: dump_hoa is not a fixpoint"); bad += 1
        else:
            print(f"  ok  [idem] {f}")

    print("SUCCESS" if not bad else f"FAIL: {bad} property violation(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
