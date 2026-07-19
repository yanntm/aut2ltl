"""Exact equivalence against a reference invariant — the SoS-calculus decision.

Decides whether a hypothesis `Invariant` denotes the language of a reference
`Invariant` ``R``, and returns the globally minimal disagreeing lasso when it
does not (shortest stem, then shortest loop, then shortlex — Proposition W of
`sosl.sos.calculus.decide`).

Both sides are genuine invariants, so the whole decision is the calculus's
align-and-scan: `align` puts the two stamps on one node set — the
letter-generated pairs ``(fold_H(w), fold_R(w))``, at most ``n_H * n_R`` of
them, each keyed by its shortlex-least word — and `equivalent` scans its cells
``(stem node, loop node)`` in the counterexample discipline, reading one
algebraic verdict per side per cell: each side's ``Val`` on its own component,
which by the factoring theorem speaks for every lasso of the cell. No further
assumption is needed on either side, and **no membership query is posed**: the
oracle decides from the two algebras alone.
"""
from __future__ import annotations

from typing import Optional, Tuple

from sosl.sos.alphabet import Alphabet
from sosl.sos.calculus import PairSet, Table, align, equivalent
from sosl.sos.invariant import Invariant
from sosl.sos.lasso import Lasso


def exact_ref_counterexample(
    alphabet: Alphabet,
    hypothesis: Invariant,
    ref_table: Table,
    ref_pairs: PairSet,
) -> Optional[Lasso]:
    """Decide ``hypothesis`` against the language ``ref_pairs`` of ``ref_table``
    exactly: the minimal counterexample, or ``None`` when the hypothesis denotes
    the reference language. ``O(n_H * n_R * |Sigma|)`` alignment steps and
    ``O((n_H * n_R)^2)`` cell verdicts, zero membership queries."""
    assert hypothesis.alphabet.aps == alphabet.aps, \
        "hypothesis/teacher alphabet mismatch"
    assert ref_table.alphabet.aps == alphabet.aps, \
        "reference/teacher alphabet mismatch"
    hyp_table = Table.of(hypothesis)
    aligned = align(hyp_table.language(hypothesis.accept),
                    ref_table.language(ref_pairs))
    agree, witness = equivalent(aligned)
    if agree:
        return None
    assert witness is not None
    return witness.lasso


def reference_table(reference: Invariant) -> Tuple[Table, PairSet]:
    """The reference invariant split into the algebra the scan folds through and
    the pair set it reads verdicts from."""
    return Table.of(reference), reference.accept
