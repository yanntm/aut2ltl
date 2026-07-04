"""For one HOA input, test aperiodicity of BOTH deterministic forms:
  - det_generic_minimal()  -- the form the gate screens
  - det_parity_sbacc()     -- the form the cascade actually builds and decomposes

Prints whether each transition monoid is aperiodic (group-free). A form with a
group is one whose Z2 (etc.) survived that particular determinization.

Usage:  python3 tests/probes/form_aperiodic.py <file.hoa>
"""
import sys

import spot

from aut2ltl.language import Language
from aut2ltl.bls.generators import extract_generators
from aut2ltl.bls.gap.aperiodic import is_aperiodic_gens


def _report(tag: str, det: "spot.twa_graph") -> None:
    aut = spot.postprocess(det, "deterministic", "generic", "complete")
    gens, _, _ = extract_generators(aut, max_aps=5)
    ap = is_aperiodic_gens(gens, gap_cmd="gap", timeout=30)
    print(f"{tag:24s} states={aut.num_states()}  aperiodic={ap}  "
          f"({'Z2-free' if ap else 'carries a group'})")


def main(path: str) -> int:
    lang = Language.of(spot.automaton(path))
    _report("det_generic_minimal", lang.det_generic_minimal())
    _report("det_parity_sbacc", lang.det_parity_sbacc())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
