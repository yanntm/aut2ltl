"""Phases 3-4 (C5) gate: profiles and residual classes checked against an
explicit ground truth built by a deliberately different algorithm — the
loop verdict A(q, x) by walking the cycle of x's state map (orbit walks
are the engine's forbidden move, so the GT doing exactly that is the
point), then the residual partition as an explicit lockstep refinement
over the global states seeded by those verdicts (the Prop 3.4 gfp,
unwound by hand).

Cases: the triptych; mod3 (period-3 orbit); dupe (two language-equal
states — the partition must actually merge); ebeb (factored product:
multi-block global states, mixed-radix indexing); refusal probes
(residual readings on a phase-2 object raise; phases > 4 are refused).
A single case name as argv runs just that case. Stats streams land in
tests/sos_sdd/logs/residuals_<name>.jsonl."""

import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from e0_triptych import TRIPTYCH  # noqa: E402
from e2_async import product as eb_product  # noqa: E402
from phase2_test import MOD3  # noqa: E402

from sos_sdd import Automaton, Engine  # noqa: E402
from sos_sdd.model import Input  # noqa: E402
from sos_sdd.slotmodel import SlotModel, async_factored, from_automaton  # noqa: E402

LOGS = Path(__file__).resolve().parent / "logs"

Elem = Tuple[int, ...]

# Two states with identical rows (1, 2 — language-equal, the partition
# must merge them) and a rejecting sink (0 — its own class).
DUPE = Automaton("dupe", ("a",), 3, 0, 1, "Inf(0)", (
    (0, "a", 0, set()), (0, "!a", 0, set()),
    (1, "a", 1, {0}), (1, "!a", 2, set()),
    (2, "a", 1, {0}), (2, "!a", 2, set())))

# The seed is not the gfp here: L(0) = a·(!a)^ω is nonempty, but every
# pure-loop verdict A(0, x) is 0 (iterating any x through 0 falls into
# the dead state 3), so the profile columns merge 0 with {1, 3} and only
# the lockstep refinement splits it off via the a-step (2 vs 3).
# Expected partition: {0} | {1, 3} | {2} — one splitting round plus the
# confirming one.
STEM = Automaton("stem", ("a",), 4, 0, 1, "Inf(0)", (
    (0, "a", 2, set()), (0, "!a", 3, set()),
    (1, "a", 3, set()), (1, "!a", 3, set()),
    (2, "a", 3, set()), (2, "!a", 2, {0}),
    (3, "a", 3, set()), (3, "!a", 3, set())))


def blocks_of(model: SlotModel) -> List[Tuple[int, int]]:
    """(first slot, state count) per component block, from block_base."""
    starts = [s for s in range(len(model.doms)) if model.block_base[s] == s]
    ends = starts[1:] + [len(model.doms)]
    return list(zip(starts, [e - s for s, e in zip(starts, ends)]))


def globals_of(blocks: Sequence[Tuple[int, int]]) -> List[Tuple[int, ...]]:
    """Global states as local-state tuples, block 0 most significant —
    the engine's mixed-radix order."""
    out: List[Tuple[int, ...]] = [()]
    for _, size in blocks:
        out = [g + (p,) for g in out for p in range(size)]
    return out


def gt_verdict(g: Tuple[int, ...], x: Elem, model: SlotModel,
               blocks: Sequence[Tuple[int, int]]) -> int:
    """A(g, x) by explicit cycle walk, blockwise: iterate the state map of
    x from the local state, union the marks around the closed cycle,
    evaluate the block's acceptance table; conjunction across blocks."""
    for b, (start, _) in enumerate(blocks):
        bits = model.mark_bits[start]
        mask = (1 << bits) - 1
        seen: List[int] = []
        p = g[b]
        while p not in seen:
            seen.append(p)
            p = x[start + p] >> bits
        cycle = seen[seen.index(p):]
        inf = 0
        for q in cycle:
            inf |= x[start + q] & mask
        if inf not in model.accept[start]:
            return 0
    return 1


def gt_partition(elems: Sequence[Elem], model: SlotModel) -> List[Tuple[int, ...]]:
    """The residual partition of the global states: seed by the full
    verdict vector, refine by lockstep letter steps to the gfp."""
    blocks = blocks_of(model)
    gstates = globals_of(blocks)
    bits = [model.mark_bits[s] for s, _ in blocks]
    delta = [[tuple((model.classes[c].maps[s + p][model.identity[s + p]]
                     >> bits[b])
                    for b, (s, _) in enumerate(blocks) for p in (g[b],))
              for c in range(len(model.classes))]
             for g in gstates]
    index = {g: i for i, g in enumerate(gstates)}
    labels = _canon([tuple(gt_verdict(g, x, model, blocks) for x in elems)
                     for g in gstates])
    while True:
        new = _canon([(labels[i],
                       tuple(labels[index[d]] for d in delta[i]))
                      for i in range(len(gstates))])
        if new == labels:
            break
        labels = new
    classes: Dict[int, List[int]] = {}
    for i, l in enumerate(labels):
        classes.setdefault(l, []).append(i)
    return sorted((tuple(v) for v in classes.values()), key=lambda c: c[0])


def _canon(keys: Sequence) -> List[int]:
    seen: Dict = {}
    return [seen.setdefault(k, len(seen)) for k in keys]


def check(aut: Input, model: SlotModel) -> None:
    log = LOGS / f"residuals_{model.name}.jsonl"
    eng = Engine(square="off", stats=str(log))
    s = eng.build(aut, until_phase=4)

    blocks = blocks_of(model)
    gstates = globals_of(blocks)
    assert s.n_states() == len(gstates), (model.name, s.n_states())
    elems = [tuple(e) for e in s.elements()]

    # Phase 3: every verdict bit, engine (symbolic column membership)
    # against the cycle-walk ground truth.
    engine_rows: Dict[Elem, Tuple[int, ...]] = {
        tuple(x): tuple(bits) for x, bits in s.profile_rows()}
    assert len(engine_rows) == len(elems), model.name
    for x in elems:
        want = tuple(gt_verdict(g, x, model, blocks) for g in gstates)
        assert engine_rows[x] == want, (model.name, x, engine_rows[x], want)

    # Phase 4: the partition itself.
    got = sorted((tuple(c) for c in s.residual_classes()), key=lambda c: c[0])
    want_part = gt_partition(elems, model)
    assert got == want_part, (model.name, got, want_part)
    print(f"{model.name}: states={len(gstates)} "
          f"residual_classes={len(got)} sizes={[len(c) for c in got]}")


def case_triptych(name: str) -> None:
    aut = next(a for a, _ in TRIPTYCH if a.name == name)
    check(aut, from_automaton(aut))


def case_ebeb() -> None:
    ebeb = eb_product(2)
    check(ebeb, async_factored(ebeb))


def case_refuse() -> None:
    # Residual readings on a phase-2 object must refuse.
    s2 = Engine(square="off").build(DUPE, until_phase=2)
    for reading in ("residual_classes", "n_states", "profile_rows"):
        try:
            getattr(s2, reading)()
            raise AssertionError(f"{reading} on a phase-2 object did not raise")
        except RuntimeError:
            pass
    # Beyond-ceiling refusals live with the ceiling: phase-6 probes are
    # conformance_test's (products, non-default quotient switch).


CASES = {
    "gf_aa_parity": lambda: case_triptych("gf_aa_parity"),
    "even": lambda: case_triptych("even"),
    "evenblocks": lambda: case_triptych("evenblocks"),
    "mod3": lambda: check(MOD3, from_automaton(MOD3)),
    "dupe": lambda: check(DUPE, from_automaton(DUPE)),
    "stem": lambda: check(STEM, from_automaton(STEM)),
    "ebeb": case_ebeb,
    "refuse": case_refuse,
}


def main() -> None:
    LOGS.mkdir(exist_ok=True)
    for name in (sys.argv[1:] or CASES):
        CASES[name]()
    print("SUCCESS")


if __name__ == "__main__":
    main()
