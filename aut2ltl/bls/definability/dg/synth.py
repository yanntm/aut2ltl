"""The induction driver — from the canonical algebra to a defining formula
(`algorithm.md` layers 2–5, 7, 14).

A recursion node is `(frame, target)`; the synthesized formula is a function
of exactly that pair. The prepend letter of the [DG] contract anchors
*evaluation* but never enters the assembly — every shape reads position 0's
real letter or looks strictly later — so it is not part of the memo key, and
the root unwinding may partially evaluate against a fresh letter matching no
atom.

Per node: if every letter is invisible (image = unit), the base case — a
disjunction over the at most three `≈`-classes the node can still see
(`{ε}`, `Δ⁺`, `Δ^ω`). Otherwise the least visible letter is the pivot (the
v0 rule of layer 8), `compress` materializes the tables, and the node formula
is assembled over the *compressed* alphabet — the `K₀`/`K₁`/`K₂` pieces with
their guards, saturation subformulas from the monoid induction on the child
frame — then transported to the node's own alphabet by one `tilde`, whose
substitution maps each compressed atom to its decorated block formula from
the alphabet induction (lift to the pivot, `XF c` for `T₁`-letters, `¬XF c`
for `T₂`-letters). Empty pieces (`X_{n,m} = ∅`, an empty `K` set) are
skipped — a deterministic choice, so canonicity is preserved.

All enumerations follow the canonical orders their tables carry; the arena
is shared across the whole synthesis, so the DAG identity of layer 8 is the
identity of arena ids. Caps (recursion nodes, arena size) exit by raising
`DgDecline` — a decline, never a wrong formula.
"""
from __future__ import annotations

from typing import Dict, FrozenSet, List, Sequence, Tuple

from aut2ltl.bls.definability.dg.compress import NodeData, compress
from aut2ltl.bls.definability.dg.formulas import Ast
from aut2ltl.bls.definability.dg.frame import Frame, Target, root_frame, root_target
from aut2ltl.bls.definability.dg.morphism import Alg


class DgDecline(Exception):
    """A resource cap was hit; the synthesis declines (no formula)."""


NodeKey = Tuple[Tuple[int, ...], Tuple[Tuple[int, ...], ...], int, Target]


class Synth:
    """The memoized induction. Owns sequencing, the pivot rule, the piece
    assembly and the caps — no table computation and no clause logic."""

    def __init__(self, ast: Ast, max_nodes: int = 2000,
                 max_arena: int = 200000) -> None:
        self.ast = ast
        self.max_nodes = max_nodes
        self.max_arena = max_arena
        self.n_nodes = 0
        self._memo: Dict[NodeKey, int] = {}

    def node(self, frame: Frame, target: Target) -> int:
        """The formula of one recursion node, over the node's own letters."""
        key: NodeKey = (frame.images, frame.mult, frame.unit, target)
        got = self._memo.get(key)
        if got is not None:
            return got
        self.n_nodes += 1
        if self.n_nodes > self.max_nodes:
            raise DgDecline(f"recursion node cap {self.max_nodes} hit")
        if len(self.ast) > self.max_arena:
            raise DgDecline(f"arena cap {self.max_arena} hit")
        visible: List[int] = [li for li, im in enumerate(frame.images)
                              if im != frame.unit]
        r: int = (self._base(frame, target) if not visible
                  else self._pivot(compress(frame, target, visible[0])))
        self._memo[key] = r
        return r

    def _base(self, frame: Frame, target: Target) -> int:
        """Every letter invisible: `N` is a union of `{ε}`, `Δ⁺`, `Δ^ω` —
        fibers over unreachable elements denote no word and are dropped."""
        a = self.ast
        end: int = a.neg(a.x(a.top()))
        parts: List[int] = []
        if target.eps:
            parts.append(end)
        if frame.unit in target.fin and frame.unit in frame.rep:
            parts.append(a.xf(end))
        if target.om:
            parts.append(a.neg(a.f_(end)))
        return _or_all(a, parts)

    def _pivot(self, nd: NodeData) -> int:
        """One visible-pivot node: assemble `K₀ ∪ K₁ ∪ K₂` over the
        compressed alphabet, then transport by tilde."""
        a = self.ast
        n1: int = len(nd.t1)
        end: int = a.neg(a.x(a.top()))
        or_t1: int = _or_all(a, [a.atom(i) for i in range(n1)])
        pieces: List[int] = []

        for j, tl in enumerate(nd.t2):                                # K₀
            here = (nd.k0_eps if tl[0] == "eps"
                    else tl[1] in nd.k0_fib if tl[0] == "fib"
                    else tl[1] in nd.k0_om)
            if here:
                pieces.append(a.and_(a.atom(n1 + j), end))

        for i in range(n1):                                           # K₁
            for j in range(len(nd.t2)):
                if nd.x[i][j]:
                    sat: int = self.node(
                        nd.fc, Target(False, frozenset(nd.x[i][j]), frozenset()))
                    guard: int = a.xu(or_t1, a.and_(a.atom(n1 + j), end))
                    pieces.append(_and_all(a, [a.atom(i), guard, sat]))

        inf: int = a.neg(a.f_(end))
        all_t1: int = a.neg(a.xf(a.neg(or_t1)))
        for i in range(n1):                                           # K₂
            if nd.k2[i]:
                sat = self.node(nd.fc, Target(False, frozenset(), nd.k2[i]))
                pieces.append(_and_all(a, [a.atom(i), all_t1, inf, sat]))

        xi: int = _or_all(a, pieces)

        sub_cache: Dict[int, int] = {}

        def sub(atom: int) -> int:
            """The decorated block formula of one compressed atom."""
            got = sub_cache.get(atom)
            if got is None:
                if atom < n1:
                    n: int = nd.t1[atom]
                    tgt = Target(n == nd.frame.unit,
                                 frozenset({n}) if n in nd.fa.gen
                                 else frozenset(), frozenset())
                    dec: int = a.xf(a.atom(nd.c))
                else:
                    tl = nd.t2[atom - n1]
                    tgt = (Target(True, frozenset(), frozenset())
                           if tl[0] == "eps"
                           else Target(False, frozenset({tl[1]}), frozenset())
                           if tl[0] == "fib"
                           else Target(False, frozenset(), frozenset({tl[1]})))
                    dec = a.neg(a.xf(a.atom(nd.c)))
                body: int = self.node(nd.fa, tgt)
                host: int = a.map_atoms(body, lambda k: nd.A[k])
                got = a.and_(a.lift(host, nd.c), dec)
                sub_cache[atom] = got
            return got

        return a.tilde(xi, nd.c, sub)


def synthesize(alg: Alg, max_nodes: int = 2000,
               max_arena: int = 200000) -> Tuple[Ast, int, int]:
    """The root call and the unwinding: a formula for the algebra's language,
    pure-future over `Σ^ω`. The algebra must be aperiodic (caller-checked;
    a group fires the divisor's strict-decrease assert at the latest).
    Returns `(arena, formula id, recursion node count)`."""
    frame: Frame = root_frame(alg)
    target: Target = root_target(alg, frame)
    ast = Ast()
    sy = Synth(ast, max_nodes=max_nodes, max_arena=max_arena)
    phi: int = sy.node(frame, target)
    return ast, ast.pe(phi, None), sy.n_nodes


def _or_all(a: Ast, ids: Sequence[int]) -> int:
    r: int = a.bot() if not ids else ids[0]
    for i in ids[1:]:
        r = a.or_(r, i)
    return r


def _and_all(a: Ast, ids: Sequence[int]) -> int:
    r: int = a.top() if not ids else ids[0]
    for i in ids[1:]:
        r = a.and_(r, i)
    return r


__all__ = ["DgDecline", "Synth", "synthesize"]
