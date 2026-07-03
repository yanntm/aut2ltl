"""Run the language-adapter Translator on ONE HOA file and check its answer.

Usage: python3 tests/probes/kanchor_adapter_probe.py <file.hoa>

Same protocol as kanchor_probe.py but through `AdaptedKAnchor` (the
presentation exploration): prints the result and, on OK, checks language
equivalence against the input with spot. Exit code: 0 = OK and equivalent,
1 = OK but NOT equivalent (a real bug), 2 = declined / NOT_LTL.
"""

import sys

import spot

from aut2ltl.language import Language
from aut2ltl.kanchor.language_adapter import AdaptedKAnchor


def main(path: str) -> int:
    aut = spot.automaton(path)
    rec = AdaptedKAnchor(lambda sub: rec(sub))
    res = rec(Language.of(aut))
    print(f"status={res.status.value} technique={res.technique_str()} "
          f"diagnosis={res.diagnosis}")
    if res.nok:
        return 2
    print(f"LTL: {res.formula}")
    cand = res.formula.translate("GeneralizedBuchi", "Small", "High")
    if spot.are_equivalent(aut, cand):
        print("VERIFY: ok (language-equivalent)")
        return 0
    print("VERIFY: FAIL -- formula is NOT language-equivalent to the input")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
