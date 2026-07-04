"""Certify a Π₂-hunt hit: dump the cascade's normalized D and the non-star-free
Inf(C) counting witnesses for one automaton.

For a HIT reported by predicate.py this records the evidence the protocol asks
for: the size of the form the cascade actually grounds configs on (to rule out
that a group only appears on an internally PADDED, non-minimal form), the config
count, and -- for every config C whose Inf(C) language the oracle rules NOT_LTL
-- the serialized counting family (period p, u vⁿ x) that proves non-star-freeness.

Usage:  python3 tests/pi2_hunt/witness_config.py <file.hoa>
Exit 0 if at least one non-star-free config witness was found, 1 otherwise.
"""
from __future__ import annotations

import sys
from typing import List

import spot

from aut2ltl.language import Language
from aut2ltl.bls.definability.oracle import decide, NOT_LTL
from predicate import _gt_fin_automaton, build_cascade_unstripped  # same-dir reuse


def main(path: str) -> int:
    aut = spot.automaton(path)
    if not spot.is_complete(aut):
        aut = spot.complete(aut)
    dmin = Language.of(aut).det_generic_minimal()
    casc = build_cascade_unstripped(aut)
    d = casc.original_aut
    configs = casc.all_configs()
    print(f"input states         : {aut.num_states()}")
    print(f"SAT-min states       : {dmin.num_states()}  "
          f"(input minimal: {aut.num_states() == dmin.num_states()})")
    print(f"cascade normalized D : {d.num_states()} states  "
          f"(padding beyond minimal: {d.num_states() > dmin.num_states()})")
    print(f"cascade configs      : {len(configs)}")

    found: List[str] = []
    for c in configs:
        gt = _gt_fin_automaton(casc, c)
        v = decide(Language.of(gt))
        if str(v.answer) == str(NOT_LTL):
            wit = v.witness.serialize() if v.witness is not None else "(no witness)"
            print(f"  Inf({c}): NON-star-free  {wit}")
            found.append(str(c))
    if not found:
        print("no non-star-free config -- not a P3 witness")
        return 1
    print(f"non-star-free configs: {found}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
