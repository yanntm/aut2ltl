"""The mid-learning hypothesis (Cayley form) and its normative prediction.

A `Hypothesis` is what an equivalence query ships. It is deliberately weaker
than an `Invariant`: during learning no class multiplication table is trusted,
so a hypothesis carries only

  - ``keys[c]`` — the current key of class ``c``;
  - ``step[c][a]`` — the class reached by reading letter ``a`` from class ``c``
    (a right action, ``step(c, a) = class(rep(c).a)``), the "Cayley" table;
  - ``accept`` — a *partial* cache of accepting-pair verdicts (the P-cache);
  - ``start`` — the class of the empty word, where every fold begins.

`predict` is the single normative meaning of a hypothesis, used identically by
the teacher (to hunt counterexamples) and the learner (to stay in sync): fold
stem and loop through ``step`` from ``start``, stabilize the loop to a power
``k`` (the stand-in for an idempotent before a multiplication table exists), and
answer the cached bit for the resulting ``(stem-value, loop-value)`` pair.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from sosl.objects.alphabet import Alphabet, Word
from sosl.objects.lasso import Lasso


@dataclass(frozen=True)
class Hypothesis:
    """A Cayley-form hypothesis; see the module docstring for the field
    contract. ``accept`` may be partial — a missing pair means "not yet
    decided", surfaced by `predict` returning ``None``."""

    alphabet: Alphabet
    keys: Tuple[Word, ...]
    step: Tuple[Tuple[int, ...], ...]
    accept: Dict[Tuple[int, int], bool]
    start: int

    @property
    def n(self) -> int:
        """The number of classes."""
        return len(self.keys)

    def _sfold(self, c: int, word: Word) -> int:
        """The class reached by reading ``word`` from class ``c`` via ``step``."""
        for a in word:
            c = self.step[c][a]
        return c

    def class_of(self, word: Word) -> int:
        """The class of ``word``, folding from ``start``."""
        return self._sfold(self.start, word)

    def stabilized_pair(self, lasso: Lasso) -> Tuple[int, int]:
        """The pair ``(s, e)`` this hypothesis reduces ``lasso`` to: ``e`` is the
        loop folded to its stabilization power ``k`` (least ``k <= 2n`` with
        ``fold(loop^{2k}) == fold(loop^k)``), and ``s`` is the stem followed by
        ``k`` loops, both folded through ``step`` from ``start``."""
        n = self.n
        # efold[j] = fold(loop^j) from start, incrementally (loop^0 = eps).
        efold = [self.start]
        for _ in range(4 * n):
            efold.append(self._sfold(efold[-1], lasso.loop))
        k = next(k for k in range(1, 2 * n + 1) if efold[2 * k] == efold[k])
        e = efold[k]
        s = self._sfold(self.class_of(lasso.stem), lasso.loop * k)
        return (s, e)

    def predict(self, lasso: Lasso) -> Optional[bool]:
        """The cached verdict for ``lasso``, or ``None`` if the reduced pair is
        not yet in the cache (the caller must then query the teacher)."""
        return self.accept.get(self.stabilized_pair(lasso))
