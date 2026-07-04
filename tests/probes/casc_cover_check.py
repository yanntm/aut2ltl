"""Dump a holonomy cascade and check the paper's two premises on it.

Boker-Lehtinen-Sickert's correctness core (Lemma 4/7 + Thm 2) is unconditional
given (a) a genuine RESET cascade and (b) a homomorphism (cover) pi from the
cascade's configuration semiautomaton onto D's semiautomaton:
delta_D(pi(C), sigma) = pi(delta_A(C, sigma)). Counter-freeness of D enters the
paper ONLY as the existence guarantee for such a cascade (Prop. 6). This probe
takes one HOA, runs the decomposition, and reports exactly where (if anywhere)
those two premises break -- so an off-theorem-but-correct translation can be
localized to the premise it violates.

Usage:  python3 tests/probes/casc_cover_check.py <file.hoa>
Exit: 0 both premises hold, 1 a premise fails, 2 decomposition failed.
"""
import sys
from typing import Dict, List, Optional, Tuple

import spot

from aut2ltl.bls.gap import decompose_aut


def fmt_val(val: Dict[str, bool]) -> str:
    return "&".join(("" if v else "!") + k for k, v in sorted(val.items())) or "true"


def main(path: str) -> int:
    aut = spot.automaton(path)
    casc = decompose_aut(aut)
    if casc is None:
        print("decomposition FAILED")
        return 2

    print(f"== input: {path}")
    print(f"D (normalized): {casc.num_states} states, aps={casc.aps}, "
          f"acc={casc.original_aut.get_acceptance() if casc.original_aut else '?'}")
    for li, imgs in enumerate(casc.generator_images):
        print(f"  letter {li} [{fmt_val(casc.letter_valuations[li])}]: "
              f"images {imgs}")

    print(f"== cascade: {casc.num_levels} level(s)")
    for lv in casc.levels:
        print(f"  level {lv.index}: size={lv.size} kind={lv.kind} "
              f"structure={lv.structure}")
    print(f"  state_to_config (section): {casc.state_to_config}")
    print(f"  config_to_state (cover pi): {casc.config_to_state}")

    configs: List[Tuple[int, ...]] = casc.all_configs()
    nlet: int = casc.num_letters()
    print(f"  configs ({len(configs)}): {configs}")
    for c in configs:
        row = " ".join(str(casc.move_config(c, li)) for li in range(nlet))
        print(f"    {c} -> {row}")

    # Premise (a): every level is a reset semiautomaton -- for each level i and
    # each combined letter (letter, lower sub-config), the induced action on
    # that level's coordinates is the identity or a constant. Convention per
    # model.py: coordinate 0 is the TOP level, the tail is the lower sub-config,
    # so level i's action may depend only on the letter and coordinates i+1..n.
    print("== premise (a): reset property per level")
    reset_ok = True
    for lvl in range(casc.num_levels):
        # group observed actions by (letter, sub-config below this level)
        actions: Dict[Tuple[int, Tuple[int, ...]], Dict[int, int]] = {}
        for c in configs:
            for li in range(nlet):
                nc = casc.move_config(c, li)
                key = (li, c[lvl + 1:])
                actions.setdefault(key, {})[c[lvl]] = nc[lvl]
        for (li, prefix), act in sorted(actions.items()):
            vals = set(act.values())
            is_id = all(k == v for k, v in act.items())
            is_const = len(vals) == 1
            tag = "identity" if is_id else ("reset->" + str(vals.pop()) if is_const else "NON-RESET")
            if not (is_id or is_const):
                reset_ok = False
            print(f"  level {lvl} letter {li} below={prefix}: {act}  [{tag}]")
    print(f"  reset premise: {'HOLDS' if reset_ok else 'VIOLATED'}")

    # Premise (b): pi is a homomorphism onto D.
    print("== premise (b): cover pi commutes with the dynamics")
    homo_ok = True
    onto = set(casc.config_to_state.values())
    if onto != set(range(casc.num_states)):
        homo_ok = False
        print(f"  pi not surjective: image {sorted(onto)} vs D states 0..{casc.num_states - 1}")
    for c in configs:
        q: Optional[int] = casc.state_of(c)
        if q is None:
            print(f"  pi undefined on reachable config {c}")
            continue
        for li in range(nlet):
            nc = casc.move_config(c, li)
            q_direct = casc.generator_images[li][q]
            q_via = casc.state_of(nc)
            if q_via != q_direct:
                homo_ok = False
                print(f"  BREAK at pi({c})={q}, letter {li} "
                      f"[{fmt_val(casc.letter_valuations[li])}]: "
                      f"delta_D -> {q_direct}, but pi(delta_A({c})) = pi({nc}) = {q_via}")
    print(f"  homomorphism premise: {'HOLDS' if homo_ok else 'VIOLATED'}")
    return 0 if (reset_ok and homo_ok) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
