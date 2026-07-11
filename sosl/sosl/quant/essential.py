"""The essential form: the canonical representative of a language up to null
sets, and its LTL-up-to-null verdict (paper Thm 4.4, Prop 4.5).

The value vector ``x`` (per-class measure, `measure.value_vector`) induces
the congruence ``c ~ c'  iff  x(w.c.z) == x(w.c'.z) for all classes w, z
including the identity``, computed by grouping classes on their full context
signature — ``O(n^3)`` table lookups, exact `Fraction` comparisons. The
identity is held out of the quotient and re-adjoined fresh (the calculus
canonicity convention; the abstract congruence may merge the identity with a
neutral word class — the held-out quotient is finer by exactly that split
and presents the same language, see `algorithm.md` §9).

On the quotient, ``x`` descends and must be constant 0 or 1 on every bottom
SCC (Thm 4.4(2)) — a violation raises. The essential invariant is the
shadow read-off of the value-1 bottom region, reduced; by Prop 4.5 it does
not depend on ``p`` (the gate asserts byte-equality across ``p``'s).
``ltl_up_to_null`` is aperiodicity of the quotient monoid.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Dict, FrozenSet, List, Optional, Tuple

from ..sos.alphabet import Letter
from ..sos.invariant import Invariant
from ..sos.calculus import Table, reduce
from ..sos.classify.aperiodic import is_aperiodic
from .chain import bottom_sccs
from .measure import value_vector


def _signatures(
    inv: Invariant, p: Optional[Dict[Letter, Fraction]]
) -> List[Tuple[Fraction, ...]]:
    """Per class ``c``, the full context signature
    ``(x(M(w, M(c, z))))_{w, z}`` with ``w, z`` ranging over all classes
    including the identity. Signature equality is the paper's congruence."""
    x = value_vector(inv, p)
    mult = inv.mult
    n = inv.n
    return [
        tuple(x[mult[w][row[z]]] for w in range(n) for z in range(n))
        for row in (mult[c] for c in range(n))
    ]


def congruence_classes(
    inv: Invariant, p: Optional[Dict[Letter, Fraction]] = None
) -> Tuple[FrozenSet[int], ...]:
    """The congruence's blocks on *all* classes, identity included — the
    paper's abstract quotient, as a read-off (the built quotient below
    always holds the identity out). Blocks are ordered by least member."""
    sigs = _signatures(inv, p)
    blocks: Dict[Tuple[Fraction, ...], List[int]] = {}
    for c in range(inv.n):
        blocks.setdefault(sigs[c], []).append(c)
    return tuple(
        frozenset(members)
        for members in sorted(blocks.values(), key=lambda ms: ms[0])
    )


def _quotient(
    inv: Invariant, p: Optional[Dict[Letter, Fraction]]
) -> Tuple[Table, Tuple[Fraction, ...]]:
    """The held-out-identity quotient of ``inv`` by the value congruence:
    the quotient `Table` (canonically re-keyed) and the descended value
    vector, indexed by the table's class ids. The congruence property and
    the descent of ``x`` are asserted, not assumed."""
    x = value_vector(inv, p)
    sigs = _signatures(inv, p)
    word_classes = [c for c in range(inv.n) if c != inv.identity]

    block: Dict[int, int] = {}
    reps: List[int] = []
    seen: Dict[Tuple[Fraction, ...], int] = {}
    for c in word_classes:
        b = seen.setdefault(sigs[c], len(seen))
        block[c] = b
        if b == len(reps):
            reps.append(c)
        assert x[c] == x[reps[b]], "x does not descend to the quotient"

    # Class 0 is the fresh identity; block b becomes class b + 1.
    def cls(c: int) -> int:
        return 0 if c == inv.identity else block[c] + 1

    count = len(reps)
    mult: List[List[int]] = [[0] * (count + 1) for _ in range(count + 1)]
    for i in range(count + 1):
        mult[0][i] = i
        mult[i][0] = i
    for b, c in enumerate(reps):
        for b2, c2 in enumerate(reps):
            mult[b + 1][b2 + 1] = cls(inv.mult[c][c2])
    for c in word_classes:
        for d in word_classes:
            assert cls(inv.mult[c][d]) == mult[cls(c)][cls(d)], (
                f"value congruence is not a congruence at ({c}, {d})"
            )

    letter_class = [cls(inv.letter_class[a]) for a in inv.alphabet.letters()]
    table, remap = Table.of_raw(inv.alphabet, 0, letter_class, mult)
    xbar: List[Fraction] = [Fraction(0)] * table.n
    xbar[remap[0]] = x[inv.identity]
    for b, c in enumerate(reps):
        xbar[remap[b + 1]] = x[c]
    return table, tuple(xbar)


def essential(
    inv: Invariant, p: Optional[Dict[Letter, Fraction]] = None
) -> Invariant:
    """The reduced essential invariant of ``inv``'s language: the value-1
    bottom region of the value-congruence quotient, read off as a shadow
    (default uniform ``p``; by Prop 4.5 the choice cannot matter). Raises
    if the descended vector is not constant 0 or 1 on some bottom SCC of
    the quotient — a violation of Thm 4.4(2), never silently repaired."""
    table, xbar = _quotient(inv, p)
    region: List[int] = []
    for scc in bottom_sccs(table.invariant(frozenset())):
        values = {xbar[c] for c in scc}
        assert len(values) == 1 and next(iter(values)) in (0, 1), (
            f"Thm 4.4(2) violated: quotient bottom SCC {sorted(scc)} "
            f"carries values {sorted(values)}"
        )
        if next(iter(values)) == 1:
            region.extend(scc)
    dbar = frozenset(region)
    pairs = frozenset((s, e) for (s, e) in table.linked if s in dbar)
    return reduce(table, pairs)


def ltl_up_to_null(
    inv: Invariant, p: Optional[Dict[Letter, Fraction]] = None
) -> bool:
    """Whether ``inv``'s language agrees with an LTL-definable language up
    to a null set: aperiodicity of the value-congruence quotient monoid
    (Thm 4.4's characterization)."""
    table, _ = _quotient(inv, p)
    return is_aperiodic(table.invariant(frozenset()))
