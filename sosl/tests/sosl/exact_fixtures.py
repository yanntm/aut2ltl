"""Exact-mode equivalence: sanity + the proven-permanent stall fixtures (spec P4).

    python3 -m tests.sosl.exact_fixtures

Checks, all self-contained (white-box teacher in ``eq_mode="exact"``):

  - GF a: exact certifies the canonical invariant (byte-equal to the reference);
  - `a_implies_xa` and `a_once` under **no saturation** (the current M2 learner):
    exact CERTIFIES their non-canonical stall (4 and 3 classes) — Proposition 4.4
    proves no counterexample exists, so a counterexample here would be an
    exact-mode bug (spec §9 row P4). The exported `.sos` is a class short of the
    reference (F5: byte-inequality is the theorem).

Saturation is not yet in the loop; the saturated+exact half of P4 (both reach
canonical) is exercised once saturation lands.
"""
from __future__ import annotations

from sosl.learn import learn
from sosl.sos import dump_invariant
from sosl.sos.build import reference_of_hoa
from sosl.teacher import HoaTeacher

SOURCES = "samples"


def check_gfa_exact() -> None:
    t = HoaTeacher.of_ltl("GF a", eq_mode="exact")
    learned = learn(t, t.alphabet)
    assert learned.n == 3, learned.n  # [eps] [!a] [a] under the fresh-identity convention
    print(f"OK GF a exact: {learned.n} classes (canonical)")


def check_canonical_exact(name: str, ref_n: int) -> None:
    """A transient-stall language: exact must FIND the counterexamples (its
    closure-driven cex path, not just certification) and reach the reference."""
    path = f"{SOURCES}/{name}.hoa"
    ref = reference_of_hoa(path)
    assert ref.n == ref_n, (name, ref.n, ref_n)
    t = HoaTeacher.of_hoa(path, eq_mode="exact")
    learned = learn(t, t.alphabet, saturation=False)
    assert dump_invariant(learned) == dump_invariant(ref), (
        f"{name}: exact did not reach the canonical reference\n"
        + dump_invariant(learned)
    )
    print(f"OK {name} exact/no-sat: reached canonical {ref_n} classes (byte-equal)")


def check_stall_certified(name: str, ref_n: int, stall_n: int) -> None:
    path = f"{SOURCES}/{name}.hoa"
    ref = reference_of_hoa(path)
    assert ref.n == ref_n, (name, ref.n, ref_n)
    t = HoaTeacher.of_hoa(path, eq_mode="exact")
    learned = learn(t, t.alphabet, saturation=False)
    assert learned.n == stall_n, (
        f"{name}: exact returned a counterexample and drove past the stall "
        f"(got {learned.n} classes, expected the {stall_n}-class stall) — "
        "exact-mode bug (spec P4: Prop 4.4 proves none exists)"
    )
    assert dump_invariant(learned) != dump_invariant(ref), (
        f"{name}: exported stall is byte-equal to the reference (F5 says it must "
        "not be)"
    )
    print(f"OK {name} exact/no-sat: certified {stall_n}-class stall "
          f"(reference {ref_n}), byte-different")

    # with saturation AND exact, the same specimen reaches canonical byte-equal.
    ts = HoaTeacher.of_hoa(path, eq_mode="exact")
    sat = learn(ts, ts.alphabet, saturation=True)
    assert dump_invariant(sat) == dump_invariant(ref), (
        f"{name}: saturation+exact did not reach the canonical reference\n"
        + dump_invariant(sat)
    )
    print(f"OK {name} exact+sat: reached canonical {ref_n} classes (byte-equal)")


def main() -> int:
    check_gfa_exact()
    check_canonical_exact("gf_aa_parity", ref_n=6)
    check_canonical_exact("even", ref_n=5)
    check_stall_certified("a_implies_xa", ref_n=5, stall_n=4)
    check_stall_certified("a_once", ref_n=4, stall_n=3)
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
