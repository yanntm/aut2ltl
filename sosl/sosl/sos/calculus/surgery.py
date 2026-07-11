"""The free fragment of the calculus: operations that keep the table fixed and
only move the pair set.

Everything here is `O(|linked|)` (a set operation or one scan) unless stated,
because `Val` factors through the pair set pointwise:

    Val_P(c, d) = (M(c, idem(d)), idem(d)) in P

so any Boolean combination of pair sets is the same Boolean combination of the
languages. This is the "pay canonicity once" half of the calculus: once an
invariant exists, complement and the Boolean operations cost nothing.

Two operations move outside that pattern. `rooting` shifts the stem by a class,
realizing the left quotient ``key(c)^{-1}.L``; `inverse_substitution` rewrites
the letter map, realizing relabeling / letter merging / alphabet extension, and
is the only one that returns a new table.

The hull section (`live`, `safety_closure`, `interior`, `liveness_part` and the
`is_safety` / `is_cosafety` / `is_obligation` / `obligation_degree` read-offs)
costs one ``O(n^2)`` liveness scan or one ``O(n * |Sigma|)`` SCC pass: the
topological classifications — safety closure, Alpern-Schneider decomposition,
the obligation rung and its Wagner coordinates — as surgeries and read-offs on
the same table.

**The internal law.** Two linked pairs denote the same set of omega-words iff
they are conjugate, so a pair set that is a *language* is closed under
conjugation — `saturate`d. Every operation here maps saturated sets to saturated
sets; the harness asserts it on every output, and a violation convicts the
operation (never `saturate` an output silently to hide it).
"""
from __future__ import annotations

from typing import Callable, Dict, FrozenSet, Iterable, Iterator, List, Optional, Sequence, Set, Tuple

from ..alphabet import Alphabet, Letter
from .table import PairSet, Table

# --- the Boolean fragment --------------------------------------------------


def empty(table: Table) -> PairSet:
    """The empty language over ``table``."""
    return frozenset()


def universal(table: Table) -> PairSet:
    """The language of all omega-words: every linked pair."""
    return table.linked


def complement(table: Table, pairs: PairSet) -> PairSet:
    """``linked \\ pairs``. Correct because ``Val`` reads membership of the same
    looked-up pair, so flipping the set flips the verdict pointwise."""
    return table.linked - pairs


def union(table: Table, left: PairSet, right: PairSet) -> PairSet:
    """``left | right``; ``Val`` distributes over union pointwise."""
    return left | right


def intersection(table: Table, left: PairSet, right: PairSet) -> PairSet:
    """``left & right``; ``Val`` distributes over intersection pointwise."""
    return left & right


def difference(table: Table, left: PairSet, right: PairSet) -> PairSet:
    """``left - right``, i.e. ``left & complement(right)``."""
    return left - right


def xor(table: Table, left: PairSet, right: PairSet) -> PairSet:
    """``left ^ right`` — the symmetric difference, the disagreement language."""
    return left ^ right


# --- rooting (the left quotient) -------------------------------------------


def rooting(table: Table, pairs: PairSet, c: int) -> PairSet:
    """``P_c = {(s, e) in linked : (M(c, s), e) in pairs}``, the pair set of the
    left quotient ``key(c)^{-1}.L(pairs)``.

    Well defined: ``(M(c, s), e)`` is linked whenever ``(s, e)`` is. Correct:
    ``Val_{P_c}(x, d) = Val_P(M(c, x), d)``, which is membership of
    ``key(c).key(x).key(d)^omega``. The action law ``P_{M(c,d)} = (P_c)_d``
    holds, with ``P_identity = pairs``."""
    mult = table.mult
    return frozenset((s, e) for (s, e) in table.linked if (mult[c][s], e) in pairs)


def residual_count(table: Table, pairs: PairSet) -> int:
    """The number of distinct left quotients ``{P_c : c in C}`` — the size of
    the residual (right-congruence) automaton of ``L(pairs)``, read off the
    algebra with no automaton."""
    return len({rooting(table, pairs, c) for c in range(table.n)})


# --- saturation and the legality check --------------------------------------


def linked_pair_of(table: Table, stem: int, loop: int) -> Tuple[int, int]:
    """The linked pair that decides the cell ``(stem, loop)``: absorb one
    idempotent loop into the stem. This is the pair `Table.val` looks up, so a
    cell and its linked pair always carry the same verdict."""
    e = table.idem(loop)
    return (table.mult[stem][e], e)


def saturate(table: Table, pairs: PairSet) -> PairSet:
    """The conjugation closure of ``pairs``: the least superset closed under

        (s, e) in Q,  M(x, y) = e  ==>  linked_pair_of(M(s, x), M(y, x)) in Q

    The rule is the word identity ``u.(xy)^omega = (ux).(yx)^omega``: the cell
    ``(sx, yx)`` denotes the same omega-words as ``(s, e)``, so the two must get
    the same verdict, and a pair set denotes a language iff it equals its
    closure. Conjugacy is symmetric (swap ``x`` and ``y`` to travel back), so
    the closure is a union of conjugacy classes.

    Note ``M(y, x)`` need **not** be idempotent even though ``M(x, y) = e`` is,
    which is why the conjugate cell is normalized through `linked_pair_of`
    rather than inserted as it stands. ``O(|linked| * n^2)`` worst case; run
    rarely (legality checks, harness)."""
    mult = table.mult
    factor = table.factorizations
    out: Set[Tuple[int, int]] = set(pairs)
    work: List[Tuple[int, int]] = list(out)
    while work:
        s, e = work.pop()
        for x, y in factor[e]:
            conjugate = linked_pair_of(table, mult[s][x], mult[y][x])
            if conjugate not in out:
                out.add(conjugate)
                work.append(conjugate)
    return frozenset(out)


def is_saturated(table: Table, pairs: PairSet) -> bool:
    """Is ``pairs`` closed under conjugation — i.e. does it denote a language?"""
    return saturate(table, pairs) == pairs


def conjugacy_classes(table: Table) -> Tuple[PairSet, ...]:
    """The partition of ``table.linked`` into conjugacy classes — the atoms of
    the saturated pair sets: a set denotes a language iff it is a union of
    these, and each class is `saturate` of any one of its members.

    Deterministic: linked pairs are processed in the discipline order of their
    keys (``(len(key(s)), key(s), len(key(e)), key(e))``); each not-yet-covered
    pair contributes ``saturate({pair})``, and the classes are returned in
    discovery order, so the first pair of a class is its least representative.
    ``O(|linked| * n^2)`` worst case; memoized on the table like `linked` is
    (the ``_conjugacy`` slot; the table only hosts it, this function owns it)."""
    if table._conjugacy is not None:
        return table._conjugacy
    keys = table.keys
    order = sorted(
        table.linked,
        key=lambda p: (len(keys[p[0]]), keys[p[0]], len(keys[p[1]]), keys[p[1]]),
    )
    covered: Set[Tuple[int, int]] = set()
    classes: List[PairSet] = []
    for pair in order:
        if pair in covered:
            continue
        cls = saturate(table, frozenset((pair,)))
        classes.append(cls)
        covered |= cls
    table._conjugacy = tuple(classes)
    return table._conjugacy


def pair_language(table: Table, pairs: Iterable[Tuple[int, int]]) -> PairSet:
    """An arbitrary set of linked pairs promoted to a language, after checking
    that it is legal: every pair linked, and the set saturated. Raises
    `AssertionError` otherwise — the entry point for hand-written pair sets."""
    frozen = frozenset(pairs)
    illegal = frozen - table.linked
    assert not illegal, f"not linked pairs: {sorted(illegal)}"
    assert is_saturated(table, frozen), "pair set is not conjugation-closed"
    return frozen


# --- hulls: the safety closure, the interior, the liveness part -------------


def live(table: Table, pairs: PairSet) -> FrozenSet[int]:
    """The classes with a nonempty residual: ``c`` is live iff some right
    multiple ``M(c, x)`` is the stem of a pair in ``pairs`` (the identity is in
    the table, so the row of ``c`` already contains ``c`` itself). One pass over
    the rows of ``M`` against the stem set, ``O(n^2)``."""
    stems = {s for (s, e) in pairs}
    return frozenset(
        c for c in range(table.n) if not stems.isdisjoint(table.mult[c])
    )


def safety_closure(table: Table, pairs: PairSet) -> PairSet:
    """The pair set of ``cl(L(pairs))``, the smallest closed (safety) superset:
    the linked pairs whose stem is `live`. An omega-word is in the closure iff
    every finite prefix of it is live, and that holds exactly on these pairs —
    a closure operator on the saturated pair sets of the table (extensive,
    monotone, idempotent)."""
    alive = live(table, pairs)
    return frozenset(p for p in table.linked if p[0] in alive)


def interior(table: Table, pairs: PairSet) -> PairSet:
    """The pair set of the interior, the largest open (co-safety) subset — the
    dual hull ``int(L) = complement(cl(complement(L)))``: the linked pairs whose
    stem has *every* continuation inside ``L(pairs)``."""
    escaping = live(table, complement(table, pairs))
    return frozenset(p for p in table.linked if p[0] not in escaping)


def liveness_part(table: Table, pairs: PairSet) -> PairSet:
    """The canonical liveness factor of the Alpern-Schneider decomposition:
    ``pairs | complement(safety_closure(pairs))``. Its closure is the universal
    language (every class is live for it), and
    ``pairs == safety_closure(pairs) & liveness_part(pairs)``."""
    return pairs | (table.linked - safety_closure(table, pairs))


def is_safety(table: Table, pairs: PairSet) -> bool:
    """Is ``L(pairs)`` a safety (closed) property? Exact: the fixpoint equation
    ``pairs == safety_closure(pairs)`` on saturated pair sets."""
    return pairs == safety_closure(table, pairs)


def is_cosafety(table: Table, pairs: PairSet) -> bool:
    """Is ``L(pairs)`` a co-safety (open, guarantee) property? Exact: the
    fixpoint equation ``pairs == interior(pairs)``."""
    return pairs == interior(table, pairs)


# --- the obligation rung (Boolean combinations of safety) -------------------


def _right_cayley_sccs(table: Table) -> Tuple[List[int], int]:
    """The strongly connected components of the right-Cayley letter graph
    ``c -> M(c, lambda(a))`` — Green's R-classes, since the table is
    letter-generated. Iterative Tarjan, ``O(n * |Sigma|)``. Returns
    ``(component of each class, component count)``; component ids are in
    reverse topological order (every edge leaves a component toward a
    smaller id or stays inside)."""
    n = table.n
    succs: List[List[int]] = [
        sorted({table.mult[c][x] for x in table.letter_class}) for c in range(n)
    ]
    index: List[int] = [-1] * n
    low: List[int] = [0] * n
    on_stack: List[bool] = [False] * n
    comp: List[int] = [-1] * n
    stack: List[int] = []
    counter = 0
    ncomp = 0
    for root in range(n):
        if index[root] != -1:
            continue
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack[root] = True
        work: List[Tuple[int, Iterator[int]]] = [(root, iter(succs[root]))]
        while work:
            v, it = work[-1]
            descended = False
            for w in it:
                if index[w] == -1:
                    index[w] = low[w] = counter
                    counter += 1
                    stack.append(w)
                    on_stack[w] = True
                    work.append((w, iter(succs[w])))
                    descended = True
                    break
                if on_stack[w]:
                    low[v] = min(low[v], index[w])
            if descended:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[v])
            if low[v] == index[v]:
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    comp[w] = ncomp
                    if w == v:
                        break
                ncomp += 1
    return comp, ncomp


def _stem_verdicts(table: Table, pairs: PairSet) -> Optional[Dict[int, bool]]:
    """The loop-blind verdict ``theta(s)`` per linked stem, or ``None`` if some
    stem carries two loops with different verdicts."""
    theta: Dict[int, bool] = {}
    for s, e in table.linked:
        v = (s, e) in pairs
        if theta.setdefault(s, v) != v:
            return None
    return theta


def is_obligation(table: Table, pairs: PairSet) -> bool:
    """Is ``L(pairs)`` an obligation (Staiger-Wagner) property — a Boolean
    combination of safety properties? Exact read-off: the verdict must depend
    only on the R-class of the stem, i.e. be constant across the loops of each
    linked stem and constant on each strongly connected component of the
    right-Cayley graph. ``O(|linked| + n * |Sigma|)``."""
    theta = _stem_verdicts(table, pairs)
    if theta is None:
        return False
    comp, _ = _right_cayley_sccs(table)
    by_comp: Dict[int, bool] = {}
    for s, v in theta.items():
        if by_comp.setdefault(comp[s], v) != v:
            return False
    return True


def obligation_degree(table: Table, pairs: PairSet) -> Tuple[int, int]:
    """The Wagner superchain coordinates ``(n_plus, n_minus)`` of an obligation
    language: the longest theta-alternating path in the condensed right-Cayley
    DAG starting at a linked stem of verdict 1 (``n_plus``) resp. 0
    (``n_minus``), where path steps descend through right multiplication. A
    lone stem is a path of length 0; a polarity with no starting stem yields
    ``-1`` (the empty/universal convention). Precondition: `is_obligation`
    (asserted). One reverse-topological sweep, ``O(n * |Sigma|)``."""
    assert is_obligation(table, pairs), "obligation_degree needs an obligation"
    theta = _stem_verdicts(table, pairs)
    assert theta is not None
    comp, ncomp = _right_cayley_sccs(table)
    label: List[Optional[bool]] = [None] * ncomp
    for s, v in theta.items():
        label[comp[s]] = v
    dag: List[Set[int]] = [set() for _ in range(ncomp)]
    for c in range(table.n):
        for x in set(table.letter_class):
            d = comp[table.mult[c][x]]
            if d != comp[c]:
                dag[comp[c]].add(d)
    # best[b][w]: the longest alternating path starting at a stem of verdict b
    # reachable from component w (w included); -1 when no such stem exists.
    # Component ids are reverse-topological, so successors are already done.
    best: List[List[int]] = [[-1] * ncomp, [-1] * ncomp]
    alt: List[int] = [-1, -1]
    for w in range(ncomp):
        below = [-1, -1]
        for s in dag[w]:
            below[0] = max(below[0], best[0][s])
            below[1] = max(below[1], best[1][s])
        best[0][w], best[1][w] = below[0], below[1]
        if label[w] is not None:
            b = int(label[w])
            here = 0 if below[1 - b] < 0 else 1 + below[1 - b]
            best[b][w] = max(best[b][w], here)
            alt[b] = max(alt[b], here)
    return alt[1], alt[0]


# --- inverse substitution (the alphabet move) -------------------------------


def inverse_substitution(
    table: Table,
    pairs: PairSet,
    alphabet: Alphabet,
    pi: Callable[[Letter], Letter],
) -> Tuple[Table, PairSet]:
    """Reinterpret ``L(pairs)`` over a new alphabet through ``pi : Sigma' ->
    Sigma``: same classes and same product, letter map ``lambda . pi``. The
    result recognizes ``pi^{-1}(L)`` — a word over ``Sigma'`` is accepted iff its
    letterwise image is.

    Covers relabeling, letter merging (``pi`` non-injective) and alphabet
    extension by duplication (``pi`` non-surjective). The reachable part may
    shrink, so the returned table is restricted to it and the pair set filtered
    to the surviving classes (a dropped class is named by no word and denotes
    nothing). The result is *not* reduced — the letter map may have collapsed
    distinctions — so `reduce` it before any byte-level use."""
    letter_class: Sequence[int] = [table.letter_class[pi(a)] for a in alphabet.letters()]
    new_table, remap = Table.of_raw(alphabet, table.identity, letter_class, table.mult)
    moved = frozenset(
        (remap[s], remap[e]) for (s, e) in pairs if s in remap and e in remap
    )
    return new_table, moved
