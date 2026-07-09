"""C7 mechanism test: the engine's shortlex extraction (backward
can-reach sets + forward least-class walk) against a ground truth that
computes shortlex words the direct way — BFS from the identity taking
letter classes in canonical order, first word wins. Every EM1 element of
every triptych instance must get the exact same word, and the longest
word must equal the closure depth."""

import sys
from collections import deque
from pathlib import Path
from typing import Dict, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sos_sdd import Automaton, Engine  # noqa: E402
from sos_sdd.letters import letter_classes  # noqa: E402
from e0_triptych import TRIPTYCH  # noqa: E402

Elem = Tuple[Tuple[int, int], ...]
Word = Tuple[str, ...]


def gt_shortlex(aut: Automaton) -> Dict[Elem, Word]:
    """First-reach words of a FIFO BFS with classes in least-letter order
    are shortlex-least: parents dequeue in shortlex order of their own
    words, children extend them in letter order."""
    classes = letter_classes(aut)
    identity: Elem = tuple((q, 0) for q in range(aut.states))
    words: Dict[Elem, Word] = {identity: ()}
    queue = deque([identity])
    while queue:
        elem = queue.popleft()
        for c in classes:
            stepped: Elem = tuple((c.dst[q], marks | c.marks[q])
                                  for q, marks in elem)
            if stepped not in words:
                words[stepped] = words[elem] + (c.least,)
                queue.append(stepped)
    return words


def main() -> None:
    for aut, expected in TRIPTYCH:
        gt = gt_shortlex(aut)
        assert len(gt) == expected, (aut.name, len(gt))

        s = Engine().build(aut, until_phase=1)
        engine_words = {tuple(elem): word for elem, word in s.shortlex_words()}
        assert len(engine_words) == expected, (aut.name, len(engine_words))
        for elem, word in engine_words.items():
            assert gt[elem] == word, (aut.name, elem, word, gt[elem])
        assert max(len(w) for w in engine_words.values()) == s.depth
        print(f"{aut.name}: {len(engine_words)} shortlex words exact, "
              f"longest={s.depth}")
    print("SUCCESS")


if __name__ == "__main__":
    main()
