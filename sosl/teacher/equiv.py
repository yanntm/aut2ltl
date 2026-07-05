"""Equivalence-query strategies for a white-box teacher.

Currently the ``bounded:B`` strategy: enumerate lassos with ``|stem| <= B`` and
``1 <= |loop| <= B`` in the order ``(len stem, len loop, shortlex stem, shortlex
loop)`` and return the first on which the hypothesis and the teacher disagree.
That order is exactly the counterexample tie-break (shortest stem, then shortest
loop, then shortlex), so the first mismatch found is already minimal — no
separate minimization pass is needed. Complete in the limit as ``B`` grows;
incomplete for a fixed ``B``.

The strategy is written against a bare ``member`` callable (plus the alphabet),
not a concrete teacher, so it composes with any `sosl.contract.Teacher`.
"""
from __future__ import annotations

from itertools import product
from typing import Callable, Optional

from sosl.objects.alphabet import Alphabet
from sosl.objects.cayley import Hypothesis
from sosl.objects.lasso import Lasso

Member = Callable[[Lasso], bool]


def resolve_prediction(member: Member, h: Hypothesis, lasso: Lasso) -> bool:
    """The hypothesis's normative answer for ``lasso``: the cached verdict for
    the reduced pair, or — on a cache miss — the membership of the pair's
    representative lasso ``key(s).key(e)^omega`` (queried through ``member``)."""
    pair = h.stabilized_pair(lasso)
    cached = h.accept.get(pair)
    if cached is not None:
        return cached
    s, e = pair
    key_e = h.keys[e]
    assert key_e, "loop class has empty key (eps-singleton invariant violated)"
    return member(Lasso(h.keys[s], key_e))


def bounded_counterexample(
    member: Member, alphabet: Alphabet, h: Hypothesis, bound: int
) -> Optional[Lasso]:
    """The minimal lasso (up to ``bound``) on which ``h`` and the teacher
    disagree, or ``None`` if they agree on all lassos within the bound."""
    assert h.alphabet.aps == alphabet.aps, "hypothesis/teacher alphabet mismatch"
    letters = alphabet.letters()
    for slen in range(bound + 1):
        for llen in range(1, bound + 1):
            for stem in product(letters, repeat=slen):
                for loop in product(letters, repeat=llen):
                    lasso = Lasso(stem, loop)
                    if resolve_prediction(member, h, lasso) != member(lasso):
                        return lasso
    return None
