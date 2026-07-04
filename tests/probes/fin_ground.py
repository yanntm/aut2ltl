"""Ground each Fin(C) sub-formula of a cascade build against its true semantics.

For one HOA input: decompose to a cascade, emit Fin(C) for every reachable
config C, and compare each against a ground-truth automaton built on D's
semiautomaton ("the run visits pi(C) finitely often" = co-Buchi with marks on
the transitions leaving pi(C)). Also checks the Buchi assembly
OR_{C accepting} !Fin(C) against D itself. Localizes which sub-terms a
group-bearing (off-theorem) cascade gets wrong and whether the acceptance
combination cancels the error.

Usage:  python3 tests/probes/fin_ground.py <file.hoa>
Exit 0 if every sub-term and the assembly are equivalent, 1 otherwise.
"""
import sys
from typing import Tuple

import spot

from aut2ltl.language import Language
from aut2ltl.bls.gap import decompose_aut
from aut2ltl.bls.cascade.holder import CascadeHolder
from aut2ltl.bls.gate.aperiodic import label_ltl_definable
from aut2ltl.bls.operators.fin import fin_c


import buddy


def gt_fin_automaton(casc: "Cascade", c0: Tuple[int, ...]) -> "spot.twa_graph":
    """The configuration automaton with acceptance Fin(0), mark on transitions
    leaving config c0 — the exact Lemma-7 semantics of Fin(c0)."""
    d = casc.original_aut
    configs = casc.all_configs()
    idx = {c: i for i, c in enumerate(configs)}
    gt = spot.make_twa_graph(d.get_dict())
    gt.copy_ap_of(d)
    gt.new_states(len(configs))
    gt.set_init_state(idx[casc.config_of(d.get_init_state_number())])
    gt.set_acceptance(1, "Fin(0)")
    for c in configs:
        for li in range(casc.num_letters()):
            cond = buddy.bddtrue
            for ap, pos in casc.letter_valuations[li].items():
                v = buddy.bdd_ithvar(gt.register_ap(spot.formula.ap(ap)))
                cond &= v if pos else buddy.bdd_not(v)
            gt.new_edge(idx[c], idx[casc.move_config(c, li)], cond,
                        [0] if c == c0 else [])
    return gt


def compare(name: str, formula: "spot.formula", gt: "spot.twa_graph") -> bool:
    fa = spot.translate(formula)
    if spot.are_equivalent(fa, gt):
        print(f"  {name}: EQUIVALENT")
        return True
    missed = spot.product(gt, spot.complement(fa))  # words GT accepts, formula misses
    extra = spot.product(fa, spot.complement(gt))   # words formula accepts, GT rejects
    mw = missed.accepting_word()
    ew = extra.accepting_word()
    print(f"  {name}: DIFFERS  formula-misses: {mw}   formula-extra: {ew}")
    return False


def main(path: str) -> int:
    casc = decompose_aut(spot.automaton(path))
    holder = CascadeHolder(casc)
    d = casc.original_aut
    print(f"== D ({d.num_states()} states):")
    print(d.to_str("hoa"))

    ok = True
    acc_disj = spot.formula.ff()
    for c in casc.all_configs():
        q = casc.state_of(c)
        f = fin_c(c, holder)
        accepting = q is not None and d.state_is_accepting(q)
        tag = f"Fin({c}) [pi->{q}{' ACC' if accepting else ''}]"
        gt = gt_fin_automaton(casc, c)
        match = compare(tag, f, gt)
        ok = match and ok
        # LTL-definability of the GT language itself: a matching build certifies
        # LTL (the sub-term IS an LTL formula); the screen adds the form reading.
        definable, _ = label_ltl_definable(Language.of(gt))
        screen = {True: "aperiodic", False: "group", None: "screen-blocked"}[definable]
        cert = "LTL (certified by match)" if match else "unknown"
        print(f"      GT language: screen={screen}; {cert}")
        if accepting:
            acc_disj = spot.formula.Or([acc_disj, spot.formula.Not(f)])

    print("== assembly: OR over accepting configs of !Fin(C) vs D")
    fa = spot.translate(acc_disj)
    eq = spot.are_equivalent(fa, d)
    print(f"  assembly: {'EQUIVALENT' if eq else 'DIFFERS'}")
    return 0 if (ok and eq) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
