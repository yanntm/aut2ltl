"""§6.1 (C10) gate: closure-free lasso membership checked three ways.

1. `sweep` cases: every lasso u·v^ω with |u| ≤ 3, 1 ≤ |v| ≤ 3 over the
   concrete letters, `calculus.member` against an independent explicit
   simulation of the digest (run the stem, iterate the loop to the
   state repeat, union the repeating iterations' marks, evaluate the
   acceptance formula).
2. `closure_free`: the structural §6.1 assertion — a membership query
   never loads the C++ core (`sos_sdd._core` absent from sys.modules).
   Run it before any engine-touching case (it is first in CASES).
3. `crosscheck`: member's verdict equals the engine's Phase 3 read,
   `A(st_⟦u⟧(ι), ⟦v⟧^π)` off the built object's profile rows — ties the
   concrete arithmetic to the symbolic Val semantics.

`refuse` probes the loud failures: empty loop, ambiguous partial cube,
non-Automaton input; plus the legal partial cube ("1" on a one-class
alphabet). A single case name as argv runs just that case."""

import dataclasses
import itertools
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from e0_triptych import TRIPTYCH  # noqa: E402
from phase2_test import MOD3  # noqa: E402
from residuals_test import DUPE, STEM  # noqa: E402

from sos_sdd.accept import eval_acceptance  # noqa: E402
from sos_sdd.calculus import fold, idempotent_power, member  # noqa: E402
from sos_sdd.letters import letter_classes, parse_cube  # noqa: E402
from sos_sdd.model import Automaton  # noqa: E402
from sos_sdd.slotmodel import from_automaton  # noqa: E402

Word = Tuple[str, ...]

# One class covering the whole alphabet: the partial cube "1" is legal.
UNIV = Automaton("univ", ("a",), 1, 0, 1, "Inf(0)", ((0, "1", 0, {0}),))


def letters_of(aut: Automaton) -> List[str]:
    """Every concrete letter as a full-valuation cube string, in the
    canonical order (absent 0 < present 1 per AP)."""
    return ["&".join(a if b else f"!{a}" for a, b in zip(aut.ap, bits))
            for bits in itertools.product((0, 1), repeat=len(aut.ap))]


def gt_member(aut: Automaton, u: Word, v: Word) -> bool:
    """Explicit lasso simulation on the digest, letter by letter — no
    monoid, no letter classes: deterministic transition lookup per
    concrete valuation, loop iterated to the entry-state repeat, the
    repeating segment's mark union fed to the acceptance formula."""
    cubes = [(t.src, parse_cube(t.cube, aut.ap), t.dst, t.marks)
             for t in aut.trans]

    def step(q: int, letter: str) -> Tuple[int, int]:
        bits = parse_cube(letter, aut.ap)
        rows = [(dst, mk) for src, cube, dst, mk in cubes
                if src == q and all(bits.get(k) == val
                                    for k, val in cube.items())]
        assert len(rows) == 1, (aut.name, q, letter, rows)
        dst, mk = rows[0]
        return dst, sum(1 << m for m in mk)

    q = aut.init
    for letter in u:
        q, _ = step(q, letter)
    entries: List[int] = []
    marks: List[int] = []
    while q not in entries:
        entries.append(q)
        acc = 0
        for letter in v:
            q, mk = step(q, letter)
            acc |= mk
        marks.append(acc)
    i = entries.index(q)
    inf = 0
    for m in marks[i:]:
        inf |= m
    return eval_acceptance(aut.acceptance, inf)


def lassos(aut: Automaton, stem_max: int = 3,
           loop_max: int = 3) -> List[Tuple[Word, Word]]:
    ls = letters_of(aut)
    stems = [w for k in range(stem_max + 1)
             for w in itertools.product(ls, repeat=k)]
    loops = [w for k in range(1, loop_max + 1)
             for w in itertools.product(ls, repeat=k)]
    return [(u, v) for u in stems for v in loops]


def sweep(aut: Automaton) -> None:
    pairs = lassos(aut)
    n_in = 0
    for u, v in pairs:
        got = member(aut, u, v)
        want = gt_member(aut, u, v)
        assert got == want, (aut.name, u, v, got, want)
        n_in += got
    print(f"{aut.name}: {len(pairs)} lassos, {n_in} in L — member == GT")


def case_closure_free() -> None:
    assert member(UNIV, (), ("a",)) is True
    assert member(STEM, ("a",), ("!a",)) is True
    assert "sos_sdd._core" not in sys.modules, (
        "a membership query loaded the C++ core — §6.1 violated")
    print("closure_free: member ran with sos_sdd._core unloaded")


def case_crosscheck() -> None:
    from sos_sdd import Engine
    for aut in (next(a for a, _ in TRIPTYCH if a.name == "evenblocks"),
                MOD3, STEM):
        classes = letter_classes(aut)
        model = from_automaton(aut)
        s = Engine(square="off").build(aut, until_phase=4)
        rows: Dict[Tuple[int, ...], Sequence[int]] = {
            tuple(x): bits for x, bits in s.profile_rows()}
        bits = model.mark_bits[aut.init]
        for u, v in lassos(aut, stem_max=2, loop_max=3):
            c = fold(u, aut, classes, model)
            e = idempotent_power(fold(v, aut, classes, model), model)
            want = bool(rows[e][c[aut.init] >> bits])
            assert member(aut, u, v) == want, (aut.name, u, v)
        print(f"{aut.name}: member == engine profile read")


def case_refuse() -> None:
    for bad_call, exc in (
            (lambda: member(MOD3, ("a",), ()), ValueError),      # empty loop
            (lambda: member(MOD3, (), ("1",)), ValueError),      # ambiguous cube
            (lambda: member(("not", "an", "aut"), (), ("a",)),   # not a digest
             NotImplementedError)):
        try:
            bad_call()
            raise AssertionError("refusal probe did not raise")
        except exc:
            pass
    # The legal partial cube: "1" where the alphabet is one class.
    assert member(UNIV, (), ("1",)) is True
    print("refuse: empty loop / ambiguous cube / non-digest all raise")


CASES = {
    "closure_free": case_closure_free,
    "gf_aa_parity": lambda: sweep(next(a for a, _ in TRIPTYCH
                                       if a.name == "gf_aa_parity")),
    "even": lambda: sweep(next(a for a, _ in TRIPTYCH if a.name == "even")),
    "evenblocks": lambda: sweep(next(a for a, _ in TRIPTYCH
                                     if a.name == "evenblocks")),
    "mod3": lambda: sweep(MOD3),
    "dupe": lambda: sweep(DUPE),
    # DUPE rebased at state 1: init 0 is a rejecting sink, so the plain
    # sweep is all-rejecting; the rebase exercises accepting verdicts
    # (and previews §6.5's rooting = moving ι).
    "dupe1": lambda: sweep(dataclasses.replace(DUPE, name="dupe1", init=1)),
    "stem": lambda: sweep(STEM),
    "refuse": case_refuse,
    "crosscheck": case_crosscheck,
}


def main() -> None:
    for name in (sys.argv[1:] or CASES):
        CASES[name]()
    print("SUCCESS")


if __name__ == "__main__":
    main()
