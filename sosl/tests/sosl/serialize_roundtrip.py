"""Round-trip and byte-stability checks for sosl.sos.io.serialize.

Self-contained. Run from the `sosl/` subtree root:

    python3 -m tests.sosl.serialize_roundtrip

Dumps the GF(a) invariant to text and parses it back, checks
structural equality, byte-idempotence of a second dump, and that the parsed
invariant still decides membership the same way. Prints OK lines / the dumped
`.sos` for eyeballing, or raises on the first failure.
"""
from __future__ import annotations

from sosl.sos import (
    EMPTY,
    Alphabet,
    Invariant,
    Lasso,
    dump_invariant,
    load_invariant,
)
from sosl.sos.residuals import Residuals


TARGET = """SOS v1
ap: a
classes: 4
1 !a
2 a
3 !a;a
4 a;!a
letters: !a->1 a->2
mult:
1: 1 3 3 3
2: 4 2 3 4
3: 3 3 3 3
4: 4 3 3 3
accept:
1 1
4 1
"""


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


def check_target() -> None:
    inv = load_invariant(TARGET)
    inv.validate()
    assert inv.n == 5 and inv.identity == 0 and inv.keys[0] == EMPTY
    assert inv.class_count == 4
    assert inv.letter_class == (1, 2)
    assert dump_invariant(inv) == TARGET
    assert inv.member(Lasso(EMPTY, (0,))) is True
    assert inv.member(Lasso(EMPTY, (1,))) is False
    assert inv.member(Lasso((1,), (0,))) is True
    assert inv.member(Lasso((0,), (1,))) is False
    assert inv.complement().complement() == inv
    print("OK four-class target + membership + complement")


def check_zero_ap() -> None:
    inv = Invariant(
        alphabet=Alphabet.of([]),
        keys=(EMPTY, (0,)),
        letter_class=(1,),
        mult=((0, 1), (1, 1)),
        accept=frozenset({(1, 1)}),
        identity=0,
    )
    text = dump_invariant(inv)
    assert "classes: 1\n1 t\n" in text
    assert inv.class_count == 1
    assert load_invariant(text) == inv
    assert inv.member(Lasso(EMPTY, (0,))) is True
    print("OK zero-AP round-trip")


def check_residuals() -> None:
    inv = gfa_invariant()
    res = Residuals(keys=(EMPTY,), delta=((0, 0),))
    trailer = "residuals: 1\n0 eps\nres-step:\n0: 0 0\n"
    assert dump_invariant(inv, residuals=res) == dump_invariant(inv) + trailer
    assert load_invariant(dump_invariant(inv, residuals=res)) == inv
    print("OK residual trailer unchanged")


def main() -> int:
    check_invariant_roundtrip()
    check_multi_ap_letters()
    check_target()
    check_zero_ap()
    check_residuals()
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
