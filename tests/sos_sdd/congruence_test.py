"""Phase 5 (C6) gate: the syntactic congruence checked against an
explicit ground truth — seed each element by its residual-class signature
(~lin) and loop-verdict signature (~w) computed the explicit way
(residuals_test's cycle walks), then refine by explicit right
translations x -> x·a until stable (the sosl-style algorithm). The
engine's symbolic preimage refinement must land on the identical
partition of EM1.

Cases: the triptych (evenblocks quotients 16 elements to 7 classes, the
identity class absorbing [[aa]] per [SwS26, Table 2(c)]; gf_aa_parity's
6 classes match the explicit tool's gfaa fixture count); mod3; dupe;
stem; ebeb (factored product, multi-block ~lin); refusal probes. A single case name as argv
runs just that case. Stats streams land in
tests/sos_sdd/logs/congruence_<name>.jsonl."""

import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from e0_triptych import TRIPTYCH  # noqa: E402
from e2_async import product as eb_product  # noqa: E402
from phase2_test import MOD3  # noqa: E402
from residuals_test import (  # noqa: E402
    DUPE, STEM, blocks_of, globals_of, gt_partition, gt_verdict)

from sos_sdd import Engine  # noqa: E402
from sos_sdd.model import Input  # noqa: E402
from sos_sdd.slotmodel import SlotModel, async_factored, from_automaton  # noqa: E402

LOGS = Path(__file__).resolve().parent / "logs"

Elem = Tuple[int, ...]


def gt_congruence(elems: Sequence[Elem], model: SlotModel) -> List[List[Elem]]:
    """The syntactic congruence by the explicit route: residual + verdict
    seed, right-translation refinement over the letter classes."""
    blocks = blocks_of(model)
    gstates = globals_of(blocks)
    gindex = {g: i for i, g in enumerate(gstates)}
    part = gt_partition(elems, model)
    state_label = [0] * len(gstates)
    for label, cls in enumerate(part):
        for g in cls:
            state_label[g] = label

    def st(x: Elem, g: Tuple[int, ...]) -> int:
        return gindex[tuple(x[s + g[b]] >> model.mark_bits[s]
                            for b, (s, _) in enumerate(blocks))]

    labels: Dict[Elem, object] = {
        x: (tuple(state_label[st(x, g)] for g in gstates),
            tuple(gt_verdict(g, x, model, blocks) for g in gstates))
        for x in elems}
    labels = _canon(labels)
    right = [{x: tuple(c.maps[q][x[q]] for q in range(len(x))) for x in elems}
             for c in model.classes]
    while True:
        new = _canon({x: (labels[x], tuple(labels[r[x]] for r in right))
                      for x in elems})
        if new == labels:
            break
        labels = new
    classes: Dict[int, List[Elem]] = {}
    for x in elems:
        classes.setdefault(labels[x], []).append(x)
    return sorted((sorted(v) for v in classes.values()), key=lambda c: c[0])


def _canon(keyed: Dict[Elem, object]) -> Dict[Elem, int]:
    seen: Dict[object, int] = {}
    return {x: seen.setdefault(k, len(seen)) for x, k in keyed.items()}


def check(aut: Input, model: SlotModel) -> None:
    log = LOGS / f"congruence_{model.name}.jsonl"
    eng = Engine(square="off", stats=str(log))
    s = eng.build(aut, until_phase=5)

    elems = [tuple(e) for e in s.elements()]
    got = sorted((sorted(tuple(e) for e in cls)
                  for cls in s.congruence_classes()), key=lambda c: c[0])
    want = gt_congruence(elems, model)
    assert got == want, (model.name, got, want)
    assert s.congruence_count() == len(want), model.name
    print(f"{model.name}: |EM1|={len(elems)} classes={len(want)} "
          f"sizes={sorted((len(c) for c in want), reverse=True)}")


def case_triptych(name: str) -> None:
    aut = next(a for a, _ in TRIPTYCH if a.name == name)
    check(aut, from_automaton(aut))


def case_refuse() -> None:
    # Congruence readings on a phase-4 object must refuse.
    s4 = Engine(square="off").build(DUPE, until_phase=4)
    for reading in ("congruence_count", "congruence_classes"):
        try:
            getattr(s4, reading)()
            raise AssertionError(f"{reading} on a phase-4 object did not raise")
        except RuntimeError:
            pass
    # Non-layered fp5 is still refused loudly (phase-6 refusal probes
    # are conformance_test's).
    try:
        Engine(square="off", fp5="saturation").build(DUPE, until_phase=5)
        raise AssertionError("fp5=saturation was not refused")
    except NotImplementedError:
        pass


CASES = {
    "gf_aa_parity": lambda: case_triptych("gf_aa_parity"),
    "even": lambda: case_triptych("even"),
    "evenblocks": lambda: case_triptych("evenblocks"),
    "mod3": lambda: check(MOD3, from_automaton(MOD3)),
    "dupe": lambda: check(DUPE, from_automaton(DUPE)),
    "stem": lambda: check(STEM, from_automaton(STEM)),
    "ebeb": lambda: check(eb_product(2), async_factored(eb_product(2))),
    "refuse": case_refuse,
}


def main() -> None:
    LOGS.mkdir(exist_ok=True)
    for name in (sys.argv[1:] or CASES):
        CASES[name]()
    print("SUCCESS")


if __name__ == "__main__":
    main()
