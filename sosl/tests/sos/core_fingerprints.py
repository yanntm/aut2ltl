"""Class-count fingerprints of the canonical construction (`sosl.sos.core`).

    python3 -m tests.sos.core_fingerprints

Builds the reference invariant of each fingerprint language through the full
pipeline (LTL/PSL -> deterministic form -> sos.build -> sos.core) and asserts
the canonical class count ``|S(L)+1|`` against the recorded value. These are
the regression guards of the fresh-identity convention (see
``sosl/sos/core/algorithm.md``): the counts must not move under any change to
the core, and the triptych rows are the paper's Table 1.
"""
from __future__ import annotations

from typing import List, Tuple

from sosl.sos.build import reference_of_ltl

# (formula, canonical class count, note)
FINGERPRINTS: List[Tuple[str, int, str]] = [
    ("GF a", 3, "the fresh-identity bug case: [eps], [a], [!a]"),
    ("F a", 3, ""),
    ("a U b", 4, ""),
    ("G F(a & Xa)", 6, "triptych"),
    ("{ {a[*2]}[*] ; !a }!", 5, "triptych (Even)"),
    ("GF!a && FG(!a -> X{ {a[*2]}[*] ; !a }!)", 8, "triptych (EvenBlocks)"),
    ("F(a & Xa)", 6, ""),
]


def main() -> None:
    for formula, expected, note in FINGERPRINTS:
        inv = reference_of_ltl(formula)
        tag = f" ({note})" if note else ""
        assert inv.n == expected, (
            f"{formula}: {inv.n} classes, expected {expected}{tag}")
        print(f"OK {formula!r:45} |S(L)+1| = {inv.n}{tag}")
    print("ALL OK")


if __name__ == "__main__":
    main()
