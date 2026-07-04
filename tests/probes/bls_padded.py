"""Run the bls cascade on a PADDED form, bypassing the normalization that
would strip it — the (A)-vs-(B) discriminating experiment.

A padded fixture (e.g. gfa_pad2.hoa: GFa product an acceptance-inert
position-parity bit) has a star-free language but a non-LTL per-state
recurrence question. The normal path can never see it: decompose_aut
re-postprocesses its input ("parity min even" / "deterministic" / "complete" /
"sbacc"), and the reduction merges the padding's bisimilar phases — so even a
Language mock answering the padded form gets stripped one call later. This
probe therefore replicates decompose_aut BELOW its postprocess line
(determinism check, generator extraction, GAP decomposition, context fields)
on the input verbatim, then:

  1. shows what postprocess would have done (the stripping, as evidence);
  2. grounds every Fin(C) sub-term against its config-level semantics;
  3. runs the ungated cascade dispatch and checks the assembled formula
     against the input.

(B) predicts wrong per-Fin sub-terms on the padded orbit but a correct total
(the acceptance is phase-saturated by construction); (A)-only predicts a
wrong total.

Usage:  python3 tests/probes/bls_padded.py <file.hoa>
Exit 0 total equivalent, 1 not, 2 build failed.
"""
import sys
from typing import Tuple

import buddy
import spot

from aut2ltl.bls.cascade import CascadeHolder
from aut2ltl.bls.gap import decompose_gens
from aut2ltl.bls.generators import extract_generators, is_deterministic
from aut2ltl.bls.hierarchy_class import make_hierarchy_class


def build_cascade_unstripped(aut: "spot.twa_graph"):
    """decompose_aut minus its spot.postprocess: the input IS the working D."""
    assert is_deterministic(aut), "padded fixture must already be deterministic"
    gens, masks, valuations = extract_generators(aut, max_aps=5)
    casc = decompose_gens(gens)
    casc.aps = [str(ap) for ap in aut.ap()]
    casc.letter_masks = masks
    casc.letter_valuations = valuations
    casc.original_aut = aut
    return casc


def gt_fin_automaton(casc, c0: Tuple[int, ...]) -> "spot.twa_graph":
    """Configuration automaton, acceptance Fin(0), marks leaving config c0."""
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


def main(path: str) -> int:
    aut = spot.automaton(path)
    stripped = spot.postprocess(aut, "parity min even", "deterministic",
                                "complete", "sbacc")
    print(f"input: {aut.num_states()} states; postprocess would leave "
          f"{stripped.num_states()} (the padding it strips)")

    casc = build_cascade_unstripped(aut)
    print(f"cascade: {casc.num_levels} level(s), configs {casc.all_configs()}")

    from aut2ltl.bls.operators.fin import fin_c
    holder = CascadeHolder(casc)
    for c in casc.all_configs():
        q = casc.state_of(c)
        f = fin_c(c, holder)
        gt = gt_fin_automaton(casc, c)
        fa = spot.translate(f)
        if spot.are_equivalent(fa, gt):
            print(f"  Fin({c}) [pi->{q}]: EQUIVALENT")
        else:
            mw = spot.product(gt, spot.complement(fa)).accepting_word()
            ew = spot.product(fa, spot.complement(gt)).accepting_word()
            print(f"  Fin({c}) [pi->{q}]: DIFFERS  misses: {mw}   extra: {ew}")

    res = make_hierarchy_class()(CascadeHolder(casc))
    print("ok       :", res.ok)
    print("technique:", res.technique_str())
    if not (res.ok and res.formula is not None):
        print("diagnosis:", res)
        return 2
    print("formula  :", res.formula)
    fa = res.formula.translate()
    eq = spot.are_equivalent(fa, aut)
    print("TOTAL EQUIVALENT to padded input:", eq)
    if not eq:
        mw = spot.product(aut, spot.complement(fa)).accepting_word()
        ew = spot.product(fa, spot.complement(aut)).accepting_word()
        print(f"  formula misses (in L, not in formula): {mw}")
        print(f"  formula extra  (in formula, not in L): {ew}")
    if len(sys.argv) > 2:
        ref = spot.translate(sys.argv[2])
        print(f"input  == reference '{sys.argv[2]}':",
              spot.are_equivalent(aut, ref))
        print(f"output == reference '{sys.argv[2]}':",
              spot.are_equivalent(fa, ref))
    return 0 if eq else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
