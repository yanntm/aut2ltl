"""Exact equivalence against a reference invariant — the SoS-calculus decision.

Decides whether a Cayley `Hypothesis` denotes the language of a reference
`Invariant` ``R``, and returns the shortlex-least disagreeing lasso when it does
not. Polynomial: no transformation closure is built, so there is no work cap and
no `ExactTooLarge` (contrast `sosl.teacher.exact`, which products the
hypothesis's transformation monoid with the automaton and is exponential in the
automaton's presentation).

The decision is emptiness of the symmetric difference, in the calculus. `align`
puts the two sides on one node set — the letter-generated pairs
``(fold_H(w), fold_R(w))``, at most ``n_H * n_R`` of them, each keyed by its
shortlex-least word — and `equivalent` scans its cells ``(stem node, loop node)``
in the counterexample discipline, reading one verdict per side per cell:

  - ``R``'s verdict is algebraic: ``Val_P(c, d) = (M(c, idem(d)), idem(d)) in P``,
    the membership of *every* lasso whose stem and loop fold to ``(c, d)``;
  - ``H``'s verdict is its normative prediction (`resolve_prediction`) on the
    cell's canonical lasso ``key(c).key(d)^omega`` — the cached bit of the pair
    the hypothesis stabilizes that lasso to, or the teacher's bit for that pair's
    representative lasso on a cache miss. No linked-pair or associativity law is
    ever applied to ``H``: a mid-learning Cayley form need not be a lawful
    algebra, and prediction is the only discipline it admits.

Reading ``H`` on the cell's *word* rather than on the bare class pair is what
makes the two sides comparable. A class pair ``(s, e)`` carries no bit of its
own: the P-cache is indexed by *stabilized* pairs, and stabilizing a loop means
iterating the loop word, which the pair has forgotten. The prediction on the
node's key does that iteration.

**The functionality guard.** One keyed lasso decides a whole cell only if the
hypothesis's prediction is constant on that cell, which holds exactly when the
aligned graph is *functional*: no two nodes share their ``R``-component. Since
the graph is the full image ``{(fold_H(w), psi_R(w)) : w in Sigma*}``,
functionality says ``fold_H`` factors as ``f . psi_R`` on **every** word, so a
cell's loop orbit ``fold_H(v^j) = f(d_R^j)``, its stabilization power and its
stabilized pair are all cell-determined — and so is the prediction. Every
``R``-class is reached, so the check is the node count: ``n_nodes == n_R``.

The guard is not decoration. The hypothesis's classes are unions of syntactic
classes of ``L`` only for the *table* words (that is what a witnessed split
buys); a loop power ``v^j`` lies far outside the table, where the fold computes
whatever ``step`` composes. Closedness and consistency constrain rows, not
fold-intermediates, so factoring is a conjecture about the tables a learner
reaches, not a theorem — and the saturated leg cannot rescue it without
circularity. Hence: a **returned counterexample is sound unconditionally** (both
verdicts are read on the concrete keyed lasso), while **certification and
minimality are conditional on the guard**. When it fires, `NotFunctional` is
raised, the caller falls back to the closure oracle for that query, and the
graph is a counterexample to the factoring conjecture — a recorded finding, not
a bug.

Under the guard, keys are shortlex-least and cells are scanned in the discipline
order (shortest stem, then shortest loop, then shortlex), so the first
disagreeing cell yields the minimal counterexample over all lassos.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from sosl.sos.alphabet import Alphabet, Letter, Word
from sosl.sos.calculus import Aligned, Cell, PairSet, Table, align, equivalent
from sosl.sos.hypothesis import Hypothesis, loop_reps
from sosl.sos.invariant import Invariant
from sosl.sos.lasso import Lasso
from sosl.teacher.equiv import resolve_prediction

Member = Callable[[Lasso], bool]


class NotFunctional(Exception):
    """The aligned graph is not functional: two nodes share an ``R``-component, so
    the hypothesis's fold does not factor through the reference's classes and a
    cell's keyed lasso no longer speaks for the cell.

    A capability limit on *certification*, never a soundness failure — the caller
    falls back to the closure oracle for that query and records the firing (spec
    §9 row F10). Carries the two colliding nodes and the shortlex words that key
    them: those words are syntactically equivalent (one ``R``-class) yet fold to
    different hypothesis classes — the witness pair a firing exists to exhibit."""

    def __init__(self, n_nodes: int, n_ref: int, collision: Tuple[Cell, Cell],
                 witnesses: Tuple[Word, Word]) -> None:
        super().__init__(
            f"aligned graph not functional: {n_nodes} nodes over {n_ref} reference "
            f"classes; nodes {collision[0]} and {collision[1]} share an R-class"
        )
        self.n_nodes = n_nodes
        self.n_ref = n_ref
        self.collision = collision
        self.witnesses = witnesses

    @property
    def ref_class(self) -> int:
        """The reference class both witnesses fold to."""
        return self.collision[0][1]


def _assert_functional(aligned: Aligned, n_ref: int) -> None:
    """Every reference class is named by exactly one aligned node. Raises
    `NotFunctional` with the first colliding node pair and its witness words
    otherwise."""
    if aligned.n == n_ref:
        return
    seen: Dict[int, int] = {}
    for i, node in enumerate(aligned.nodes):
        j = seen.setdefault(node[1], i)
        if j != i:
            raise NotFunctional(aligned.n, n_ref, (aligned.nodes[j], node),
                                (aligned.keys[j], aligned.keys[i]))
    raise AssertionError(
        f"aligned graph has {aligned.n} distinct R-components but {n_ref} classes"
    )


class HypothesisLanguage:
    """A `sosl.sos.calculus.FoldedLanguage` view of a Cayley hypothesis: its
    classes, its ``step`` right action, and its P-cache read-off on a
    ``(stem class, loop class)`` pair.

    Only the right action generates the aligned node set; the scan reads the
    hypothesis through `predicted_verdict` instead, on the words the nodes are
    keyed by — a bare class pair has lost the loop word the hypothesis must
    iterate to stabilize it, so `verdict` answers the coarser question "what does
    the cache say about this pair's representative lasso". A miss is resolved by
    one membership query, as the hypothesis's own prediction resolves one; the
    answers are memoized."""

    def __init__(self, hypothesis: Hypothesis, member: Member) -> None:
        self.hypothesis = hypothesis
        self._member = member
        self._loops: List[Optional[Word]] = loop_reps(hypothesis)
        self._verdicts: Dict[Tuple[int, int], bool] = {}

    @property
    def alphabet(self) -> Alphabet:
        return self.hypothesis.alphabet

    @property
    def loops(self) -> List[Optional[Word]]:
        """A non-empty word per class, or ``None`` for a class no non-empty word
        reaches (`sosl.sos.hypothesis.loop_reps`)."""
        return self._loops

    @property
    def classes(self) -> Sequence[int]:
        return range(self.hypothesis.n)

    @property
    def identity(self) -> int:
        return self.hypothesis.start

    def step(self, c: int, a: Letter) -> int:
        return self.hypothesis.step[c][a]

    def predicted_verdict(self, lasso: Lasso) -> bool:
        """The hypothesis's normative answer for ``lasso``: the cached bit of the
        pair it stabilizes to, or the teacher's bit for that pair's
        representative lasso."""
        return resolve_prediction(self._member, self.hypothesis, lasso, self._loops)

    def verdict(self, stem: int, loop: int) -> bool:
        """The cache read-off on a class pair (memoized). ``loop`` is the class of
        a non-empty word — the identity is never a loop — so it has a non-empty
        representative."""
        cached = self._verdicts.get((stem, loop))
        if cached is not None:
            return cached
        rep = self._loops[loop]
        assert rep is not None, "loop class has no non-empty representative"
        bit = self.predicted_verdict(Lasso(self.hypothesis.keys[stem], rep))
        self._verdicts[(stem, loop)] = bit
        return bit


def exact_ref_counterexample(
    member: Member,
    alphabet: Alphabet,
    h: Hypothesis,
    ref_table: Table,
    ref_pairs: PairSet,
) -> Tuple[Optional[Lasso], bool]:
    """Decide ``h`` against the language ``ref_pairs`` of ``ref_table`` exactly.

    Returns ``(lasso, True)`` with the minimal counterexample, or ``(None, True)``
    when the hypothesis is exactly correct. ``O(n_H * n_R * |Sigma|)`` alignment
    steps and ``O(n_R^2)`` cell verdicts. Raises `NotFunctional` when the aligned
    graph cannot certify (see the module docstring)."""
    assert h.alphabet.aps == alphabet.aps, "hypothesis/teacher alphabet mismatch"
    assert ref_table.alphabet.aps == alphabet.aps, "reference/teacher alphabet mismatch"
    hyp = HypothesisLanguage(h, member)
    aligned = align(hyp, ref_table.language(ref_pairs))
    _assert_functional(aligned, ref_table.n)
    scan = replace(
        aligned,
        verdict_a=lambda c, d: hyp.predicted_verdict(aligned.cell_lasso((c, d))),
    )
    agree, witness = equivalent(scan)
    if agree:
        return None, True
    assert witness is not None
    return witness.lasso, True


def reference_table(reference: Invariant) -> Tuple[Table, PairSet]:
    """The reference invariant split into the algebra the scan folds through and
    the pair set it reads verdicts from."""
    return Table.of(reference), reference.accept
