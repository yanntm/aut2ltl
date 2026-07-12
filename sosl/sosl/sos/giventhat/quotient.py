"""The bounded quotient engine: the exact primitive the simplifier searches with.

A `Quotient` is a monoid congruence of the interval's product table `T`,
presented as the quotient table `T/pi` (canonically keyed) together with the
class map `pi: T -> T/pi`. Two ways to obtain one: `congruence(T, seeds)` — the
least congruence identifying every seed pair, closed by a letter worklist —
and `syntactic_congruence(T, q)` — the coarsest congruence recognizing the
language `L(q)` (paper Prop 4.1). Both funnel through `_from_blocks`, which
builds the quotient table with **`Table.of_raw`** (the shared shortlex BFS —
there is no second BFS here, trap #13).

The one theorem the engine runs (paper Prop 4.2): for any congruence `pi`,

    hull(pi, Q) := pullback(pi, saturate_{T/pi}(forced(pi, Q)))

is the least `pi`-recognizable superset of `Q`, so the interval contains a `B`
recognized by `T/pi` **iff** `hull(pi, P_min) <= P_max` (`admits`), and
`hull(pi, P_min)` is then the least such member. `forced` renormalizes every
image pair through the **quotient's** idempotent (trap #3); `hull` saturates on
the **quotient** and only then pulls back (trap #15).

See `algorithm.md` for the ideas; the layering law (README) forbids importing
anything outside `sosl.sos` / `sosl.sos.calculus`.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from ..calculus import Table, saturate, syntactic_blocks
from ..calculus.surgery import complement, linked_pair_of
from ..calculus.table import PairSet
from .interval import Interval


@dataclass(frozen=True)
class Quotient:
    """A monoid congruence of `source`, as the canonically keyed quotient table
    `T/pi` plus the class map `pi[c]` (source class id -> quotient class id).
    Frozen; `pi` is a surjective morphism with the identity block a singleton
    (both asserted at construction)."""

    table: Table
    pi: Tuple[int, ...]
    source: Table

    @property
    def n(self) -> int:
        """`|C(T/pi)|` — the number of quotient classes; the greedy's score."""
        return self.table.n


def _from_blocks(source: Table, block_of: List[int]) -> Quotient:
    """Assemble the `Quotient` of `source` under the partition `block_of`
    (source class -> arbitrary block label). Densifies the labels, induces the
    quotient product from block representatives, and re-keys through
    `Table.of_raw`. Asserts the identity's block is a singleton (trap #8)."""
    dense: Dict[int, int] = {}
    ids = [dense.setdefault(block_of[c], len(dense)) for c in range(source.n)]
    k = len(dense)

    rep: List[Optional[int]] = [None] * k
    for c in range(source.n):
        if rep[ids[c]] is None:
            rep[ids[c]] = c

    identity = ids[source.identity]
    letter_class = [ids[source.letter_class[a]] for a in source.alphabet.letters()]
    mult = [[ids[source.mult[rep[b1]][rep[b2]]] for b2 in range(k)]  # type: ignore[index]
            for b1 in range(k)]

    table, remap = Table.of_raw(source.alphabet, identity, letter_class, mult)
    pi = tuple(remap[ids[c]] for c in range(source.n))

    singleton = [c for c in range(source.n) if pi[c] == table.identity]
    assert singleton == [source.identity], (
        f"identity block is not a singleton: {singleton} (trap #8)")
    return Quotient(table=table, pi=pi, source=source)


def congruence(table: Table, seeds: Iterable[Tuple[int, int]]) -> Quotient:
    """The least monoid congruence of `table` identifying every seed pair.

    Union-find over `table.n` classes; a worklist of merged pairs enqueues, on
    each merge `x ~ y`, the letter consequences `M(g,x) ~ M(g,y)` and
    `M(x,g) ~ M(y,g)` for every letter class `g`. Letters suffice: every class
    is a product of letters, so single-letter two-sided stability propagates by
    induction (the argument `reduce`'s refinement already runs). `[eps]` never
    merges — the seeds are non-identity and no product of non-identity classes
    returns to it (asserted in `_from_blocks`). `O(n |Sigma| alpha(n))` per
    batch."""
    parent = list(range(table.n))

    def find(x: int) -> int:
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            parent[x], x = root, parent[x]
        return root

    mult = table.mult
    letters = sorted(set(table.letter_class))
    work: "deque[Tuple[int, int]]" = deque()

    def merge(x: int, y: int) -> None:
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[max(rx, ry)] = min(rx, ry)
            work.append((x, y))

    for x, y in seeds:
        merge(x, y)
    while work:
        x, y = work.popleft()
        for g in letters:
            merge(mult[g][x], mult[g][y])
            merge(mult[x][g], mult[y][g])

    return _from_blocks(table, [find(c) for c in range(table.n)])


def syntactic_congruence(table: Table, pairs: PairSet) -> Quotient:
    """The coarsest congruence of `table` recognizing `L(pairs)` — paper
    Prop 4.1's `pi_L`, lifted from `reduce.syntactic_blocks` into a `Quotient`.
    (Kept here rather than in `calculus`: a `Quotient` is a `giventhat` object,
    and the layering law flows one way — `giventhat` imports `calculus`, never
    the reverse.)"""
    block = syntactic_blocks(table, pairs)
    # syntactic_blocks holds the identity out; give it its own fresh block.
    label = [block.get(c, -1) if c != table.identity else -2
             for c in range(table.n)]
    return _from_blocks(table, label)


def compose(outer: Quotient, inner: Quotient) -> Quotient:
    """`inner` after `outer`: the congruence `inner.pi . outer.pi` of
    `outer.source`. `inner` must be a congruence of `outer.table` (its source).
    This is how the greedy merges *in the current quotient* and keeps a map back
    to `T`, never re-closing from `T` (trap #9)."""
    assert inner.source is outer.table, "compose: inner is not a quotient of outer"
    pi = tuple(inner.pi[outer.pi[c]] for c in range(outer.source.n))
    return Quotient(table=inner.table, pi=pi, source=outer.source)


# --- the hull, the test, the members ---------------------------------------


def forced(quot: Quotient, q: PairSet) -> PairSet:
    """The image of the language `q` (linked pairs on `quot.source`) under `pi`,
    each image pair renormalized through the **quotient's** idempotent via
    `linked_pair_of` (trap #3). Every result pair is linked in `quot.table`."""
    pi = quot.pi
    return frozenset(
        linked_pair_of(quot.table, pi[s], pi[e]) for (s, e) in q)


def pullback(quot: Quotient, pairs_q: PairSet) -> PairSet:
    """The `pi`-preimage of a quotient language, as a language on `quot.source`:
    the linked pairs of the source whose `pi`-image lies in `pairs_q`."""
    pi = quot.pi
    qtab = quot.table
    return frozenset(
        (s, e) for (s, e) in quot.source.linked if qtab.val(pairs_q, pi[s], pi[e]))


def hull(quot: Quotient, q: PairSet) -> PairSet:
    """The least `pi`-recognizable superset of `q` (paper Prop 4.2): saturate
    the forced image **on the quotient**, then pull back. Extensive, monotone,
    idempotent; output saturated and `is_recognized`."""
    return pullback(quot, saturate(quot.table, forced(quot, q)))


def admits(quot: Quotient, iv: Interval) -> bool:
    """Does the interval contain a `B` recognized by `T/pi`? Paper Prop 4.2:
    `hull(pi, P_min) <= P_max`."""
    return hull(quot, iv.p_min) <= iv.p_max


def least_member(quot: Quotient, iv: Interval) -> PairSet:
    """The least member of the interval recognized by `T/pi` (defined when
    `admits`): `hull(pi, P_min)`."""
    return hull(quot, iv.p_min)


def greatest_member(quot: Quotient, iv: Interval) -> PairSet:
    """The greatest member of the interval recognized by `T/pi` (defined when
    `admits`): the dual hull `complement(hull(pi, complement(P_max)))`."""
    return complement(iv.table, hull(quot, complement(iv.table, iv.p_max)))


def is_recognized(quot: Quotient, pairs: PairSet) -> bool:
    """Is `L(pairs)` recognized by `T/pi` — invariant under `pullback . forced`?
    Gate-side; `O(|linked|)`."""
    return pullback(quot, forced(quot, pairs)) == pairs
