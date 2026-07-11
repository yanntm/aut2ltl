"""C9 slot_perm gate: the slot permutation is an indirection, never a
re-semantics — every reading of a build under "reverse" and under a
nontrivial rotation must equal the "natural" build's exactly (elements,
layer profile, pi pairs, residual and congruence partitions), and the
emitted .sos must be byte-identical (natural's is already
conformance-gated, so perm==natural transfers the gate). Node counts MAY
differ across perms — that is E7's measurement, printed, never asserted.

Cases: the triptych, mod3, stem (full pipeline to .sos, square="check"
so the squaring space is exercised under the perm too); ebeb (factored
product, multi-block, to phase 5); refusal probes (non-bijective list,
unknown string). A single case name as argv runs just that case. Stats
streams land in tests/sos_sdd/logs/slotperm_<name>.jsonl."""

import sys
from pathlib import Path
from typing import List, Sequence, Tuple, Union

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from e0_triptych import TRIPTYCH  # noqa: E402
from e2_async import product as eb_product  # noqa: E402
from phase2_test import MOD3  # noqa: E402
from residuals_test import STEM  # noqa: E402

from sos_sdd import Engine  # noqa: E402
from sos_sdd.model import Input  # noqa: E402

LOGS = Path(__file__).resolve().parent / "logs"

Perm = Union[str, Sequence[int]]


def rotation(n: int) -> List[int]:
    return list(range(1, n)) + [0]


def readings(s) -> Tuple:
    """Every perm-invariant reading, in comparable form."""
    return (
        s.em1_count(),
        s.depth,
        [(k, card) for k, card, _ in s.layers],
        sorted(tuple(e) for e in s.elements()),
        sorted((tuple(x), tuple(y)) for x, y in s.pi_pairs()),
        s.residual_classes(),
        sorted((sorted(tuple(e) for e in cls)
                for cls in s.congruence_classes()), key=lambda c: c[0]),
    )


def check(aut: Input, n_slots: int, until_phase: int = 6) -> None:
    perms: List[Tuple[str, Perm]] = [
        ("natural", "natural"), ("reverse", "reverse"),
        ("rotation", rotation(n_slots))]
    builds = []
    for tag, perm in perms:
        log = LOGS / f"slotperm_{aut.name}_{tag}.jsonl"
        eng = Engine(square="check", slot_perm=perm, stats=str(log))
        builds.append((tag, eng.build(aut, until_phase=until_phase)))
    (_, ref), rest = builds[0], builds[1:]
    want = readings(ref)
    for tag, s in rest:
        got = readings(s)
        assert got == want, (aut.name, tag)
        if until_phase >= 6:
            assert s.to_sos() == ref.to_sos(), (aut.name, tag, "sos bytes")
    nodes = ", ".join(f"{tag}={s.nodes[0]}" for tag, s in builds)
    print(f"{aut.name}: |EM1|={want[0]:.0f} depth={want[1]} "
          f"nodes_final [{nodes}]")


def case_triptych(name: str) -> None:
    aut = next(a for a, _ in TRIPTYCH if a.name == name)
    check(aut, aut.states)


def case_refuse() -> None:
    for bad in ([0, 0, 1], [0, 1], [0, 2, 3]):
        try:
            Engine(square="off", slot_perm=bad).build(MOD3, until_phase=1)
            raise AssertionError(f"slot_perm={bad} was not refused")
        except ValueError:
            pass
    try:
        Engine(square="off", slot_perm="sideways").build(MOD3, until_phase=1)
        raise AssertionError("slot_perm=sideways was not refused")
    except NotImplementedError:
        pass


CASES = {
    "gf_aa_parity": lambda: case_triptych("gf_aa_parity"),
    "even": lambda: case_triptych("even"),
    "evenblocks": lambda: case_triptych("evenblocks"),
    "mod3": lambda: check(MOD3, MOD3.states),
    "stem": lambda: check(STEM, STEM.states),
    "ebeb": lambda: check(eb_product(2), 4, until_phase=5),
    "refuse": case_refuse,
}


def main() -> None:
    LOGS.mkdir(exist_ok=True)
    for name in (sys.argv[1:] or CASES):
        CASES[name]()
    print("SUCCESS")


if __name__ == "__main__":
    main()
