"""E0 (M1 gate): the symbolic closure on the triptych, checked against an
in-test explicit BFS ground truth and the spec constants |EM1| = 10/7/16
(sos_symbolic_spec.md E0). Digests transcribed from
samples/fixtures/hoa/sos/{gf_aa_parity,even,evenblocks}.hoa; stats
streams land in tests/sos_sdd/logs/e0_<name>.jsonl."""

import itertools
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sos_sdd import Automaton, Engine  # noqa: E402

LOGS = Path(__file__).resolve().parent / "logs"

TRIPTYCH = [
    (Automaton("gf_aa_parity", ("a",), 2, 0, 1, "Inf(0)", (
        (0, "a", 1, set()), (0, "!a", 0, set()),
        (1, "a", 0, {0}), (1, "!a", 0, set()))), 10),
    (Automaton("even", ("a",), 4, 2, 1, "Inf(0)", (
        (0, "1", 0, {0}),
        (1, "a", 2, set()), (1, "!a", 3, set()),
        (2, "!a", 0, set()), (2, "a", 1, set()),
        (3, "1", 3, set()))), 7),
    (Automaton("evenblocks", ("a",), 2, 0, 2, "Fin(0)&Inf(1)", (
        (0, "a", 1, set()), (0, "!a", 0, {1}),
        (1, "a", 0, set()), (1, "!a", 0, {0}))), 16),
]

Elem = Tuple[Tuple[int, int], ...]  # per slot: (state, mark mask)


def ground_truth(aut: Automaton) -> List[Set[Elem]]:
    """Explicit BFS layers of EM1, enumerating the (tiny) alphabet —
    deliberately a different algorithm from the engine's."""
    def matches(cube: str, bits: Tuple[int, ...]) -> bool:
        if cube == "1":
            return True
        for lit in cube.split("&"):
            name = lit.lstrip("!")
            want = 0 if lit.startswith("!") else 1
            if bits[aut.ap.index(name)] != want:
                return False
        return True

    def row(q: int, bits: Tuple[int, ...]) -> Tuple[int, int]:
        hits = [(t.dst, sum(1 << m for m in t.marks))
                for t in aut.trans if t.src == q and matches(t.cube, bits)]
        assert len(hits) == 1, (aut.name, q, bits, hits)
        return hits[0]

    letters = list(itertools.product((0, 1), repeat=len(aut.ap)))
    identity: Elem = tuple((q, 0) for q in range(aut.states))
    seen: Set[Elem] = {identity}
    layers: List[Set[Elem]] = [{identity}]
    frontier: Set[Elem] = {identity}
    while frontier:
        new: Set[Elem] = set()
        for elem in frontier:
            for bits in letters:
                stepped = tuple(
                    (lambda d, mk: (d, s_marks | mk))(*row(s_state, bits))
                    for (s_state, s_marks) in elem)
                if stepped not in seen:
                    seen.add(stepped)
                    new.add(stepped)
        if new:
            layers.append(new)
        frontier = new
    return layers


def main() -> None:
    LOGS.mkdir(exist_ok=True)
    for aut, expected in TRIPTYCH:
        gt = ground_truth(aut)
        gt_count = sum(len(layer) for layer in gt)
        assert gt_count == expected, (aut.name, gt_count, expected)

        eng = Engine(stats=str(LOGS / f"e0_{aut.name}.jsonl"))
        s = eng.build(aut, until_phase=1)
        cards: Dict[int, float] = {k: card for k, card, _ in s.layers}

        assert s.em1_count() == float(expected), (aut.name, s.em1_count())
        assert s.depth == len(gt) - 1, (aut.name, s.depth, len(gt) - 1)
        assert cards == {k: float(len(layer)) for k, layer in enumerate(gt)}, \
            (aut.name, cards)
        nodes_final, _ = s.nodes
        print(f"{aut.name}: |EM1|={int(s.em1_count())} depth={s.depth} "
              f"nodes={nodes_final} layers={[int(c) for _, c, _ in s.layers]}")
    print("SUCCESS")


if __name__ == "__main__":
    main()
