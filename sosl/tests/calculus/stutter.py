"""The stutter read-off against an exact semantic check (harness prerequisite of V2).

    python3 -m tests.calculus.stutter PATH.sos

`Table.is_stutter_invariant` is the five-line algebraic read-off of paper
Prop 3.3: ``L(P)`` is stutter-invariant for every ``P`` over the table iff every
letter's class is idempotent, ``M(λ(a), λ(a)) = λ(a)``. On a *canonical*
invariant (the `flat_canon` corpus is exactly these) this algebraic fact
coincides with the language being stutter-invariant, because the table is the
syntactic monoid: a non-idempotent letter is one the syntactic congruence keeps
apart from its own square, so *some* context separates ``a`` from ``aa`` — a
genuine stutter divergence.

This gate exhibits that coincidence exactly. It runs the §8.6 divergence search
— for each non-idempotent letter, the linear shape ``Val(x·λ(a)·y, t)`` vs
``Val(x·λ(aa)·y, t)`` and the ω shape ``Val(x, λ(a)·y)`` vs ``Val(x, λ(aa)·y)``
over class triples/pairs — which finds a witness lasso pair iff the language is
stutter-sensitive. The read-off must agree with the search: sensitive iff a
witness exists. Every witness is two stutter-equivalent lassos, replayed through
`member` to confirm they truly disagree.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional, Tuple

from sosl.sos import load_invariant
from sosl.sos.calculus import Table
from sosl.sos.calculus.decide import member
from sosl.sos.io.serialize import render_word
from sosl.sos.lasso import Lasso

Divergence = Tuple[Lasso, Lasso]
"""Two stutter-equivalent lassos (an ``a`` word and its ``aa`` doubling) whose
membership disagrees — the certificate of stutter-sensitivity."""


def find_divergence(table: Table, pairs) -> Optional[Divergence]:
    """A stutter divergence for ``L(pairs)``, or ``None`` if the language is
    stutter-invariant. Scans, per non-idempotent letter ``a``, the two Arnold
    context shapes of §8.6 over class triples/pairs; the first ``Val`` mismatch
    yields the ``a`` word and its ``aa`` doubling. Complete: only non-idempotent
    letters can matter (an idempotent letter's extra copies leave every fold
    unchanged), and every single-step doubling sits in one of the two shapes."""
    classes = range(table.n)
    for a in table.alphabet.letters():
        la = table.step(table.identity, a)
        laa = table.mult[la][la]
        if laa == la:
            continue
        # linear shape: the doubled letter sits in the stem
        for x in classes:
            xa = table.mult[x][la]
            xaa = table.mult[x][laa]
            for y in classes:
                stem1 = table.mult[xa][y]
                stem2 = table.mult[xaa][y]
                for t in table.loops():
                    if table.val(pairs, stem1, t) != table.val(pairs, stem2, t):
                        stem = table.keys[x] + (a,) + table.keys[y]
                        dbl = table.keys[x] + (a, a) + table.keys[y]
                        loop = table.keys[t]
                        return Lasso(stem, loop), Lasso(dbl, loop)
        # omega shape: the doubled letter sits in the loop
        for x in classes:
            for y in classes:
                loop1 = table.mult[la][y]
                loop2 = table.mult[laa][y]
                if table.val(pairs, x, loop1) != table.val(pairs, x, loop2):
                    stem = table.keys[x]
                    loop = (a,) + table.keys[y]
                    dbl = (a, a) + table.keys[y]
                    return Lasso(stem, loop), Lasso(stem, dbl)
    return None


def main(argv: List[str]) -> int:
    path = Path(argv[1])
    inv = load_invariant(path.read_text())
    table = Table.of(inv)
    pairs = inv.accept

    readoff = table.is_stutter_invariant()
    div = find_divergence(table, pairs)

    assert readoff == (div is None), (
        f"read-off says {'invariant' if readoff else 'sensitive'} but the "
        f"semantic search {'found' if div else 'found no'} divergence"
    )

    verdict = "invariant" if readoff else "sensitive"
    print(f"{path.name}: |C| = {table.n}, stutter-{verdict} (read-off == semantic)")

    if div is not None:
        w, wd = div
        m_w = member(table, pairs, w)
        m_wd = member(table, pairs, wd)
        assert m_w != m_wd, "divergence witness does not actually disagree"
        alph = table.alphabet
        print(f"  witness: {render_word(alph, w.stem)}·({render_word(alph, w.loop)})^ω "
              f"= {1 if m_w else 0}  vs  "
              f"{render_word(alph, wd.stem)}·({render_word(alph, wd.loop)})^ω "
              f"= {1 if m_wd else 0}")

    print("SUCCESS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
