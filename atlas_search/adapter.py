"""Transfer current symbolic stamps to the historical exact teacher contract."""
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

from sosl.contract import Counterexample, Equivalent, EquivResult
from sosl.sos import Alphabet, Invariant, canonicalize
from sosl.sos.alphabet import Letter
from sosl.sos.hypothesis import Hypothesis
from sosl.sos.lasso import Lasso
from sosl.teacher.exact import DEFAULT_MAX_ELEMENTS, exact_counterexample
from sosl.teacher.exact_ref import (
    NotFunctional, exact_ref_counterexample, reference_table,
)
from synomega.sos import SymbolAlphabet
from synomega.sosio import load_sos

if TYPE_CHECKING:
    from synomega.sos import OStamp


class EffectiveAlphabet(Alphabet):
    """Exactly the listed symbols, using the historical alphabet interface.

    The inherited `aps` tuple carries symbol names for old equality checks.
    No Boolean-valuation expansion is performed.
    """

    @property
    def size(self) -> int:
        """Number of effective symbols."""
        return len(self.aps)

    def true_aps(self, letter: Letter) -> list[str]:
        """Render one effective symbol through old word-formatting clients."""
        return [self.aps[int(letter)]]

    def letter_of(self, trues: Iterable[str]) -> Letter:
        """Interpret a singleton symbol name, rather than a Boolean valuation."""
        names = tuple(trues)
        if len(names) != 1:
            raise ValueError("Expected exactly one effective symbol")
        return Letter(self.aps.index(names[0]))


def transfer(obj: OStamp, *, reverse: bool = False) -> Invariant:
    """Re-key the same reference algebra under an explicit symbol order."""
    if not isinstance(obj.stamp.alphabet, SymbolAlphabet):
        raise ValueError("Atlas input must use its effective symbolic alphabet")
    order = tuple(obj.stamp.alphabet.letters())
    if reverse:
        order = order[::-1]
    alphabet = EffectiveAlphabet(tuple(obj.stamp.alphabet.symbols[a] for a in order))
    return canonicalize(
        alphabet, obj.stamp.identity,
        tuple(obj.stamp.letter_map.class_of(a) for a in order),
        obj.stamp.mult, obj.accept,
    )


def read_reference(path: Path, *, reverse: bool = False) -> tuple[OStamp, Invariant]:
    """Read current SOS using its owner, then transfer through public data APIs."""
    obj = load_sos(path.read_text())
    return obj, transfer(obj, reverse=reverse)


class EmptyMark:
    """Empty transition marks through the closure oracle's `sets` interface."""

    def sets(self) -> tuple[int, ...]:
        """No acceptance marks are needed for a stamp's right action."""
        return ()


class StampTeacher:
    """Exact operational-hypothesis comparison against a supplied stamp.

    The unchanged closure oracle uses the reference's faithful right action;
    see README.md for why this determines the target's lasso verdicts.
    """

    def __init__(self, reference: Invariant, *,
                 max_elements: int = DEFAULT_MAX_ELEMENTS,
                 closure_only: bool = False) -> None:
        self.reference = reference
        self.alphabet = reference.alphabet
        self.max_elements = max_elements
        self.closure_only = closure_only
        self.ref_table, self.ref_pairs = reference_table(reference)
        self.dst = tuple(tuple(reference.mult[c][reference.letter_class[a]]
                               for c in range(reference.n))
                         for a in self.alphabet.letters())
        self.marks = tuple(tuple(EmptyMark() for _ in range(reference.n))
                           for _ in self.alphabet.letters())
        self.member_calls = 0
        self.n_equiv = 0
        self.guard_firings = 0
        self.last_query_fired = False
        self.closure_calls = 0
        self.counterexamples: list[Lasso] = []

    def member(self, lasso: Lasso) -> bool:
        """Reference membership; no model generation or native call."""
        self.member_calls += 1
        return self.reference.member(lasso)

    def equiv(self, hypothesis: Hypothesis) -> EquivResult:
        """Return exact assent or the least disagreeing lasso; never fall back to bounds."""
        self.n_equiv += 1
        self.last_query_fired = False
        use_closure = self.closure_only
        if not use_closure:
            try:
                witness, complete = exact_ref_counterexample(
                    self.member, self.alphabet, hypothesis,
                    self.ref_table, self.ref_pairs,
                )
            except NotFunctional:
                self.guard_firings += 1
                self.last_query_fired = True
                use_closure = True
        if use_closure:
            self.closure_calls += 1
            witness, complete = exact_counterexample(
                self.member, self.alphabet, hypothesis, self.dst, self.marks,
                self.reference.identity, self.reference.n, self.max_elements,
            )
        if not complete:
            raise AssertionError("Exact oracle returned an incomplete decision")
        if witness is None:
            return Equivalent(strategy="exact")
        self.counterexamples.append(witness)
        return Counterexample(witness)
