"""Gate: the invariant-typed contract end to end on the named small cases.

    python3 -m tests.sosl.gate_invariant_contract

For each formula: learn under the exact oracle (every hypothesis an
`Invariant`, the align-and-scan decision), and assert the learned invariant is
byte-equal to the reference construction. Prints one OK line per case.
"""
from __future__ import annotations

from sosl.learn.learner import learn
from sosl.sos import dump_invariant
from sosl.sos.build import reference_of_ltl
from sosl.teacher import HoaTeacher

CASES = [
    ("GFa", "GF a"),
    ("GF(aa)", "GF(a & X a)"),
    ("Even", "{ {a[*2]}[*] ; !a }<>-> 1"),
    ("a->Xa", "a -> X a"),
    ("a&XG!a", "a & X G !a"),
]


def main() -> None:
    for name, formula in CASES:
        ref = reference_of_ltl(formula)
        teacher = HoaTeacher.of_ltl(formula, eq_mode="exact")
        stats: dict = {}
        inv = learn(teacher, teacher.alphabet, stats=stats)
        assert dump_invariant(inv) == dump_invariant(ref), \
            f"{name}: learned invariant byte-differs from reference"
        print(f"OK {name}: N={inv.n} member={stats['n_member']} "
              f"equiv={stats['n_equiv']} cex={stats['n_cex']} "
              f"sat={stats['n_saturation']}")


if __name__ == "__main__":
    main()
