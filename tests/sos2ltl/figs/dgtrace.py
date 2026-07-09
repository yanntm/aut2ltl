"""Recursion-shape instrumentation for the DG induction (figure support).

`synthesize` reports only the three totals — recursion nodes, arena size,
flat tree size. A drawing of the recursion needs its *shape*: which node
calls which, how often, and how the memoized DAG unfolds level by level.

`TracingSynth` subclasses the synthesis driver and records, without
altering it, the call graph over recursion nodes: `node()` is the sole
recursion entry, so overriding it observes every edge. A node is the
memo key `(images, mult, unit, target)` of `dg.synth`; an edge is one
*call*, so a parent that calls the same child twice contributes two edges
— exactly the duplication a substituting (non-memoized) recursion would
pay for.

`levels()` then unfolds that DAG into the recursion *tree* by depth: the
count at depth `d` is the number of tree nodes a copy-substituting
recursion would build at that depth. The unfolding terminates because the
call graph is acyclic (the local-divisor induction strictly decreases).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from aut2ltl.sos2ltl.dg.formulas import Ast
from aut2ltl.sos2ltl.dg.frame import Frame, Target, root_frame, root_target
from aut2ltl.sos2ltl.dg.synth import Synth
from sosl.sos import Invariant


@dataclass(frozen=True)
class NodeInfo:
    """What a drawing needs to name one recursion node."""

    idx: int
    n_letters: int          # |Σ| of the node's frame
    n_monoid: int           # |M| of the node's frame
    target: str             # the ≈-class presentation, short form
    leaf: bool              # base case: every letter invisible


def _target_str(frame: Frame, target: Target) -> str:
    parts: List[str] = []
    if target.eps:
        parts.append("ε")
    if target.fin:
        parts.append("{" + ",".join(str(e) for e in sorted(target.fin)) + "}")
    if target.om:
        parts.append("ω" + ",".join(str(e) for e in sorted(target.om)))
    return "·".join(parts) if parts else "∅"


class TracingSynth(Synth):
    """`Synth` that records the recursion call graph as a side effect.

    Node ids are assigned in call (pre-)order; `edges` is a multiset of
    `(parent, child)` call sites. The recorded formulas are the driver's
    own — nothing here changes what is synthesized.
    """

    def __init__(self, ast: Ast, max_nodes: int = 2000,
                 max_arena: int = 200000) -> None:
        super().__init__(ast, max_nodes=max_nodes, max_arena=max_arena)
        self.index: Dict[object, int] = {}
        self.info: List[NodeInfo] = []
        self.edges: List[Tuple[int, int]] = []
        self._cur: Optional[int] = None

    def node(self, frame: Frame, target: Target) -> int:
        key = (frame.images, frame.mult, frame.unit, target)
        idx = self.index.get(key)
        if idx is None:
            idx = len(self.info)
            self.index[key] = idx
            visible = [li for li, im in enumerate(frame.images)
                       if im != frame.unit]
            self.info.append(NodeInfo(
                idx=idx,
                n_letters=frame.n_letters(),
                n_monoid=len(frame.mult),
                target=_target_str(frame, target),
                leaf=not visible))
        if self._cur is not None:
            self.edges.append((self._cur, idx))
        prev, self._cur = self._cur, idx
        try:
            return super().node(frame, target)
        finally:
            self._cur = prev

    # -------------------------------------------------------------- #
    def children(self, parent: int) -> List[int]:
        """The children of one node, in call order, with duplicates."""
        return [c for p, c in self.edges if p == parent]

    def levels(self) -> List[int]:
        """Tree-node counts by depth, root at depth 0 — the size of each
        level of the substituting (copy-per-occurrence) unfolding."""
        out: List[int] = []
        cur: Dict[int, int] = {0: 1}
        while cur:
            out.append(sum(cur.values()))
            nxt: Dict[int, int] = {}
            for p, mult in cur.items():
                for c in self.children(p):
                    nxt[c] = nxt.get(c, 0) + mult
            cur = nxt
        return out


def trace(inv: Invariant, max_nodes: int = 2000,
          max_arena: int = 200000) -> Tuple[TracingSynth, Ast, int]:
    """Synthesize `inv`'s formula, returning the tracer, the arena, and the
    root formula id (unwound, as `synthesize` returns it)."""
    frame: Frame = root_frame(inv)
    ast = Ast()
    sy = TracingSynth(ast, max_nodes=max_nodes, max_arena=max_arena)
    phi: int = sy.node(frame, root_target(inv, frame))
    return sy, ast, ast.pe(phi, None)


__all__ = ["NodeInfo", "TracingSynth", "trace"]
