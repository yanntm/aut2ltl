"""The Teacher contract — the learner's only source of truth about the target
language L.

A `Teacher` answers the two queries of active learning over an unknown
omega-regular language:

  * **membership** — is a given `Lasso` (the word u.v^omega) in L?
  * **equivalence** — does a hypothesis capture L? If not, return a lasso on
    which they disagree.

A hypothesis is an `Invariant`, point blank: the learner never poses anything
that is not a language, and a well-formed invariant denotes exactly one — its
own. The teacher therefore reads the hypothesis algebraically (its `member`
read-off is total and normative); no operational prediction, no partial cache,
no acceptor-shaped object crosses this interface.

The learner in `sosl.learn` is written against this Protocol and nothing else —
no automaton, no spot, no reference builder. Concrete teachers live in
`sosl.teacher`. This is a contract-floor module: it names only vocabulary from
`sosl.sos` and defines behavioural types; it depends on no implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Union

from sosl.sos.invariant import Invariant
from sosl.sos.lasso import Lasso


@dataclass(frozen=True)
class Equivalent:
    """The hypothesis agrees with L on every lasso, certified by ``strategy``
    (e.g. ``"exact"``, ``"bounded:8"``) — recorded so a run certified only by
    an incomplete strategy can be flagged."""

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

    def equiv(self, hypothesis: Invariant) -> EquivResult:
        """Decide whether the well-formed invariant ``hypothesis`` denotes L,
        returning `Equivalent` or a minimized `Counterexample`."""
        ...
