"""Unit test of sos_sdd.letters: refinement into letter-behavior classes
on the triptych shapes, a 2-AP overlap case, and the determinism /
completeness rejections."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sos_sdd import Automaton  # noqa: E402
from sos_sdd.letters import letter_classes  # noqa: E402


def gf_aa_parity() -> Automaton:
    return Automaton("gf_aa_parity", ("a",), 2, 0, 1, "Inf(0)", (
        (0, "a", 1, set()), (0, "!a", 0, set()),
        (1, "a", 0, {0}), (1, "!a", 0, set())))


def main() -> None:
    cs = letter_classes(gf_aa_parity())
    assert [c.least for c in cs] == ["!a", "a"], cs
    assert cs[0].dst == (0, 0) and cs[0].marks == (0, 0), cs[0]
    assert cs[1].dst == (1, 0) and cs[1].marks == (0, 1), cs[1]
    assert all(c.count == 1 for c in cs)

    # 2 APs, overlapping cubes: "a" (2 letters) vs "a&b"/"a&!b" must
    # refine; "!a" stays one class of 2 letters.
    two = Automaton("two_ap", ("a", "b"), 2, 0, 1, "Inf(0)", (
        (0, "!a", 0, set()), (0, "a", 1, set()),
        (1, "!a", 0, set()), (1, "a&b", 1, {0}), (1, "a&!b", 0, set())))
    cs = letter_classes(two)
    assert [c.least for c in cs] == ["!a&!b", "a&!b", "a&b"], [c.least for c in cs]
    assert [c.count for c in cs] == [2, 1, 1], cs
    assert cs[0].dst == (0, 0) and cs[1].dst == (1, 0) and cs[2].dst == (1, 1)

    # Nondeterministic and incomplete digests are rejected with the letter.
    for name, trans, word in (
            ("nondet", ((0, "a", 0, set()), (0, "a", 1, set()),
                        (0, "!a", 0, set()), (1, "1", 1, set())), "nondeterministic"),
            ("incomplete", ((0, "a", 1, set()), (1, "1", 1, set())), "incomplete")):
        try:
            letter_classes(Automaton(name, ("a",), 2, 0, 1, "Inf(0)", trans))
            raise AssertionError(f"{name} accepted")
        except ValueError as exc:
            assert word in str(exc), exc

    print("SUCCESS")


if __name__ == "__main__":
    main()
