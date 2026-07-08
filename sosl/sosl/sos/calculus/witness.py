"""The certificate every decision procedure carries: a lasso and the bit it is
supposed to have.

A `Witness` is what makes a decision replayable against an *independent* oracle
— another invariant's membership read-off, a teacher, a bounded external model
checker. `replay` takes any membership callable and asserts the recorded bit, so
nothing in this package needs to know what the other side is (in particular no
external tool is imported here; the hook is injected).

Provenance records which operation produced the witness and from which cell, so
a failing gate names the cell to look at rather than "somewhere in the scan".
Rendering is deterministic — a witness line is a stable fixture byte string.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Tuple

from ..alphabet import Alphabet, Word
from ..io.serialize import render_word
from ..lasso import Lasso

Oracle = Callable[[Word, Word], bool]
"""A membership callable: ``(stem, loop) -> is stem.loop^omega in the language``."""


@dataclass(frozen=True)
class Witness:
    """The lasso ``stem.loop^omega``, the bit ``expected`` it carries for the
    language named in ``operation``, and the ``cell`` (a stem class id and a
    loop class id, in the producing table or aligned product) it was read off."""

    alphabet: Alphabet
    stem: Word
    loop: Word
    expected: bool
    operation: str
    cell: Tuple[int, int]

    @property
    def lasso(self) -> Lasso:
        """The witness as a `Lasso`."""
        return Lasso(self.stem, self.loop)

    def render(self) -> str:
        """The canonical one-line form: ``op cell=(c,d) stem=... loop=... bit=1``."""
        return (
            f"{self.operation} cell=({self.cell[0]},{self.cell[1]}) "
            f"stem={render_word(self.alphabet, self.stem)} "
            f"loop={render_word(self.alphabet, self.loop)} "
            f"bit={1 if self.expected else 0}"
        )

    def replay(self, oracle: Oracle) -> None:
        """Assert that ``oracle`` agrees with the recorded bit on this lasso.
        Raises `AssertionError` naming the witness on disagreement."""
        got = oracle(self.stem, self.loop)
        assert got == self.expected, f"replay disagrees ({got}): {self.render()}"
