"""Evaluate the Π₂-hunt predicate P1 ∧ P2 ∧ P3 on ONE deterministic ω-automaton.

The predicate flags an automaton `D` that would refute the conjecture "a
state-minimal automaton with a star-free language has every recurrence
sub-question `Inf(C)` star-free":

  P1  L(D) is star-free (LTL-definable)          -- oracle verdict is LTL
  P2  D is state-minimal within its class        -- num_states equals the
                                                     SAT-min-backed count of
                                                     Language.det_generic_minimal
  P3  some config C has Inf(C) NON-star-free      -- the cascade grounds a
                                                     config whose Fin(C)/Inf(C)
                                                     language reads as carrying a
                                                     group (screen != aperiodic)

A HIT is P1 ∧ P2 ∧ P3. Anything else is a near-miss, tagged with every arm that
vetoed it (P1-fail / P2-fail / P3-none), plus the counts, so a sweep can build a
death histogram. On a HIT the offending configs and the ungated-cascade
assembled-output verdict are printed as well.

Usage:  python3 tests/pi2_hunt/predicate.py <file.hoa>
Exit 0 on HIT, 1 on near-miss, 2 on a build/decomposition error.
"""
from __future__ import annotations

import sys
from typing import Dict, List, Optional, Tuple

import spot
import buddy

from aut2ltl.language import Language
from aut2ltl.bls.gap import decompose_gens
from aut2ltl.bls.generators import extract_generators, is_deterministic
from aut2ltl.bls.gate.aperiodic import label_ltl_definable
from aut2ltl.bls.definability.oracle import decide, LTL, NOT_LTL
from aut2ltl.bls.aut2cas import as_translator
from aut2ltl.bls.hierarchy_class import make_hierarchy_class


def build_cascade_unstripped(aut: "spot.twa_graph") -> "object":
    """Build the holonomy cascade on `aut` VERBATIM -- decompose_aut minus its
    spot.postprocess. decompose_aut re-normalizes ("parity min even" / complete /
    sbacc) and thereby PADS a minimal input into a larger form on which a group can
    appear; grounding unstripped keeps the configs on the minimal target automaton,
    which is what the conjecture is about. Requires deterministic complete input."""
    assert is_deterministic(aut), "input must be deterministic"
    gens, masks, valuations = extract_generators(aut, max_aps=5)
    casc = decompose_gens(gens)
    casc.aps = [str(ap) for ap in aut.ap()]
    casc.letter_masks = masks
    casc.letter_valuations = valuations
    casc.original_aut = aut
    return casc


def _gt_fin_automaton(casc: "object", c0: Tuple[int, ...]) -> "spot.twa_graph":
    """The configuration semiautomaton with acceptance Fin(0), a mark on every
    transition leaving config c0 -- the exact Lemma-7 language of Fin(c0); its
    star-freeness equals that of Inf(c0) (the star-free class is complement-closed)."""
    d = casc.original_aut
    configs = casc.all_configs()
    idx: Dict[Tuple[int, ...], int] = {c: i for i, c in enumerate(configs)}
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


def eval_p1(aut: "spot.twa_graph") -> Tuple[bool, str]:
    """P1: is L(aut) star-free? Returns (holds, oracle-answer-string)."""
    v = decide(Language.of(aut))
    return (v.answer == LTL, str(v.answer))


def eval_p2(d: "spot.twa_graph") -> Tuple[bool, int, int]:
    """P2 on the form the cascade GROUNDS ON. Returns (holds, n_grounded, n_min).

    The counterexample must be minimal in the acceptance class the pipeline
    actually builds -- i.e. `d = casc.original_aut`, NOT the raw input: decompose_aut
    re-postprocesses (parity-min / complete / sbacc) and can PAD a minimal input
    into a larger form on which a group then appears (the gfa_pad2 phenomenon). So
    P2 holds iff `d` equals its own SAT-min within the class it already carries.
    """
    n = d.num_states()
    m = spot.sat_minimize(d)
    n_min = m.num_states() if m is not None else n
    return (n == n_min, n, n_min)


Reading = Tuple[Tuple[int, ...], Optional[bool], Optional[str]]


def eval_p3(casc: "object") -> Tuple[bool, List[Reading]]:
    """P3: does some config C have Inf(C) genuinely NON-star-free (as a language)?

    Two tiers per config: the cheap aperiodicity SCREEN on the Fin(C) form
    (label_ltl_definable: True aperiodic / False group / None blocked), and -- only
    when the screen flags a group or is blocked -- the language-level oracle verdict
    (decide: LTL / NOT_LTL). A form-level group with an LTL language is a *benign*
    group (set-equal twin), NOT a P3 witness; P3 holds iff some config's language is
    oracle-NOT_LTL. Returns (holds, per-config [(C, screen, oracle-or-None)]).
    """
    readings: List[Reading] = []
    for c in casc.all_configs():
        gt = _gt_fin_automaton(casc, c)
        lang = Language.of(gt)
        screen, _ = label_ltl_definable(lang)
        oracle: Optional[str] = None
        if screen is not True:  # only confirm the suspicious ones
            oracle = str(decide(lang).answer)
        readings.append((c, screen, oracle))
    nonsf = any(o == str(NOT_LTL) for _c, _s, o in readings)
    return (nonsf, readings)


def _assembled_output_verdict(aut: "spot.twa_graph") -> str:
    """Run the ungated cascade and report whether its formula equals L(aut)."""
    cascade = as_translator(make_hierarchy_class())
    res = cascade(Language.of(aut))
    if res.ok and res.formula is not None:
        eq = spot.are_equivalent(res.formula.translate(), aut)
        return f"formula={res.formula}  EQUIVALENT={eq}"
    return "cascade did not produce a formula"


def main(path: str) -> int:
    aut = spot.automaton(path)
    p1, ans = eval_p1(aut)

    if not spot.is_complete(aut):
        aut = spot.complete(aut)
    try:
        casc = build_cascade_unstripped(aut)
    except Exception as e:
        print(f"{path}: ERROR {type(e).__name__}: {e}")
        return 2
    d = casc.original_aut                       # the minimal target we ground on
    n_in = aut.num_states()
    n_d = d.num_states()
    p2, _n_d, n_dmin = eval_p2(d)
    p3, readings = eval_p3(casc)

    nonsf_configs = [c for c, _s, o in readings if o == str(NOT_LTL)]
    benign = [c for c, s, o in readings if s is False and o != str(NOT_LTL)]
    blocked = [c for c, s, _o in readings if s is None]

    reasons: List[str] = []
    if not p1:
        reasons.append(f"P1-fail(oracle={ans})")
    if not p2:
        # decompose_aut expanded a minimal input past its class-minimal -> "pad";
        # otherwise the grounded form is simply not minimal.
        tag = "P2-pad" if n_d > n_in else "P2-fail"
        reasons.append(f"{tag}(in={n_in} grounded={n_d} min={n_dmin})")
    if not p3:
        if benign:
            reasons.append(f"P3-benign(group_configs={len(benign)}_all_star_free)")
        else:
            reasons.append("P3-none")
        if blocked:
            reasons.append(f"P3-blocked({len(blocked)})")

    if p1 and p2 and p3:
        print(f"{path}: HIT  grounded_states={n_d} oracle={ans} "
              f"nonSF_configs={nonsf_configs}")
        print(f"  assembled-output: {_assembled_output_verdict(aut)}")
        return 0

    print(f"{path}: near-miss  {' '.join(reasons)}  "
          f"[in={n_in} grounded={n_d}/{n_dmin} oracle={ans} "
          f"nonSF={len(nonsf_configs)} blocked={len(blocked)}]")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
