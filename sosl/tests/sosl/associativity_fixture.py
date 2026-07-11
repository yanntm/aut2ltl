"""P7/F8 — the associativity probe and the stalled-export display lock.

    python3 -m tests.sosl.associativity_fixture

Spec §8 M4.e item 2, §9 rows P7/F8, adapted to export refusal (§8 item 13b):
the raw read-off of a non-congruent fixpoint only exists as the *unchecked*
diagnostic export, so that is what the F8 half drives.

  - **F8 (MUST be red, with the pinned witness).** The `a_implies_xa` ablation
    fixpoint (4 classes, certified by the exact oracle) is exported unchecked
    and must reproduce the paper's §4.2 display cell-for-cell — keys
    `eps / !a / a / a;!a`; row `a` = `a, a;!a, !a, !a` — and be
    **non-associative** with first witness triple `([a], [a], [a])`. A green
    associativity check here means the export or the check is wrong; a
    different display means the read-off drifted. Never "fix" the red — it
    anchors the paper.
  - **P7 (always green).** Saturated runs of the same specimens export a
    two-sided congruence quotient, whose table is associative by construction
    (and `fixpoint_congruent = true`, recorded from the clean final sweep).

Exits non-zero on the first violated assertion.
"""
from __future__ import annotations

from typing import List

from sosl.experiment.run import Config, run_case
from sosl.learn import learn
from sosl.sos.invariant import Invariant
from sosl.sos.io.serialize import render_word
from sosl.teacher import HoaTeacher

# The paper's §4.2 display of the stalled a_implies_xa read-off: class keys in
# display order, and the full `a` row of M against those columns.
DISPLAY_KEYS = ["eps", "!a", "a", "a;!a"]
ROW_A = ["a", "a;!a", "!a", "!a"]


def _key_index(inv: Invariant, rendered: str) -> int:
    for c in range(inv.n):
        if render_word(inv.alphabet, inv.keys[c]) == rendered:
            return c
    raise AssertionError(f"no class keyed {rendered!r} in the export")


def check_f8_display() -> None:
    t = HoaTeacher.of_hoa("samples/a_implies_xa.hoa", eq_mode="exact")
    inv = learn(t, t.alphabet, saturation=False, unchecked_export=True)
    assert inv.n == 4, f"stall expected 4 classes, got {inv.n}"

    keys = [render_word(inv.alphabet, inv.keys[c]) for c in range(inv.n)]
    assert sorted(keys) == sorted(DISPLAY_KEYS), (keys, DISPLAY_KEYS)
    cols = [_key_index(inv, k) for k in DISPLAY_KEYS]
    ia = _key_index(inv, "a")
    row_a = [render_word(inv.alphabet, inv.keys[inv.mult[ia][d]]) for d in cols]
    assert row_a == ROW_A, f"row a drifted: got {row_a}, display says {ROW_A}"

    witness = inv.associativity_witness()
    assert witness is not None, (
        "F8: the stalled a_implies_xa export came out ASSOCIATIVE — "
        "the export or the check is wrong (spec §9 row F8)")
    assert witness == (ia, ia, ia), (
        f"F8 witness drifted: got {witness}, expected ([a],[a],[a]) = "
        f"({ia},{ia},{ia})")
    print(f"OK F8 a_implies_xa unchecked export: display cell-for-cell "
          f"(keys {'/'.join(DISPLAY_KEYS)}; row a = {', '.join(ROW_A)}); "
          f"non-associative, witness ([a],[a],[a])")


def check_p7_saturated(name: str) -> None:
    res = run_case(name, f"samples/{name}.hoa",
                   Config("default-exact", saturation=True, eq_mode="exact"))
    s = res.stats
    assert s.verdict == "SOUND", (name, s.verdict, s.detail)
    assert s.export_associative == "true", (
        f"P7 violated on {name}: saturated export non-associative "
        f"({s.detail}) — learner bug")
    assert s.fixpoint_congruent == "true", (name, s.fixpoint_congruent)
    print(f"OK P7 {name} saturated: export associative, fixpoint congruent")


def main() -> int:
    check_f8_display()
    for name in ("a_implies_xa", "a_once"):
        check_p7_saturated(name)
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
