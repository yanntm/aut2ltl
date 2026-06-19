"""
genaut/probe_post.py — does a stronger spot postprocess collapse a non-canonical
"true" automaton to the 1-state canonical form?

Background: enumerate.py runs ONE postprocess(Generic, Small, High) pass, and 651
of the 654 universal-language cases survived as 2-state automata (spot's Small is
a structural reducer, not a universality decider). This probe takes ONE generator
id, rebuilds the RAW automaton from that index (the filename aut_NNNNN.hoa encodes
the combo number), and runs a matrix of spot.postprocess (type x pref x level)
settings on it — the same string-API convenience the tool uses for input cleanup
(aut2ltl/language.py::_clean) — reporting #states + acceptance for each, to see
whether any setting reaches the canonical 1-state `true`.

Usage:  python3 genaut/probe_post.py [INDEX]      # default 51142 (a 2-state true)
"""
from __future__ import annotations

import sys

import spot

# probe lives in genaut/, so its own dir is sys.path[0] -> plain import works.
from enumerate import aut_at, combo_at  # noqa: E402

# spot.postprocess(aut, *opts) option strings — the dimensions we sweep.
TYPES = ("generic", "ba", "tgba")
PREFS = ("small", "deterministic")
LEVELS = ("low", "medium", "high")


def describe(aut: "spot.twa_graph") -> str:
    return (f"states={aut.num_states()} "
            f"acc=[{aut.get_acceptance()}] "
            f"det={'Y' if spot.is_deterministic(aut) else 'n'}")


def main(index: int) -> None:
    bdict = spot.make_bdd_dict()
    raw = aut_at(index, bdict)

    print(f"=== index {index}  combo={combo_at(index)} ===")
    print(f"RAW             : {describe(raw)}")
    print("RAW HOA:")
    print(raw.to_str("hoa"))

    print("--- spot.postprocess matrix on the RAW automaton ---")
    print(f"{'type':10s} {'pref':14s} {'level':7s}  result")
    for t in TYPES:
        for pref in PREFS:
            for level in LEVELS:
                try:
                    r = spot.postprocess(aut_at(index, bdict), t, pref, level)
                    mark = "  <-- CANONICAL 1-state" if r.num_states() == 1 else ""
                    print(f"{t:10s} {pref:14s} {level:7s}  {describe(r)}{mark}")
                except Exception as e:  # spot raises on its own limits
                    print(f"{t:10s} {pref:14s} {level:7s}  ERROR: {str(e)[:60]}")

    # spot.is_universal is the STRUCTURAL HOA property (about branching), NOT
    # "accepts every word". Test language-universality the honest way: the
    # complement accepts nothing.
    print(f"--- sanity: language == true (complement empty)? "
          f"{spot.complement(raw).is_empty()} ---")


if __name__ == "__main__":
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 51142
    main(idx)
