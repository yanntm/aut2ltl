"""The configuration machine M_k(R) and the condition-(C) decider.

Implements the normative algorithms of `research_notes/bls_cascade_experiments.md`
§3 directly (ALG-1 cone build, ALG-2 entry stems, ALG-5 unified closure, ALG-6
decision), reading its objects off a `sosl.sos.Invariant` and a layer `R` (a
frozenset of class ids that is an SCC of the Cayley machine).

Vocabulary, all as class ids of the invariant:
  - a *quotient letter* is a distinct value of `λ` (`inv.letter_class`); the
    within-layer action of quotient letter `d` at class `q` is `inv.mult[q][d]`,
    *defined* iff the result stays in `R`.
  - a *node* is `(q, m)`: a class `q ∈ R` and a buffer `m` (a tuple of quotient
    letters of length `≤ k`); `push(m, d)` appends `d` and keeps the last `k`.
  - a *full-memory* node has `|m| = k`; an *edge* `e = ((q, m), d)` has `|m| = k`
    and `q·d` defined. Full-memory nodes are closed under edges, so ALG-5 walks
    among them; warm-up nodes (`|m| < k`) exist only to thread the entry stem.

The verdict oracle (ALG-3/6): `Val(s, d) = (M(s, π(d)), π(d)) ∈ P`, with `π(d)`
the idempotent power of the loop class `d` (`inv.idempotent_power`) and `P` the
accepting linked pairs (`inv.accept`).
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from sosl.sos import Invariant

# A node is (class, buffer); an edge is (node, quotient-letter).
Node = Tuple[int, Tuple[int, ...]]
Edge = Tuple[Node, int]


def quotient_letters(inv: Invariant) -> Tuple[int, ...]:
    """Σ_λ: the distinct λ-values (letter classes), ascending. Each is the
    within-layer multiplier `d` used as `inv.mult[q][d]`."""
    return tuple(sorted(set(inv.letter_class)))


def concrete_letters(inv: Invariant) -> Dict[int, Tuple[int, ...]]:
    """For each quotient letter `d`, the concrete letter masks folding to it —
    needed only at formula-rendering time (K-E4), carried here for completeness."""
    out: Dict[int, List[int]] = defaultdict(list)
    for a, d in enumerate(inv.letter_class):
        out[d].append(a)
    return {d: tuple(v) for d, v in out.items()}


@dataclass(frozen=True)
class Cone:
    """The `c`-cone of `M_k(R)` (ALG-1 output): every node reachable from
    `(c, ε)`, the full-memory edges among full-memory nodes, and the successor
    maps. `trans` covers all cone steps (warm-up included, for ALG-2); `edges`
    and `edge_succ` are restricted to full-memory edges (for ALG-5)."""

    R: FrozenSet[int]
    c: int
    k: int
    nodes: FrozenSet[Node]
    fm_nodes: Tuple[Node, ...]
    edges: FrozenSet[Edge]
    edge_succ: Dict[Edge, Node]
    trans: Dict[Tuple[Node, int], Node]
    out_edges: Dict[Node, Tuple[Edge, ...]]


def build_cone(inv: Invariant, R: FrozenSet[int], c: int, k: int,
               sigma: Tuple[int, ...]) -> Cone:
    """ALG-1: breadth-first build of the `c`-cone of `M_k(R)`."""
    def push(m: Tuple[int, ...], d: int) -> Tuple[int, ...]:
        return (m + (d,))[-k:] if k > 0 else ()

    start: Node = (c, ())
    nodes: Set[Node] = {start}
    frontier: List[Node] = [start]
    trans: Dict[Tuple[Node, int], Node] = {}
    edges: Set[Edge] = set()
    edge_succ: Dict[Edge, Node] = {}
    while frontier:
        node = frontier.pop()
        q, m = node
        for d in sigma:
            q2 = inv.mult[q][d]
            if q2 not in R:
                continue
            node2: Node = (q2, push(m, d))
            trans[(node, d)] = node2
            if len(m) == k:                       # full-memory edge only
                e: Edge = (node, d)
                edges.add(e)
                edge_succ[e] = node2
            if node2 not in nodes:
                nodes.add(node2)
                frontier.append(node2)

    out_edges: Dict[Node, List[Edge]] = defaultdict(list)
    for e in edges:
        out_edges[e[0]].append(e)
    fm_nodes = tuple(nd for nd in sorted(nodes) if len(nd[1]) == k)
    return Cone(
        R=R, c=c, k=k,
        nodes=frozenset(nodes), fm_nodes=fm_nodes,
        edges=frozenset(edges), edge_succ=edge_succ, trans=trans,
        out_edges={nd: tuple(v) for nd, v in out_edges.items()},
    )


def entry_stems(inv: Invariant, cone: Cone,
                sigma: Tuple[int, ...]) -> Dict[Node, FrozenSet[int]]:
    """ALG-2: `EntrySt(x)` for every reached node — the stem classes obtained by
    folding a cone path from `(c, ε)`, seeded with the entry class `c` itself."""
    reached: Dict[Node, Set[int]] = defaultdict(set)
    start: Node = (cone.c, ())
    reached[start].add(cone.c)
    frontier: List[Tuple[Node, int]] = [(start, cone.c)]
    while frontier:
        node, s = frontier.pop()
        for d in sigma:
            node2 = cone.trans.get((node, d))
            if node2 is None:
                continue
            s2 = inv.mult[s][d]                   # M(s, λ(d)) = mult[s][d]
            if s2 not in reached[node2]:
                reached[node2].add(s2)
                frontier.append((node2, s2))
    return {nd: frozenset(v) for nd, v in reached.items()}


def closure_at(inv: Invariant, cone: Cone, x: Node,
               budget: int) -> Optional[Set[Tuple[FrozenSet[Edge], int]]]:
    """ALG-5: the loop-class closure with a covered-set coordinate, based at the
    full-memory node `x`. States are `(node, d, F)` with `d ∈ 𝒞∪{1}` (the unit
    `1` is `inv.identity`) and `F ⊆ edges`; returns `CL(x) = {(F, d) : state
    (x, d, F) reached, d ≠ 1}` (closed walks at `x`), or `None` on BUDGET."""
    one = inv.identity
    start: Tuple[Node, int, FrozenSet[Edge]] = (x, one, frozenset())
    seen: Set[Tuple[Node, int, FrozenSet[Edge]]] = {start}
    frontier: List[Tuple[Node, int, FrozenSet[Edge]]] = [start]
    cl: Set[Tuple[FrozenSet[Edge], int]] = set()
    while frontier:
        node, d, F = frontier.pop()
        for e in cone.out_edges.get(node, ()):
            a = e[1]
            node2 = cone.edge_succ[e]
            d2 = inv.mult[d][a]                   # M(d, λ(a)); one·a = a
            F2 = F | {e}
            st = (node2, d2, F2)
            if st in seen:
                continue
            if len(seen) >= budget:
                return None
            seen.add(st)
            frontier.append(st)
            if node2 == x and d2 != one:
                cl.add((F2, d2))
    return cl


Closed = Set[Tuple[FrozenSet[Edge], int]]


def first_returns(inv: Invariant, cone: Cone, x: Node,
                  budget: int) -> Optional[Closed]:
    """The first-return loops based at `x`: closed walks that touch `x` only at
    their ends. Every closed walk at `x` is a concatenation of these, so
    saturating them under the composition rule reproduces `CL(x)` (ALG-5's
    saturation route). `None` on BUDGET."""
    one = inv.identity
    start = (x, one, frozenset())
    seen: Set[Tuple[Node, int, FrozenSet[Edge]]] = {start}
    frontier = [start]
    prims: Closed = set()
    while frontier:
        node, d, F = frontier.pop()
        for e in cone.out_edges.get(node, ()):
            node2 = cone.edge_succ[e]
            d2 = inv.mult[d][e[1]]
            F2 = F | {e}
            if node2 == x and d2 != one:
                prims.add((F2, d2))          # first return: collect, do not extend
                continue
            st = (node2, d2, F2)
            if st in seen:
                continue
            if len(seen) >= budget:
                return None
            seen.add(st)
            frontier.append(st)
    return prims


def is_closed(inv: Invariant, cl: Closed) -> Optional[Tuple]:
    """The ALG-5 assertion: `CL(x)` is closed under
    `(F₁,d₁),(F₂,d₂) ↦ (F₁∪F₂, M(d₁,d₂))`. Returns `None` if closed, else a
    witness `(a, b, composite)` whose composite is missing."""
    for F1, d1 in cl:
        for F2, d2 in cl:
            comp = (F1 | F2, inv.mult[d1][d2])
            if comp not in cl:
                return ((F1, d1), (F2, d2), comp)
    return None


def saturate(inv: Invariant, seeds: Closed) -> Closed:
    """Close `seeds` under the composition rule to a fixpoint — the saturation
    alternative to raw exploration (ALG-5 note)."""
    out: Closed = set(seeds)
    frontier = list(seeds)
    while frontier:
        F1, d1 = frontier.pop()
        for F2, d2 in list(out):
            comp = (F1 | F2, inv.mult[d1][d2])
            if comp not in out:
                out.add(comp)
                frontier.append(comp)
    return out


def all_closures(inv: Invariant, R: FrozenSet[int], k: int,
                 budget: int = 10 ** 6) -> Dict[Tuple[int, Node], Closed]:
    """Per-base `CL(x)` over every entry cone — the raw ALG-5 output, keyed by
    `(entry c, base x)`. `None` values mark BUDGET-hit bases."""
    sigma = quotient_letters(inv)
    out: Dict[Tuple[int, Node], Closed] = {}
    for c in sorted(R):
        cone = build_cone(inv, R, c, k, sigma)
        for x in cone.fm_nodes:
            out[(c, x)] = closure_at(inv, cone, x, budget)
    return out


@dataclass
class Decision:
    """ALG-6 output for one layer at one width. `verdicts[F]` is `VerdictSet(F)`;
    `groups[proj]` unions verdicts over F's sharing a window projection (the
    (B)-mode). `c_holds`/`b_holds` are the two verdicts; a hit budget forces
    both to False and lists the offending bases in `budget_bases`."""

    k: int
    verdicts: Dict[FrozenSet[Edge], Set[bool]]
    groups: Dict[FrozenSet[Tuple[int, ...]], Set[bool]]
    n_collected: int
    max_states: int
    budget_bases: List[Tuple[int, Node]]
    closures: Dict[Tuple[int, Node], Closed]  # per-base CL(x), for the K-E7 scan
    entryst: Dict[Node, FrozenSet[int]]        # EntrySt(x) unioned over entries

    @property
    def budget(self) -> bool:
        return bool(self.budget_bases)

    @property
    def c_conflicts(self) -> List[FrozenSet[Edge]]:
        return [F for F, vs in self.verdicts.items() if len(vs) > 1]

    @property
    def c_holds(self) -> Optional[bool]:
        if self.budget:
            return None
        return not self.c_conflicts

    @property
    def b_conflicts(self) -> List[FrozenSet[Tuple[int, ...]]]:
        return [p for p, vs in self.groups.items() if len(vs) > 1]

    @property
    def b_holds(self) -> Optional[bool]:
        if self.budget:
            return None
        return not self.b_conflicts


def window_projection(F: FrozenSet[Edge], k: int) -> FrozenSet[Tuple[int, ...]]:
    """The window projection of an edge set: the buffers of the endpoint nodes
    of its edges (source and, via push, destination) — the class-blind data the
    (B)-mode groups by. At `k = 0` this is always `{()}` (windows carry nothing),
    so (B) coincides with 'one verdict across all collected F'."""
    wins: Set[Tuple[int, ...]] = set()
    for (q, m), d in F:
        wins.add(m)
        wins.add((m + (d,))[-k:] if k > 0 else ())
    return frozenset(wins)


def edge_set_strongly_connected(F: FrozenSet[Edge], cone: Cone) -> bool:
    """Assertion helper: the nodes touched by `F`, with `F`'s edges, form one
    strongly connected component."""
    if not F:
        return True
    adj: Dict[Node, Set[Node]] = defaultdict(set)
    nodes: Set[Node] = set()
    for e in F:
        src = e[0]
        dst = cone.edge_succ[e]
        adj[src].add(dst)
        nodes.add(src)
        nodes.add(dst)

    def reach(start: Node, graph: Dict[Node, Set[Node]]) -> Set[Node]:
        seen = {start}
        stack = [start]
        while stack:
            u = stack.pop()
            for w in graph.get(u, ()):
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        return seen

    radj: Dict[Node, Set[Node]] = defaultdict(set)
    for u, ws in adj.items():
        for w in ws:
            radj[w].add(u)
    root = next(iter(nodes))
    return reach(root, adj) >= nodes and reach(root, radj) >= nodes


def decide(inv: Invariant, R: FrozenSet[int], k: int,
           budget: int = 10 ** 6, assert_sc: bool = True) -> Decision:
    """ALG-6: build cones from every entry `c ∈ R`, run ALG-5 per full-memory
    base, and aggregate `VerdictSet(F)` and its window-projection grouping."""
    sigma = quotient_letters(inv)
    verdicts: Dict[FrozenSet[Edge], Set[bool]] = defaultdict(set)
    proj_of: Dict[FrozenSet[Edge], FrozenSet[Tuple[int, ...]]] = {}
    budget_bases: List[Tuple[int, Node]] = []
    closures: Dict[Tuple[int, Node], Closed] = {}
    entryst: Dict[Node, Set[int]] = defaultdict(set)
    max_states = 0
    for c in sorted(R):
        cone = build_cone(inv, R, c, k, sigma)
        est = entry_stems(inv, cone, sigma)
        for x in cone.fm_nodes:
            cl = closure_at(inv, cone, x, budget)
            if cl is None:
                budget_bases.append((c, x))
                continue
            closures[(c, x)] = cl
            max_states = max(max_states, len(cl))
            entry_st = est.get(x, frozenset())
            entryst[x] |= entry_st
            for F, d in cl:
                if assert_sc:
                    assert edge_set_strongly_connected(F, cone), (c, x, F)
                e_id = inv.idempotent_power(d)
                for s in entry_st:
                    val = (inv.mult[s][e_id], e_id) in inv.accept
                    verdicts[F].add(val)
                if F not in proj_of:
                    proj_of[F] = window_projection(F, k)

    groups: Dict[FrozenSet[Tuple[int, ...]], Set[bool]] = defaultdict(set)
    for F, vs in verdicts.items():
        groups[proj_of[F]] |= vs
    return Decision(
        k=k, verdicts=dict(verdicts), groups=dict(groups),
        n_collected=len(verdicts), max_states=max_states,
        budget_bases=budget_bases, closures=closures,
        entryst={x: frozenset(s) for x, s in entryst.items()},
    )
