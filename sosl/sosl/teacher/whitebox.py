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

from typing import Dict, List, Optional, Tuple

import buddy
import spot

from sosl.contract import Counterexample, Equivalent, EquivResult
from sosl.sos.alphabet import Alphabet, Letter
from sosl.sos.build import canonical
from sosl.sos.calculus import PairSet, Table
from sosl.sos.core.quotient import invariant_of
from sosl.sos.hypothesis import Hypothesis, loop_reps
from sosl.sos.invariant import Invariant
from sosl.sos.lasso import Lasso
from sosl.teacher.equiv import bounded_counterexample, resolve_prediction
from sosl.teacher.exact import ExactTooLarge, exact_counterexample
from sosl.teacher.exact_ref import (
    NotFunctional,
    exact_ref_counterexample,
    reference_table,
)


def _pump(lasso: Lasso, k: int) -> Lasso:
    """Inflate a lasso by factor ``k`` while denoting the same ω-word:
    ``(u, v) -> (u.v^(k-1), v^k)`` (both stem and loop grow, and
    ``u.v^(k-1).(v^k)^ω = u.v^ω``). ``k <= 1`` is the identity."""
    if k <= 1:
        return lasso
    return Lasso(lasso.stem + lasso.loop * (k - 1), lasso.loop * k)


def _prepare(aut: "spot.twa_graph") -> "spot.twa_graph":
    """Return the deterministic, complete form D of ``aut`` via the sos import
    layer, determinizing and completing a nondeterministic or partial input."""
    return canonical(aut)


class HoaTeacher:
    """A membership teacher over a deterministic complete EL automaton.

    ``alphabet`` is the automaton's AP set in canonical order; letters are masks
    over it. Construct via `of_hoa` / `of_ltl`, or directly from a prepared
    ``twa_graph``.

    ``reference`` is the language's invariant, the decision structure of
    ``eq_mode="exact"``. When it is not supplied it is built from the automaton
    on the first exact query and cached; a language whose algebra blows the
    construction's cap has none, and exact mode then falls back to the
    transformation-closure oracle (`sosl.teacher.exact`).

    ``cap_escape`` lets an exact query whose closure fallback exceeds its work cap
    answer by bounded enumeration instead of raising: the escape of a leg that a
    later byte-equality still validates. A leg that certifies a *stall* must leave
    it off — a bounded answer cannot certify permanence.
    """

    def __init__(
        self, aut: "spot.twa_graph", eq_bound: int = 8, eq_mode: str = "bounded",
        cex_policy: str = "minimal", reference: Optional[Invariant] = None,
        cap_escape: bool = False,
    ) -> None:
        self.aut = _prepare(aut)
        self.acc = self.aut.acc()
        self.init = self.aut.get_init_state_number()
        self.eq_bound = eq_bound
        self.eq_mode = eq_mode
        self.cex_policy = cex_policy
        self._reference: Optional[Invariant] = reference
        self._ref_built = reference is not None
        self._ref_table: Optional[Tuple[Table, PairSet]] = None
        self.cap_escape = cap_escape
        self.guard_firings: List[NotFunctional] = []
        self.last_query_fired = False
        # AP name -> buddy variable, registered once before any BDD op.
        self._var: Dict[str, int] = {
            ap.ap_name(): self.aut.register_ap(ap) for ap in self.aut.ap()
        }
        self.alphabet = Alphabet.of(self._var.keys())
        self._compile()

    @classmethod
    def of_hoa(cls, path: str, eq_mode: str = "bounded",
               reference: Optional[Invariant] = None) -> "HoaTeacher":
        """Load a HOA automaton file as a teacher, optionally over a precomputed
        reference invariant of its language (the corpus `.sos`)."""
        return cls(spot.automaton(path), eq_mode=eq_mode, reference=reference)

    @classmethod
    def of_ltl(cls, formula: str, eq_mode: str = "bounded") -> "HoaTeacher":
        """Translate an LTL/PSL formula to a deterministic automaton teacher."""
        return cls(spot.translate(formula, "deterministic", "generic"), eq_mode=eq_mode)

    # -- compilation ---------------------------------------------------------

    def _point_bdd(self, mask: int) -> "buddy.bdd":
        """The full minterm for the letter ``mask`` over the canonical AP order.
        The bit layout is delegated to `Alphabet.true_aps`, so this is agnostic
        to how masks encode propositions."""
        trues = set(self.alphabet.true_aps(Letter(mask)))
        point = buddy.bddtrue
        for name, var in self._var.items():
            lit = buddy.bdd_ithvar(var) if name in trues else buddy.bdd_nithvar(var)
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

    def reference(self) -> Optional[Tuple[Table, PairSet]]:
        """The reference invariant as an algebra and a pair set, built once from
        D and cached, or ``None`` when the algebra's closure blows its cap. The
        decision structure of exact-by-reference equivalence."""
        if not self._ref_built:
            self._reference = invariant_of(self.aut)
            self._ref_built = True
        if self._reference is None:
            return None
        if self._ref_table is None:
            assert self._reference.alphabet.aps == self.alphabet.aps, \
                "reference/teacher alphabet mismatch"
            self._ref_table = reference_table(self._reference)
        return self._ref_table

    def equiv(self, hypothesis: Hypothesis, bound: Optional[int] = None) -> EquivResult:
        """Decide whether ``hypothesis`` captures L, per ``self.eq_mode``:
        ``"bounded"`` (lasso enumeration up to ``bound``, default ``eq_bound`` —
        complete only in the limit) or ``"exact"`` (complete). Returns
        `Equivalent` tagged with the certifying strategy, or a minimal
        `Counterexample`.

        Exact mode decides against the reference invariant in the SoS calculus
        (`sosl.teacher.exact_ref`), which is polynomial. Only a language with no
        reference — the algebra's closure blew its cap — takes the
        transformation-closure oracle (`sosl.teacher.exact`), which may raise
        `ExactTooLarge`."""
        if self.eq_mode == "exact":
            cx, strategy = self._exact(hypothesis)
            if cx is None:
                return Equivalent(strategy=strategy)
            return Counterexample(lasso=self._policy_cex(cx, hypothesis))
        b = self.eq_bound if bound is None else bound
        cx, complete = bounded_counterexample(self.member, self.alphabet, hypothesis, b)
        if cx is None:
            return Equivalent(strategy=f"bounded:{b}" if complete else f"bounded:{b}:capped")
        return Counterexample(lasso=self._policy_cex(cx, hypothesis))

    def _exact(self, hypothesis: Hypothesis) -> Tuple[Optional[Lasso], str]:
        """The exact decision: ``(minimal counterexample, certifying strategy)``,
        the lasso being ``None`` when the hypothesis is exactly correct.

        The escalation of spec §3.2. Exact-by-reference decides the query when a
        reference exists and its aligned graph passes the functionality guard.
        A firing (recorded in ``guard_firings``, row F10) or a referenceless
        target sends the query to the transformation-closure oracle. Should that
        exceed its work cap, `ExactTooLarge` propagates — permanence cannot be
        certified below the cap — unless ``cap_escape`` is set, when the query
        falls to ``bounded:<eq_bound>`` instead and says so in its strategy."""
        ref = self.reference()
        self.last_query_fired = False
        if ref is not None:
            try:
                cx, _ = exact_ref_counterexample(
                    self.member, self.alphabet, hypothesis, *ref)
                return cx, "exact"
            except NotFunctional as exc:
                self.guard_firings.append(exc)
                self.last_query_fired = True
        try:
            cx, _ = exact_counterexample(
                self.member, self.alphabet, hypothesis,
                self._dst, self._mark, self.init, self.aut.num_states())
            return cx, "exact"
        except ExactTooLarge:
            if not self.cap_escape:
                raise
        b = self.eq_bound
        cx, complete = bounded_counterexample(self.member, self.alphabet, hypothesis, b)
        return cx, f"bounded:{b}" if complete else f"bounded:{b}:capped"

    def _policy_cex(self, cx: Lasso, hypothesis: Hypothesis) -> Lasso:
        """Apply ``cex_policy`` to the oracle's (minimal) counterexample.

        ``minimal`` / ``first`` return it unchanged — both our oracles enumerate
        in minimal (shortlex-least) order, so first-found already *is* minimal.
        ``padded:<k>`` pumps it by ``k`` (spec §6 E5), but only if the pumped
        lasso is still a genuine hypothesis/teacher disagreement — otherwise the
        minimal one is kept (never hand the learner a lasso it predicts correctly,
        spec §9 F3)."""
        policy = self.cex_policy
        if not policy or policy in ("minimal", "first"):
            return cx
        if policy.startswith("padded:"):
            k = int(policy.split(":", 1)[1])
            padded = _pump(cx, k)
            loops = loop_reps(hypothesis)
            if resolve_prediction(self.member, hypothesis, padded, loops) \
                    != self.member(padded):
                return padded
            return cx
        raise ValueError(f"unknown cex_policy {policy!r}")
