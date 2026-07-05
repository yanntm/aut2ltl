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
from typing import Callable, List, Optional, Sequence, Tuple

from sosl.objects.alphabet import Alphabet, Word
from sosl.objects.cayley import Hypothesis, loop_reps
from sosl.objects.lasso import Lasso

Member = Callable[[Lasso], bool]

# Cap on lassos examined in one bounded search. |Sigma|^B grows fast (|Sigma|=4,
# B=8 is billions), so past this many candidates the search stops and reports
# itself incomplete rather than running unbounded — bounded is a first pass, not
# a proof. Chosen to cover |Sigma|=2 up to B=8 (~2.6e5) in full.
DEFAULT_MAX_LASSOS = 500_000


def resolve_prediction(
    member: Member,
    h: Hypothesis,
    lasso: Lasso,
    loops: Sequence[Optional[Word]],
) -> bool:
    """The hypothesis's normative answer for ``lasso``: the cached verdict for
    the reduced pair, or — on a cache miss — the membership of the pair's
    representative lasso ``key(s).loop(e)^omega`` (queried through ``member``),
    where ``loops`` is `sosl.objects.cayley.loop_reps` (a non-empty loop
    representative per class)."""
    pair = h.stabilized_pair(lasso)
    cached = h.accept.get(pair)
    if cached is not None:
        return cached
    s, e = pair
    loop = loops[e]
    assert loop is not None, "loop class has no non-empty representative"
    return member(Lasso(h.keys[s], loop))


def bounded_counterexample(
    member: Member,
    alphabet: Alphabet,
    h: Hypothesis,
    bound: int,
    max_lassos: int = DEFAULT_MAX_LASSOS,
) -> Tuple[Optional[Lasso], bool]:
    """Search lassos (up to ``bound``) for a hypothesis/teacher disagreement.

    Returns ``(lasso, complete)``: the minimal counterexample and ``True`` if the
    search finished, or ``(None, True)`` if none exists within the bound, or
    ``(None, False)`` if the ``max_lassos`` work cap was hit first (the search is
    then inconclusive, not a proof of equivalence)."""
    assert h.alphabet.aps == alphabet.aps, "hypothesis/teacher alphabet mismatch"
    letters = alphabet.letters()
    loops = loop_reps(h)
    seen = 0
    for slen in range(bound + 1):
        for llen in range(1, bound + 1):
            for stem in product(letters, repeat=slen):
                for loop in product(letters, repeat=llen):
                    if seen >= max_lassos:
                        return None, False
                    seen += 1
                    lasso = Lasso(stem, loop)
                    if resolve_prediction(member, h, lasso, loops) != member(lasso):
                        return lasso, True
    return None, True
