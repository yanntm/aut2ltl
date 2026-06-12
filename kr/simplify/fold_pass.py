"""
fold_pass.py — Rule 4: unroll-inverse folding (the expansion laws, backwards).

The kr/ construction emits temporal obligations in locally-unrolled form
(last-step decomposition, first-occurrence splits): `a | F(!a & Xa)` instead
of `Fa`, `a & G(!a | Xa)` instead of `Ga`, `g | (f & X(f U g))` instead of
`f U g`. Spot's tl_simplifier never folds these back (measured on the
F(a&Xa) dump, kr/testing/logs/faxa_dag_dump.txt). Folding them is the
canonical orientation: every rule below strictly shrinks the tree AND
removes a distinct temporal subformula — the Couvreur acc-set driver.
now_eval only ever returns constants or an arm, so the passes cannot
ping-pong.

At an Or node (dually at And):

    c ∨ X F c               → F c       [F expansion law]
    c ∨ F(¬c ∧ X c)         → F c       [first occurrence: the earliest c
                                         is now or strictly later]
    g ∨ (f ∧ X(f U g))      → f U g     [U expansion law]
    g ∨ (f ∧ X(f W g))      → f W g     [W expansion law]

    c ∧ X G c               → G c       [G expansion law]
    c ∧ G(¬c ∨ X c)         → G c       [induction: c now + G(c → Xc)]
    g ∧ (f ∨ X(f R g))      → f R g     [R expansion law]
    g ∧ (f ∨ X(f M g))      → f M g     [M expansion law]

Plus two sibling-subsumption rules (the Formula-5 line redundancy: the
construction disjoins the strong-reach lines with the "stay forever" G
line, and the G line is implied by the R line whenever the Or also holds
the now-case c):

    c ∨ X(c R d) ∨ G(c ∨ Xd)    → c ∨ X(c R d)     [S1: drop the G]
    c ∧ X(c U d) ∧ F(c ∧ Xd)    → c ∧ X(c U d)     [S2: drop the F, dual]

S1 soundness: assume G(c ∨ Xd) and ¬c now; for any i ≥ 1, either some
j ∈ [1, i-1] has c, or ¬c on [0, i-1] and the G clause at i-1 forces d@i —
exactly c R d from position 1. S2 is the literal dual. The M/W variants are
NOT valid (the c-never case needs no eventual c) and are excluded.

All rules are plain language equivalences for ARBITRARY c/d/f/g (no
propositional restriction). The ¬c match is two-tier like now_eval:
hash-consed identity against spot.formula.Not(c), then BDD complement for
propositional c. Each fold removes at least one child of the boolean node,
so the per-node loop terminates; the whole pass is a memoized bottom-up
walk, O(DAG) with persistent results.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple

import buddy
import spot

from .now_eval import _prop_bdd


def _is_neg(g: "spot.formula", c: "spot.formula") -> bool:
    """g ≡ ¬c — identity tier (Not constructor folds involution), then BDD
    complement when both sides are propositional."""
    if g == spot.formula.Not(c):
        return True
    bg, bc = _prop_bdd(g), _prop_bdd(c)
    return bg is not None and bc is not None and bg == buddy.bdd_not(bc)


def _find_fold_or(kids: List["spot.formula"]) -> Optional[Tuple[int, int, "spot.formula"]]:
    """One applicable Or-fold: (index, partner index, replacement)."""
    pos = {k: i for i, k in enumerate(kids)}
    for i, k in enumerate(kids):
        # c | XFc -> Fc
        if k._is(spot.op_X) and k[0]._is(spot.op_F):
            j = pos.get(k[0][0])
            if j is not None:
                return i, j, k[0]
        # c | F(¬c & Xc) -> Fc
        if k._is(spot.op_F) and k[0]._is(spot.op_And):
            subs = list(k[0])
            for s in subs:
                if s._is(spot.op_X):
                    j = pos.get(s[0])
                    if j is None:
                        continue
                    rest = spot.formula.And([t for t in subs if t != s])
                    if _is_neg(rest, s[0]):
                        return i, j, spot.formula.F(s[0])
        # g | (f & X(f U g)) -> f U g   (same for W)
        if k._is(spot.op_And):
            subs = list(k)
            for s in subs:
                if s._is(spot.op_X) and (s[0]._is(spot.op_U) or s[0]._is(spot.op_W)):
                    u = s[0]
                    j = pos.get(u[1])
                    if j is None:
                        continue
                    rest = spot.formula.And([t for t in subs if t != s])
                    if rest == u[0]:
                        return i, j, u
    return None


def _find_fold_and(kids: List["spot.formula"]) -> Optional[Tuple[int, int, "spot.formula"]]:
    """One applicable And-fold (dual of _find_fold_or)."""
    pos = {k: i for i, k in enumerate(kids)}
    for i, k in enumerate(kids):
        # c & XGc -> Gc
        if k._is(spot.op_X) and k[0]._is(spot.op_G):
            j = pos.get(k[0][0])
            if j is not None:
                return i, j, k[0]
        # c & G(¬c | Xc) -> Gc
        if k._is(spot.op_G) and k[0]._is(spot.op_Or):
            subs = list(k[0])
            for s in subs:
                if s._is(spot.op_X):
                    j = pos.get(s[0])
                    if j is None:
                        continue
                    rest = spot.formula.Or([t for t in subs if t != s])
                    if _is_neg(rest, s[0]):
                        return i, j, spot.formula.G(s[0])
        # g & (f | X(f R g)) -> f R g   (same for M)
        if k._is(spot.op_Or):
            subs = list(k)
            for s in subs:
                if s._is(spot.op_X) and (s[0]._is(spot.op_R) or s[0]._is(spot.op_M)):
                    r = s[0]
                    j = pos.get(r[1])
                    if j is None:
                        continue
                    rest = spot.formula.Or([t for t in subs if t != s])
                    if rest == r[0]:
                        return i, j, r
    return None


def _find_subsumed_or(kids: List["spot.formula"]) -> Optional[int]:
    """S1: index of a G(c | Xd) disjunct made redundant by sibling
    disjuncts c (possibly split by flattening) and X(c R d)."""
    pos = set(kids)
    for i, k in enumerate(kids):
        if k._is(spot.op_G) and k[0]._is(spot.op_Or):
            body = list(k[0])
            for s in body:
                if s._is(spot.op_X):
                    rest = [t for t in body if t != s]
                    c = spot.formula.Or(rest)
                    if (all(t in pos for t in rest)
                            and spot.formula.X(spot.formula.R(c, s[0])) in pos):
                        return i
    return None


def _find_subsumed_and(kids: List["spot.formula"]) -> Optional[int]:
    """S2 (dual): index of an F(c & Xd) conjunct made redundant by sibling
    conjuncts c and X(c U d)."""
    pos = set(kids)
    for i, k in enumerate(kids):
        if k._is(spot.op_F) and k[0]._is(spot.op_And):
            body = list(k[0])
            for s in body:
                if s._is(spot.op_X):
                    rest = [t for t in body if t != s]
                    c = spot.formula.And(rest)
                    if (all(t in pos for t in rest)
                            and spot.formula.X(spot.formula.U(c, s[0])) in pos):
                        return i
    return None


def _fold_node(node: "spot.formula") -> "spot.formula":
    """Fold one boolean node to its fixpoint (children assumed processed)."""
    is_and = node._is(spot.op_And)
    finder = _find_fold_and if is_and else _find_fold_or
    subsumer = _find_subsumed_and if is_and else _find_subsumed_or
    kids = list(node)
    changed = False
    while len(kids) >= 2:
        drop = subsumer(kids)
        if drop is not None:
            kids = [k for idx, k in enumerate(kids) if idx != drop]
            changed = True
            continue
        hit = finder(kids)
        if hit is None:
            break
        i, j, rep = hit
        kids = [k for idx, k in enumerate(kids) if idx not in (i, j)]
        kids.append(rep)
        changed = True
    if not changed:
        return node
    return spot.formula.And(kids) if is_and else spot.formula.Or(kids)


# Persistent memo (see context_pass note): per-DAG-node pipeline usage is
# amortized O(1) per node only if results survive across calls.
_memo: Dict["spot.formula", "spot.formula"] = {}


def reset_cache() -> None:
    _memo.clear()


def fold_simplify(f: "spot.formula") -> "spot.formula":
    """Bottom-up unroll-inverse folding over the whole DAG (memoized)."""
    memo = _memo

    def walk(n: "spot.formula") -> "spot.formula":
        hit = memo.get(n)
        if hit is not None:
            return hit
        if n._is(spot.op_And) or n._is(spot.op_Or):
            kids = [walk(c) for c in n]
            out = spot.formula.And(kids) if n._is(spot.op_And) else spot.formula.Or(kids)
            # Constructors flatten/dedupe; fold only what is still boolean.
            if out._is(spot.op_And) or out._is(spot.op_Or):
                out = _fold_node(out)
        elif list(n):
            out = n.map(walk)
        else:
            out = n
        memo[n] = out
        return out

    return walk(f)
