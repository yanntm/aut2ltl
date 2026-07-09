"""An operator view of the DG formula arena.

The `dg` arena speaks five primitives — `⊤`, an abstract letter, `¬`, `∨`,
strict next-until `XU` — and builds `∧`, `X`, `U`, `F` out of them by fixed
patterns (`dg.formulas`). A drawing of the formula wants those patterns back:
a node labelled `φ U ψ` with two out-arcs `φ` and `ψ` says what the node *is*,
where the raw `∨(ψ, ¬(¬φ ∨ ¬(φ XU ψ)))` says only how it was spelled.

`head(ast, i)` returns exactly that: the head connective of arena node `i` and
the arena ids filling its slots. It is a *view* — nothing is rewritten, ids
stay arena ids, and two occurrences of a subterm are the same id because the
arena is hash-consed. So node identity is subtree identity in the view too,
and the view's reachable set is a sub-DAG of the arena's.

Derived shapes are recognised in the order the constructors nest them: `U` and
`F` before the `∨` they are spelled with, `∧` before the `¬` it is spelled
with, `X` and strict-`F` before the bare `XU`. Associative chains flatten:
`a ∨ (b ∨ c)` is one wide node — `⋁`, of arity three — which is how the exit
fans of the induction actually read. `∧`/`∨` are flagged associative-commutative
(`Head.ac`): their slots are a multiset, so a drawing owes them no slot names.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from aut2ltl.sos2ltl.dg.formulas import Ast

Slot = Tuple[str, int]      # (the slot's TeX label, the arena id filling it)


@dataclass(frozen=True)
class Head:
    """One arena node, seen as an operator over slots."""

    tex: str                # the node's label, e.g. `\phi \U \psi`
    slots: Tuple[Slot, ...]
    ac: bool = False        # associative-commutative: its slots are unordered

    @property
    def leaf(self) -> bool:
        return not self.slots


_PHI = r"\phi"
_PSI = r"\psi"


def _op(ast: Ast, i: int) -> str:
    return ast.node(i)[0]


def _is_top(ast: Ast, i: int) -> bool:
    return _op(ast, i) == "top"


def _is_bot(ast: Ast, i: int) -> bool:
    return _op(ast, i) == "not" and _is_top(ast, ast.node(i)[1])


def _as_and(ast: Ast, i: int) -> Optional[Tuple[int, int]]:
    """`(p, q)` when `i` is `¬(¬p ∨ ¬q)` — the arena's `∧`."""
    if _op(ast, i) != "not":
        return None
    j = ast.node(i)[1]
    if _op(ast, j) != "or":
        return None
    a, b = ast.node(j)[1], ast.node(j)[2]
    if _op(ast, a) != "not" or _op(ast, b) != "not":
        return None
    return ast.node(a)[1], ast.node(b)[1]


def _as_until(ast: Ast, i: int) -> Optional[Tuple[int, int]]:
    """`(φ, ψ)` when `i` is `ψ ∨ (φ ∧ (φ XU ψ))` — the arena's non-strict `U`."""
    if _op(ast, i) != "or":
        return None
    psi, right = ast.node(i)[1], ast.node(i)[2]
    conj = _as_and(ast, right)
    if conj is None:
        return None
    phi, xu = conj
    if _op(ast, xu) != "xu":
        return None
    if ast.node(xu)[1] != phi or ast.node(xu)[2] != psi:
        return None
    return phi, psi


def _as_eventually(ast: Ast, i: int) -> Optional[int]:
    """`φ` when `i` is `φ ∨ (⊤ XU φ)` — the arena's non-strict `F`."""
    if _op(ast, i) != "or":
        return None
    phi, right = ast.node(i)[1], ast.node(i)[2]
    if _op(ast, right) != "xu":
        return None
    return phi if (_is_top(ast, ast.node(right)[1])
                   and ast.node(right)[2] == phi) else None


Split = Callable[[Ast, int], Optional[Tuple[int, int]]]


def _split_or(ast: Ast, i: int) -> Optional[Tuple[int, int]]:
    if _op(ast, i) != "or":
        return None
    return ast.node(i)[1], ast.node(i)[2]


def _split_and(ast: Ast, i: int) -> Optional[Tuple[int, int]]:
    return _as_and(ast, i)


def _links(ast: Ast, i: int, split: Split) -> bool:
    """True when `i` is one more link of the same associative chain — and not
    a shape the view names in its own right, which must stay a node."""
    if split(ast, i) is None:
        return False
    return _as_until(ast, i) is None and _as_eventually(ast, i) is None


def _chain(ast: Ast, i: int, split: Split) -> List[int]:
    """`i` flattened along an associative operator; `i` itself is known to be
    of that shape."""
    parts = split(ast, i)
    assert parts is not None
    out: List[int] = []
    for p in parts:
        out += _chain(ast, p, split) if _links(ast, p, split) else [p]
    return out


def _wide(tex_bin: str, tex_wide: str, parts: Sequence[int]) -> Head:
    """An `∧`/`∨` node. Associative-commutative: its slots are a multiset, so
    they carry no names — position in an `∧` means nothing."""
    if len(parts) == 2:
        return Head(tex_bin, ((_PHI, parts[0]), (_PSI, parts[1])), ac=True)
    return Head(tex_wide,
                tuple((str(k + 1), p) for k, p in enumerate(parts)), ac=True)


def head(ast: Ast, i: int, letters: Sequence[str]) -> Head:
    """Arena node `i` as an operator over slots. `letters[a]` is the TeX of
    abstract letter `a` — the atoms print verbatim, never as ids."""
    n = ast.node(i)
    op = n[0]

    if op == "top":
        return Head(r"\top", ())
    if op == "atom":
        return Head(letters[n[1]], ())

    if op == "not":
        if _is_top(ast, n[1]):
            return Head(r"\bot", ())
        conj = _as_and(ast, i)
        if conj is not None:
            return _wide(rf"{_PHI} \land {_PSI}", r"\bigwedge",
                         _chain(ast, i, _split_and))
        return Head(rf"\lnot {_PHI}", ((_PHI, n[1]),))

    if op == "or":
        u = _as_until(ast, i)
        if u is not None:
            return Head(rf"{_PHI} \U {_PSI}", ((_PHI, u[0]), (_PSI, u[1])))
        f = _as_eventually(ast, i)
        if f is not None:
            return Head(rf"\F {_PHI}", ((_PHI, f),))
        return _wide(rf"{_PHI} \lor {_PSI}", r"\bigvee",
                     _chain(ast, i, _split_or))

    assert op == "xu", op
    left, right = n[1], n[2]
    if _is_bot(ast, left):
        return Head(rf"\X {_PHI}", ((_PHI, right),))
    if _is_top(ast, left):
        return Head(rf"\X \F {_PHI}", ((_PHI, right),))
    return Head(rf"{_PHI} \mathbin{{\widetilde{{\mathsf{{U}}}}}} {_PSI}",
                ((_PHI, left), (_PSI, right)))


# ------------------------------------------------------------------ #
def reachable(ast: Ast, root: int, letters: Sequence[str]) -> Dict[int, Head]:
    """Every node the view reaches from `root`, keyed by arena id. Smaller
    than the arena: the `∨`/`¬` nodes that spell a `U` or an `∧` are
    consumed by the head that names them."""
    out: Dict[int, Head] = {}
    stack = [root]
    while stack:
        i = stack.pop()
        if i in out:
            continue
        h = head(ast, i, letters)
        out[i] = h
        stack += [c for _s, c in h.slots]
    return out


def depths(view: Dict[int, Head], root: int) -> Dict[int, int]:
    """Each node's *shortest* distance from the root — the level a top-down
    drawing puts it on."""
    d: Dict[int, int] = {root: 0}
    front = [root]
    while front:
        nxt: List[int] = []
        for i in front:
            for _s, c in view[i].slots:
                if c not in d:
                    d[c] = d[i] + 1
                    nxt.append(c)
        front = nxt
    return d


def tree_nodes(view: Dict[int, Head], root: int, cut: int) -> int:
    """How many nodes the same top-down unfolding of levels `0..cut` costs a
    substituting (copy-per-occurrence) reader."""
    memo: Dict[Tuple[int, int], int] = {}

    def go(i: int, d: int) -> int:
        if d == cut:
            return 1
        key = (i, d)
        got = memo.get(key)
        if got is None:
            got = 1 + sum(go(c, d + 1) for _s, c in view[i].slots)
            memo[key] = got
        return got

    return go(root, 0)


__all__ = ["Head", "depths", "head", "reachable", "tree_nodes"]
