"""Smoke check that the Teacher contract is usable (sosl.contract).

Self-contained. Run from the `sosl/` subtree root:

    python3 -m tests.sosl.contract_smoke

Defines a tiny in-memory teacher backed by an Invariant read-off, drives it
through the `Teacher` interface, and constructs both equivalence results. Prints
OK lines, or raises on the first failure. Doubles as the reference usage of the
contract.
"""
from __future__ import annotations

from sosl.contract import Counterexample, Equivalent, EquivResult, Teacher
from sosl.sos import EMPTY, Alphabet, Hypothesis, Invariant, Lasso


class InvariantTeacher:
    """A `Teacher` whose language is given by an `Invariant` (member by
    read-off; equiv always agrees — a stand-in, real teachers search)."""

    def __init__(self, inv: Invariant) -> None:
        self.inv = inv

    def member(self, lasso: Lasso) -> bool:
        return self.inv.member(lasso)

    def equiv(self, hypothesis: Hypothesis) -> EquivResult:
        return Equivalent(strategy="stub")


def gfa_invariant() -> Invariant:
    ab = Alphabet.of(["a"])
    return Invariant(
        alphabet=ab,
        keys=(EMPTY, (0,), (1,)),
        letter_class=(1, 2),
        mult=((0, 1, 2), (1, 1, 2), (2, 2, 2)),
        accept=frozenset({(2, 2)}),
        identity=0,
    )


def check_used_through_interface() -> None:
    teacher: Teacher = InvariantTeacher(gfa_invariant())
    assert teacher.member(Lasso(EMPTY, (1,))) is True
    assert teacher.member(Lasso(EMPTY, (0,))) is False
    print("OK member through the Teacher interface")


def check_results_construct() -> None:
    eq = Equivalent(strategy="bounded:8")
    cx = Counterexample(lasso=Lasso(EMPTY, (0,)))
    assert eq.strategy == "bounded:8"
    assert cx.lasso.loop == (0,)
    print("OK Equivalent / Counterexample construct")


def main() -> int:
    check_used_through_interface()
    check_results_construct()
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
