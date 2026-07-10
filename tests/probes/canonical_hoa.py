"""dump_hoa is a normal form: forced transition-based, AP order canonical.

Three properties, each the negation of a way `to_str("hoa")` failed the corpus:

1. transition-based — `F a` is terminal, and the plain printer declares
   `state-acc` on it even after `prop_state_acc` was cleared.
2. AP-order invariant — the same automaton, with its atomic propositions
   registered in either order, serializes to the same bytes. This is what made
   `corpus/det/` differ between two Spot builds.
3. idempotent — reparsing a canonical dump and dumping it again is a fixpoint.

    python3 tests/probes/canonical_hoa.py
"""
from __future__ import annotations

import sys

import spot  # noqa: E402
import buddy  # noqa: E402

from aut2ltl.ltl.twa import dump_hoa  # noqa: E402


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


def _rotate_states(aut: "spot.twa_graph") -> "spot.twa_graph":
    """The same automaton with every state index shifted by one (mod n).

    A pure renumbering: same graph, same language, different indices — what a
    process-boundary round trip or a Spot minimization leaves behind.
    """
    n = aut.num_states()
    new = lambda s: (s + 1) % n                                     # noqa: E731
    res = spot.make_twa_graph(aut.get_dict())
    res.copy_ap_of(aut)
    res.copy_acceptance_of(aut)
    res.new_states(n)
    res.set_init_state(new(aut.get_init_state_number()))
    for e in aut.edges():
        res.new_edge(new(e.src), new(e.dst), e.cond, e.acc)
    res.prop_copy(aut, spot.twa_prop_set.all())
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

    # 3. state numbering cannot be observed.
    for f in ("F a & G b", "a U (b & X c)", "GF a & GF b", "G(a -> X b)"):
        d = _canonical(f)
        if d.num_states() < 2:
            print(f"  --  [states] {f}: single state, nothing to permute"); continue
        rot = _rotate_states(d)
        if d.to_str("hoa") == rot.to_str("hoa"):
            print(f"  ??  [states] {f}: plain printer already agreed (weak case)")
        if dump_hoa(d) != dump_hoa(rot):
            print(f"FAIL [states] {f}: canonical dump depends on state numbering")
            bad += 1
        else:
            print(f"  ok  [states] {f}: canonical bytes agree under renumbering")

    # 4. fixpoint.
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
