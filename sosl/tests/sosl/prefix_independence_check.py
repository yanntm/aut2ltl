"""Validate `census_e2_exhibits._prefix_independent` against known languages.

    python3 -m tests.sosl.prefix_independence_check

GF(aa) and EvenBlocks are prefix-independent (a finite prefix cannot change
"infinitely many aa" / the eventual-block property); Even, a_once and
a_implies_xa are not (their membership is fixed by the prefix). If the algebraic
predicate disagrees, the census-E2 structural buckets cannot be trusted.
"""
from __future__ import annotations

from sosl.sos.build import reference_of_hoa
from tests.sosl.census_e2_exhibits import _prefix_independent

EXPECT = {
    "gf_aa_parity": True,
    "evenblocks": True,
    "even": False,
    "a_once": False,
    "a_implies_xa": False,
}


def main() -> int:
    bad = []
    for name, want in EXPECT.items():
        got = _prefix_independent(reference_of_hoa(f"samples/{name}.hoa"))
        flag = "ok" if got == want else "MISMATCH"
        print(f"  {name:<14} prefix-independent={got} (expect {want}) {flag}")
        if got != want:
            bad.append(name)
    print("ALL OK" if not bad else f"FAILURES: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
