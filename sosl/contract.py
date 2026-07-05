"""The Teacher contract — the learner's only source of truth about the target
language L.

A `Teacher` answers the two queries of active learning over an unknown
omega-regular language:

  * **membership** — is a given `Lasso` (the word u.v^omega) in L?
  * **equivalence** — does a `Hypothesis` capture L? If not, return a lasso on
    which they disagree.

The learner in `sosl.learn` is written against this Protocol and nothing else —
no automaton, no spot, no reference builder. Concrete teachers live in
`sosl.teacher`. This is a contract-floor module: it names only vocabulary from
`sosl.objects` and defines behavioural types; it depends on no implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Union

from sosl.objects.cayley import Hypothesis
from sosl.objects.lasso import Lasso


@dataclass(frozen=True)
class Equivalent:
    """The hypothesis agrees with L on every lasso, certified by ``strategy``
    (e.g. ``"reps"``, ``"bounded:8"``, ``"exact"``) — recorded so a run
    certified only by an incomplete strategy can be flagged."""

    strategy: str


@dataclass(frozen=True)
class Counterexample:
    """A lasso on which hypothesis and L disagree. It is minimized (shortest
    stem, then shortest loop, then shortlex) before being returned, so the
    learner's response to it is deterministic."""

    lasso: Lasso


# The result of an equivalence query: agreement, or a witnessing lasso.
EquivResult = Union[Equivalent, Counterexample]


class Teacher(Protocol):
    """The membership + equivalence oracle the learner queries.

    A concrete `Teacher` decides an omega-regular language; the learner sees
    only these two methods and never how the language is presented.
    """

    def member(self, lasso: Lasso) -> bool:
        """Is ``lasso`` (the ultimately-periodic word u.v^omega) in L?"""
        ...

    def equiv(self, hypothesis: Hypothesis) -> EquivResult:
        """Decide whether ``hypothesis`` captures L, returning `Equivalent` or a
        minimized `Counterexample`."""
        ...
