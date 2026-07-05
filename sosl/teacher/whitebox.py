"""The white-box teacher: a `Teacher` over a known deterministic, complete,
transition-based Emerson-Lei automaton D (a spot ``twa_graph``).

Membership is decided by pure simulation of the lasso on D — no external tools,
no timeouts. At construction the automaton is compiled once into per-letter
transition and mark tables indexed by the sosl letter mask (over the alphabet's
canonical AP order), so a query walks integer tables and evaluates the
Emerson-Lei condition on the marks of the closed loop.

This module is spot-backed (it lives above the contract floor, on the teacher
side); the learner never imports it.
"""
from __future__ import annotations

from typing import Dict, List, Optional

import buddy
import spot

from sosl.contract import Counterexample, Equivalent, EquivResult
from sosl.objects.alphabet import Alphabet, Letter
from sosl.objects.cayley import Hypothesis
from sosl.objects.lasso import Lasso
from sosl.teacher.equiv import bounded_counterexample


def _prepare(aut: "spot.twa_graph") -> "spot.twa_graph":
    """Return a deterministic, complete view of ``aut`` (completion adds a
    rejecting sink if needed); raise if it is not deterministic."""
    aut = spot.complete(aut)
    if not spot.is_deterministic(aut):
        raise ValueError("HoaTeacher requires a deterministic automaton")
    return aut


class HoaTeacher:
    """A membership teacher over a deterministic complete EL automaton.

    ``alphabet`` is the automaton's AP set in canonical order; letters are masks
    over it. Construct via `of_hoa` / `of_ltl`, or directly from a prepared
    ``twa_graph``.
    """

    def __init__(self, aut: "spot.twa_graph", eq_bound: int = 8) -> None:
        self.aut = _prepare(aut)
        self.acc = self.aut.acc()
        self.init = self.aut.get_init_state_number()
        self.eq_bound = eq_bound
        # AP name -> buddy variable, registered once before any BDD op.
        self._var: Dict[str, int] = {
            ap.ap_name(): self.aut.register_ap(ap) for ap in self.aut.ap()
        }
        self.alphabet = Alphabet.of(self._var.keys())
        self._compile()

    @classmethod
    def of_hoa(cls, path: str) -> "HoaTeacher":
        """Load a HOA automaton file as a teacher."""
        return cls(spot.automaton(path))

    @classmethod
    def of_ltl(cls, formula: str) -> "HoaTeacher":
        """Translate an LTL/PSL formula to a deterministic automaton teacher."""
        return cls(spot.translate(formula, "deterministic", "generic"))

    # -- compilation ---------------------------------------------------------

    def _point_bdd(self, mask: int) -> "buddy.bdd":
        """The full minterm for the letter ``mask`` over the canonical AP order."""
        point = buddy.bddtrue
        for i, name in enumerate(self.alphabet.aps):
            var = self._var[name]
            lit = buddy.bdd_ithvar(var) if (mask >> i) & 1 else buddy.bdd_nithvar(var)
            point = point & lit
        return point

    def _compile(self) -> None:
        """Build ``_dst[mask][state]`` and ``_mark[mask][state]`` from D's edges."""
        n = self.aut.num_states()
        size = self.alphabet.size
        self._dst: List[List[int]] = [[-1] * n for _ in range(size)]
        self._mark: List[List["spot.mark_t"]] = [[None] * n for _ in range(size)]
        for mask in range(size):
            point = self._point_bdd(mask)
            for s in range(n):
                for e in self.aut.out(s):
                    if (e.cond & point) != buddy.bddfalse:
                        self._dst[mask][s] = e.dst
                        self._mark[mask][s] = e.acc
                        break
                if self._dst[mask][s] < 0:
                    raise ValueError(
                        f"automaton not complete at state {s} under letter {mask}"
                    )

    # -- membership ----------------------------------------------------------

    def member(self, lasso: Lasso) -> bool:
        """Is ``lasso`` accepted by D? Simulate the stem, then the loop until the
        (state, loop-position) pair repeats; the marks on that closed cycle are
        the infinitely-often set, which the Emerson-Lei condition judges."""
        q = self.init
        for a in lasso.stem:
            q = self._dst[a][q]
        loop = lasso.loop
        length = len(loop)
        seen: Dict[tuple, int] = {}
        trace: List["spot.mark_t"] = []
        config = (q, 0)
        while config not in seen:
            seen[config] = len(trace)
            st, pos = config
            a: Letter = loop[pos]
            trace.append(self._mark[a][st])
            config = (self._dst[a][st], (pos + 1) % length)
        inf = spot.mark_t()
        for m in trace[seen[config]:]:
            inf |= m
        return bool(self.acc.accepting(inf))

    # -- equivalence ---------------------------------------------------------

    def equiv(self, hypothesis: Hypothesis, bound: Optional[int] = None) -> EquivResult:
        """Decide whether ``hypothesis`` captures L by bounded lasso enumeration
        (up to ``bound``, default ``eq_bound``). Returns `Equivalent` tagged with
        the certifying bound, or a minimal `Counterexample`."""
        b = self.eq_bound if bound is None else bound
        cx, complete = bounded_counterexample(self.member, self.alphabet, hypothesis, b)
        if cx is None:
            return Equivalent(strategy=f"bounded:{b}" if complete else f"bounded:{b}:capped")
        return Counterexample(lasso=cx)
