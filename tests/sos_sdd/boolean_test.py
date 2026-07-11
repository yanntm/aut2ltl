"""§6.2 (C10) gate: the same-table Boolean algebra, checked as language
operations and as the E9 commutation gate (Prop 6.0).

The moves are set operations on the grounded accept-mask table over a
`fork()` of the core sharing Phases 0-2; the derived object's phases
3-5 run lazily on first consumption. Checks per case:

- `masks`: `masks_to_formula` is exact — grounding its output returns
  the input mask set, for every subset at 1..3 marks.
- `complement_*`: `~S` agrees with negated membership on every lasso
  (|u| ≤ 3, |v| ≤ 3); op-then-reduce is byte-identical to the fresh
  build of the complemented digest (the commutation gate — the fresh
  build's own conformance is F14/F17); `~~S` round-trips to `S`'s
  bytes.
- `boolean_evenblocks`: two acceptance conditions over one marked
  semiautomaton — `& | -` against the membership Booleans and the
  fresh combined builds.
- `reference_complement`: the commutation gate closed against the
  explicit reference itself (Spot-backed, bounded) on stem and
  gf_aa_parity.
- `lazy`: a derived object runs no Acc-dependent phase until consumed;
  the core's write-once guard holds; cross-table and non-SoS operands
  are refused loudly.

A single case name as argv runs just that case."""

import dataclasses
import sys
from pathlib import Path
from typing import Callable, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from conformance_test import to_hoa  # noqa: E402
from e0_triptych import TRIPTYCH  # noqa: E402
from member_test import lassos  # noqa: E402
from phase2_test import MOD3  # noqa: E402
from residuals_test import STEM  # noqa: E402

from sos_sdd import Automaton, Engine  # noqa: E402
from sos_sdd.accept import accept_masks, masks_to_formula  # noqa: E402
from sos_sdd.quotient import QuotientSoS  # noqa: E402

LOGS = Path(__file__).resolve().parent / "logs"


def build(aut: Automaton) -> QuotientSoS:
    return Engine(square="off").build(aut, until_phase=6)


def fresh(aut: Automaton, masks: Tuple[int, ...], name: str) -> QuotientSoS:
    """The from-scratch build of (D, masks) — the commutation gate's
    other side (its conformance to the reference is F14/F17)."""
    return build(dataclasses.replace(
        aut, name=name, acceptance=masks_to_formula(masks, aut.marks)))


def case_masks() -> None:
    import itertools
    for k in (1, 2, 3):
        universe = range(1 << k)
        for r in range(len(list(universe)) + 1):
            for ms in itertools.combinations(universe, r):
                got = accept_masks(masks_to_formula(ms, k), k)
                assert got == ms, (k, ms, got)
    print("masks: formula rendering exact on every subset, 1..3 marks")


def check_complement(aut: Automaton) -> None:
    s = build(aut)
    t = ~s
    for u, v in lassos(aut):
        assert t.member(u, v) == (not s.member(u, v)), (aut.name, u, v)
    comp = tuple(m for m in range(1 << aut.marks)
                 if m not in accept_masks(aut.acceptance, aut.marks))
    want = fresh(aut, comp, f"{aut.name}_comp_fresh").to_sos()
    assert t.to_sos() == want, f"{aut.name}: ~S != fresh complement build"
    assert (~t).to_sos() == s.to_sos(), f"{aut.name}: ~~S != S"
    print(f"{aut.name}: ~S == fresh build bytes, membership negated, "
          f"~~S round-trips ({t.n_classes()} classes)")


def case_boolean_evenblocks() -> None:
    eb = next(a for a, _ in TRIPTYCH if a.name == "evenblocks")
    other = dataclasses.replace(eb, name="eb_inf0", acceptance="Inf(0)")
    s1, s2 = build(eb), build(other)
    m1 = set(accept_masks(eb.acceptance, eb.marks))
    m2 = set(accept_masks(other.acceptance, other.marks))
    ops: Tuple[Tuple[str, Callable, Callable], ...] = (
        ("and", lambda a, b: a & b, lambda x, y: x and y),
        ("or", lambda a, b: a | b, lambda x, y: x or y),
        ("minus", lambda a, b: a - b, lambda x, y: x and not y))
    masks = {"and": m1 & m2, "or": m1 | m2, "minus": m1 - m2}
    for tag, op, boolean in ops:
        o = op(s1, s2)
        for u, v in lassos(eb, stem_max=2, loop_max=3):
            want = boolean(s1.member(u, v), s2.member(u, v))
            assert o.member(u, v) == want, (tag, u, v)
        want_sos = fresh(eb, tuple(sorted(masks[tag])),
                         f"eb_{tag}_fresh").to_sos()
        assert o.to_sos() == want_sos, f"{tag}: op != fresh build bytes"
        print(f"evenblocks {tag}: membership Boolean + fresh-build bytes "
              f"({o.n_classes()} classes)")


def case_reference_complement() -> None:
    REPO = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(REPO / "sosl"))
    from sosl.sos.build import reference_of_hoa
    from sosl.sos.io.serialize import dump_invariant
    for aut in (STEM, next(a for a, _ in TRIPTYCH
                           if a.name == "gf_aa_parity")):
        comp = tuple(m for m in range(1 << aut.marks)
                     if m not in accept_masks(aut.acceptance, aut.marks))
        caut = dataclasses.replace(
            aut, name=f"{aut.name}_comp",
            acceptance=masks_to_formula(comp, aut.marks))
        hoa = LOGS / f"boolean_{caut.name}.hoa"
        hoa.write_text(to_hoa(caut))
        want = dump_invariant(reference_of_hoa(str(hoa)))
        got = (~build(aut)).to_sos()
        assert got == want, f"{caut.name}: ~S != reference bytes"
        print(f"{aut.name}: ~S byte-identical to the reference")


def case_lazy() -> None:
    s = build(MOD3)
    t = ~s
    assert t._pending, "derived object ran its phases eagerly"
    assert t.em1_count() == s.em1_count()  # phase-1 reading: still pending
    assert t._pending, "a phase-1 reading consumed the Acc phases"
    t.n_states()
    assert not t._pending, "consumption did not run the pending phases"
    try:  # write-once guard on the core
        t._core.residuate(None, list(t._model.mark_bits),
                          list(t._model.block_base),
                          [list(a) for a in t._model.accept])
        raise AssertionError("second residuate on one core did not raise")
    except RuntimeError:
        pass
    try:  # cross-table operands wait for §6.3
        s & build(STEM)
        raise AssertionError("cross-table op was not refused")
    except NotImplementedError:
        pass
    try:
        s & "not an SoS"
        raise AssertionError("non-SoS operand was not refused")
    except TypeError:
        pass
    print("lazy: pending until consumed; write-once, cross-table and "
          "non-SoS refusals hold")


CASES = {
    "masks": case_masks,
    "complement_gf_aa_parity": lambda: check_complement(
        next(a for a, _ in TRIPTYCH if a.name == "gf_aa_parity")),
    "complement_evenblocks": lambda: check_complement(
        next(a for a, _ in TRIPTYCH if a.name == "evenblocks")),
    "complement_mod3": lambda: check_complement(MOD3),
    "complement_stem": lambda: check_complement(STEM),
    "boolean_evenblocks": case_boolean_evenblocks,
    "reference_complement": case_reference_complement,
    "lazy": case_lazy,
}


def main() -> None:
    LOGS.mkdir(exist_ok=True)
    for name in (sys.argv[1:] or CASES):
        CASES[name]()
    print("SUCCESS")


if __name__ == "__main__":
    main()
