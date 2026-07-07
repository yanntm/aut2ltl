"""The canonicity diff: two presentations of one language, one output.

    python3 -m tests.sos2ltl.e0_canon <a.hoa> <b.hoa>

Bridges both automata to their invariants (must be byte-identical after
serialization — the language identity), synthesizes both, and asserts the
rendered formulas are string-identical: same language ⟹ same formula,
hash-consed identity, not mere equivalence (dg `algorithm.md` layer 8).
"""
from __future__ import annotations

import sys
from typing import List

import spot

from aut2ltl.sos2ltl.bridge import invariant_of_language
from aut2ltl.sos2ltl.dg import synthesize
from aut2ltl.language import Language
from sosl.sos import dump_invariant


def main(argv: List[str]) -> int:
    path_a, path_b = argv[0], argv[1]
    outs: List[str] = []
    dumps: List[str] = []
    for path in (path_a, path_b):
        inv = invariant_of_language(Language.of(spot.automaton(path)))
        dumps.append(dump_invariant(inv))
        ast, phi, n = synthesize(inv)
        cubes = ["&".join(p if p in inv.alphabet.true_aps(a) else "!" + p
                          for p in inv.alphabet.aps)
                 for a in inv.alphabet.letters()]
        outs.append(ast.to_spot(phi, cubes))
        print(f"{path}: {inv.n} classes, {n} nodes, formula {len(outs[-1])} chars")

    assert dumps[0] == dumps[1], "invariants differ: not one language"
    assert outs[0] == outs[1], "same invariant, different formulas: canonicity broken"
    print("CANONICAL: identical .sos, identical formula")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
