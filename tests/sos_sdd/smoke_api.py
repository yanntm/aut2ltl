"""Smoke test of the sos_sdd pure-Python layer: digest construction and
validation, product namespace checks, and the façade's clear failure when
the C++ extension is absent. No extension required."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sos_sdd import Automaton, Engine, Product, Transition  # noqa: E402


def main() -> None:
    aut = Automaton(
        name="toy",
        ap=("a",),
        states=2,
        init=0,
        marks=2,
        acceptance="Inf(0)&Inf(1)",
        trans=(
            (0, "a", 1, {0}),  # tuple form coerces to Transition
            Transition(1, "!a", 0, frozenset({1})),
            Transition(1, "1", 1),
        ),
    )
    aut.validate()
    assert all(isinstance(t, Transition) for t in aut.trans)

    bad = Automaton("bad", ("a",), 2, 0, 1, "Inf(0)", ((0, "b", 1, set()),))
    try:
        bad.validate()
        raise AssertionError("unknown AP accepted")
    except ValueError:
        pass

    other = Automaton("toy2", ("a",), 1, 0, 1, "Inf(0)", ((0, "a", 0, {0}),))
    try:
        Product("p", (aut, other), "async").validate()
        raise AssertionError("async product with shared APs accepted")
    except ValueError:
        pass

    try:
        Engine().build(aut, until_phase=1)
        raise AssertionError("build succeeded before the pipeline exists")
    except (RuntimeError, NotImplementedError) as exc:
        assert "_core" in str(exc)

    print("SUCCESS")


if __name__ == "__main__":
    main()
