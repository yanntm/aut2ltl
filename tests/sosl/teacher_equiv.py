"""Checks for the white-box teacher equivalence query (bounded strategy).

Self-contained (uses spot for the target). Run from the repo root:

    python3 -m tests.sosl.teacher_equiv

Against the GF a teacher: a correct hypothesis is certified Equivalent (both
with a full accept cache and an empty one, exercising cache-miss resolution via
member); a hypothesis with a flipped verdict yields a minimal Counterexample
that genuinely distinguishes hypothesis from language. Prints OK lines, or
raises on the first failure.
"""
from __future__ import annotations

from sosl.contract import Counterexample, Equivalent
from sosl.objects import EMPTY, Alphabet, Hypothesis
from sosl.teacher import HoaTeacher
from sosl.objects.cayley import loop_reps
from sosl.teacher.equiv import resolve_prediction


def gfa_hypothesis(accept) -> Hypothesis:
    ab = Alphabet.of(["a"])
    return Hypothesis(
        alphabet=ab,
        keys=(EMPTY, (0,), (1,)),
        step=((1, 2), (1, 2), (2, 2)),
        accept=accept,
        start=0,
    )


def check_correct_full_cache() -> None:
    t = HoaTeacher.of_ltl("GF a")
    h = gfa_hypothesis({(2, 2): True, (1, 1): False, (2, 1): False})
    res = t.equiv(h, bound=4)
    assert isinstance(res, Equivalent), res
    assert res.strategy == "bounded:4"
    print("OK correct hypothesis (full cache) -> Equivalent")


def check_correct_empty_cache() -> None:
    # Empty cache: every prediction is a miss, resolved via member(key_s, key_e).
    t = HoaTeacher.of_ltl("GF a")
    h = gfa_hypothesis({})
    res = t.equiv(h, bound=4)
    assert isinstance(res, Equivalent), res
    print("OK correct hypothesis (empty cache, misses resolved) -> Equivalent")


def check_broken_hypothesis() -> None:
    t = HoaTeacher.of_ltl("GF a")
    # Flip the accepting pair: claim a loop with an a is NOT accepted.
    h = gfa_hypothesis({(2, 2): False, (1, 1): False, (2, 1): False})
    res = t.equiv(h, bound=4)
    assert isinstance(res, Counterexample), res
    cx = res.lasso
    # It genuinely distinguishes: hypothesis prediction != teacher membership.
    assert resolve_prediction(t.member, h, cx, loop_reps(h)) != t.member(cx)
    # Minimal: empty stem, single-letter loop a.
    assert cx.stem == EMPTY and cx.loop == (1,), (cx.stem, cx.loop)
    print(f"OK broken hypothesis -> minimal Counterexample stem={cx.stem} loop={cx.loop}")


def main() -> int:
    check_correct_full_cache()
    check_correct_empty_cache()
    check_broken_hypothesis()
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
