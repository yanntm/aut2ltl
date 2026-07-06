"""Round-trip and byte-stability checks for sosl.sos.io.serialize.

Self-contained. Run from the repo root:

    python3 -m tests.sosl.serialize_roundtrip

Dumps the GF(a) invariant and hypothesis to text and parses them back, checks
structural equality, byte-idempotence of a second dump, and that the parsed
invariant still decides membership the same way. Prints OK lines / the dumped
`.sos` for eyeballing, or raises on the first failure.
"""
from __future__ import annotations

from sosl.sos import (
    EMPTY,
    Alphabet,
    Hypothesis,
    Invariant,
    Lasso,
    dump_hypothesis,
    dump_invariant,
    load_hypothesis,
    load_invariant,
)


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


def gfa_hypothesis() -> Hypothesis:
    ab = Alphabet.of(["a"])
    return Hypothesis(
        alphabet=ab,
        keys=(EMPTY, (0,), (1,)),
        step=((1, 2), (1, 2), (2, 2)),
        accept={(2, 2): True, (1, 1): False, (2, 1): False},
        start=0,
    )


def check_invariant_roundtrip() -> None:
    inv = gfa_invariant()
    text = dump_invariant(inv)
    back = load_invariant(text)
    assert back == inv, "invariant did not round-trip"
    assert dump_invariant(back) == text, "second dump is not byte-identical"
    # membership survives the round trip
    assert back.member(Lasso(EMPTY, (1,))) is True
    assert back.member(Lasso(EMPTY, (0,))) is False
    print("--- .sos dump ---")
    print(text, end="")
    print("OK invariant round-trip + byte-stability")


def check_multi_ap_letters() -> None:
    # Two APs: exercise the {a,b} / {} letter rendering and parsing.
    ab = Alphabet.of(["a", "b"])
    inv = Invariant(
        alphabet=ab,
        keys=(EMPTY, (0b11,)),           # key of class 1 is the letter {a,b}
        letter_class=(1, 1, 1, 1),       # every letter -> class 1 (toy)
        mult=((0, 1), (1, 1)),
        accept=frozenset({(1, 1)}),
        identity=0,
    )
    back = load_invariant(dump_invariant(inv))
    assert back == inv, "multi-AP invariant did not round-trip"
    print("OK multi-AP letter rendering round-trip")


def check_hypothesis_roundtrip() -> None:
    h = gfa_hypothesis()
    text = dump_hypothesis(h)
    back = load_hypothesis(text)
    assert back == h, "hypothesis did not round-trip"
    assert dump_hypothesis(back) == text, "second dump is not byte-identical"
    print("OK hypothesis round-trip + byte-stability")


def main() -> int:
    check_invariant_roundtrip()
    check_multi_ap_letters()
    check_hypothesis_roundtrip()
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
