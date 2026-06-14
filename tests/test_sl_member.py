#!/usr/bin/env python3
"""
tests/test_sl_member.py

Cross-check the new `Sl` Translator against the old `try_heuristic_gate`: on the
same automaton they must agree on decline/produce, and produce language-equivalent
formulas. Flags (does not fail) any equivalent-but-not-identical case — the signal
that `Language.tgba()`'s postprocess differs from the old gate's.

Spot only (no GAP), small inputs. Run from project root:
    python3 tests/test_sl_member.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import spot
from aut2ltl.language import Language
from aut2ltl.portfolio.sl import sl as sl_member
from aut2ltl.portfolio.heuristic_gate import try_heuristic_gate

CASES = ["Ga", "Fa", "a U b", "GFa", "FGa", "Fa | Gb",
         "G(a -> X b)", "GFa & FGb", "X(a & Xa)", "G(p | F q)"]


def test_sl_matches_old_gate() -> None:
    non_identical = []
    for s in CASES:
        aut = spot.formula(s).translate()
        old = try_heuristic_gate(aut)              # Optional[formula]
        new = sl_member(Language.of(aut))          # LTLFormulaResult
        if old is None:
            assert new.declined, f"{s}: old declined, new produced {new.formula}"
            continue
        assert new.ok, f"{s}: old produced {old}, new declined"
        assert spot.are_equivalent(old.translate(), new.formula.translate()), \
            f"{s}: not language-equivalent (old={old}, new={new.formula})"
        if old != new.formula:
            non_identical.append((s, str(old), str(new.formula)))
    for s, o, n in non_identical:
        print(f"  NOTE non-identical (still equivalent): {s}: old={o} | new={n}")
    print(f"  {len(non_identical)}/{len(CASES)} equivalent-but-not-identical")


def main() -> int:
    failed = 0
    for t in [test_sl_matches_old_gate]:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
    print(f"\n{'ALL PASS' if not failed else f'{failed} FAILED'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
