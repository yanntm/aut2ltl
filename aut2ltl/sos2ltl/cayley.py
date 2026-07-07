"""`Cay(L)` — the right Cayley machine of the invariant, and its layers.

The deterministic complete automaton with states `𝒞`, initial state `[ε]`,
and transitions `c →^a M(c, λ(a))`: reading a finite word from `[ε]` lands
exactly on its class (the prefix-class walk). Right multiplication never
climbs Green's R-order, so the machine's SCCs are the R-classes of the
algebra, its SCC DAG is the R-order, and every walk eventually stays inside
one final layer. `build` computes the layer structure and *verifies* the
SCC = R-class coincidence on every input, by an independent reachability
computation on the full multiplication table.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Set, Tuple

from sosl.sos import Invariant, Letter


@dataclass(frozen=True)
class Cayley:
    """The layer structure of `Cay(L)`: `layer_of[c]` is the layer (R-class)
    of class `c`; `layers[i]` lists layer `i`'s classes ascending; layer ids
    are a topological order of the R-order DAG (layer 0 = the identity's,
    the unique root), ties broken by smallest member class; `successors[i]`
    lists the layers directly below layer `i` (one letter step out)."""

    inv: Invariant
    layer_of: Tuple[int, ...]
    layers: Tuple[Tuple[int, ...], ...]
    successors: Tuple[Tuple[int, ...], ...]

    def step(self, c: int, a: Letter) -> int:
        """The transition `c →^a M(c, λ(a))`."""
        return self.inv.mult[c][self.inv.letter_class[a]]


def _closure(n: int, succ: List[Set[int]]) -> List[Set[int]]:
    """Forward-reachability sets (node included) of a graph on `0..n-1`."""
    reach: List[Set[int]] = []
    for c in range(n):
        seen: Set[int] = {c}
        stack: List[int] = [c]
        while stack:
            x = stack.pop()
            for y in succ[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        reach.append(seen)
    return reach


def _partition(n: int, reach: List[Set[int]]) -> List[FrozenSet[int]]:
    """Mutual-reachability classes, as a list indexed by node."""
    return [frozenset(d for d in reach[c] if c in reach[d]) for c in range(n)]


def build(inv: Invariant) -> Cayley:
    """The layer structure of `Cay(L)`, with the R-class check.

    The letter graph (`c → c·λ(a)`) and the full right-multiplication graph
    (`c → c·d`, all `d`) must induce the same mutual-reachability partition —
    the SCCs are the R-classes; a mismatch is a malformed invariant."""
    n = inv.n
    letter_classes = sorted(set(inv.letter_class))
    letter_succ: List[Set[int]] = [
        {inv.mult[c][d] for d in letter_classes} for c in range(n)]
    full_succ: List[Set[int]] = [
        {inv.mult[c][d] for d in range(n)} for c in range(n)]

    letter_reach = _closure(n, letter_succ)
    sccs = _partition(n, letter_reach)
    assert sccs == _partition(n, _closure(n, full_succ)), \
        "Cay(L) SCCs differ from the R-classes of M"

    blocks: Dict[FrozenSet[int], List[int]] = {}
    for c in range(n):
        blocks.setdefault(sccs[c], []).append(c)

    # Kahn's topological order over the condensation, smallest member first.
    block_succ: Dict[FrozenSet[int], Set[FrozenSet[int]]] = {
        b: {sccs[y] for x in b for y in letter_succ[x] if sccs[y] != b}
        for b in blocks}
    indeg: Dict[FrozenSet[int], int] = {b: 0 for b in blocks}
    for b, outs in block_succ.items():
        for t in outs:
            indeg[t] += 1
    ready: List[FrozenSet[int]] = sorted(
        (b for b, d in indeg.items() if d == 0), key=min)
    order: List[FrozenSet[int]] = []
    while ready:
        b = ready.pop(0)
        order.append(b)
        for t in sorted(block_succ[b], key=min):
            indeg[t] -= 1
            if indeg[t] == 0:
                ready.append(t)
        ready.sort(key=min)
    assert len(order) == len(blocks), "R-order condensation is not a DAG"
    assert inv.identity in order[0], "the identity's layer must be the root"

    layer_id: Dict[FrozenSet[int], int] = {b: i for i, b in enumerate(order)}
    layer_of: Tuple[int, ...] = tuple(layer_id[sccs[c]] for c in range(n))
    layers: Tuple[Tuple[int, ...], ...] = tuple(
        tuple(sorted(b)) for b in order)
    successors: Tuple[Tuple[int, ...], ...] = tuple(
        tuple(sorted(layer_id[t] for t in block_succ[b])) for b in order)
    return Cayley(inv=inv, layer_of=layer_of, layers=layers,
                  successors=successors)
