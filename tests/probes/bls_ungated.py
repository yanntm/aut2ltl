"""Run the UNGATED bls cascade on one HOA form and check equivalence.

Bypasses cascade_gate to see whether the cascade ITSELF handles a form the gate
declines (e.g. gf_aa_parity: an LTL language whose det form carries a Z2). If the
formula comes back equivalent, the gate (screening det_generic_minimal) is
stricter than the cascade (building det_parity_sbacc) actually requires.

Usage:  python3 tests/probes/bls_ungated.py <file.hoa>
"""
import sys

import spot

from aut2ltl.language import Language
from aut2ltl.bls.aut2cas import as_translator
from aut2ltl.bls.hierarchy_class import make_hierarchy_class


def main(path: str) -> int:
    aut = spot.automaton(path)
    lang = Language.of(aut)
    cascade = as_translator(make_hierarchy_class())   # NO gate
    res = cascade(lang)
    print("ok       :", res.ok)
    print("technique:", res.technique_str())
    if res.ok and res.formula is not None:
        f = res.formula
        print("formula  :", f)
        eq = spot.are_equivalent(f.translate(), aut)
        print("EQUIVALENT to input:", eq)
        return 0 if eq else 1
    print("diagnosis:", res.diagnosis_str() if hasattr(res, "diagnosis_str") else res)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
