"""Self-checking toy-AST tests of `aut2ltl/bls/definability/dg/formulas.py`:
the three [DG] transformations checked against their defining semantic
properties, exhaustively over small finite words — no automata, no algebra
(build-order step 4 of `dg/algorithm.md` layer 14; ω-behavior is the step-5
Spot probe's job, finite models pin every clause).

- lift:  `cw, 0 ⊨ φ^b  ⟺  c·bfp(w), 0 ⊨ φ`  (bfp = largest b-free prefix)
- tilde: `cv, 0 ⊨ ξ̃    ⟺  σ(v), 0 ⊨ ξ`      (toy 2-element morphism)
- pe:    `fresh·w, 0 ⊨ φ  ⟺  w, 0 ⊨ PE(φ)`

Usage:  python3 tests/smoke/dg_formulas.py     (exit 0 iff all checks pass)
"""
from __future__ import annotations

import itertools
import sys
from typing import Callable, Dict, List, Tuple

from aut2ltl.bls.definability.dg.formulas import Ast


def sat(ast: Ast, i: int, w: List[int], p: int) -> bool:
    """The [XU] semantics, transcribed naively: models are non-empty finite
    words with a position; `φ XU ψ` = some strictly later `ψ`, `φ` strictly
    in between."""
    n = ast.node(i)
    if n[0] == "top":
        return True
    if n[0] == "atom":
        return w[p] == n[1]
    if n[0] == "not":
        return not sat(ast, n[1], w, p)
    if n[0] == "or":
        return sat(ast, n[1], w, p) or sat(ast, n[2], w, p)
    return any(sat(ast, n[2], w, j)
               and all(sat(ast, n[1], w, k) for k in range(p + 1, j))
               for j in range(p + 1, len(w)))


def words(alphabet: List[int], max_len: int) -> List[List[int]]:
    return [list(t) for n in range(max_len + 1)
            for t in itertools.product(alphabet, repeat=n)]


def check_lift(ast: Ast) -> int:
    b = 2
    a0, a1 = ast.atom(0), ast.atom(1)
    xtop = ast.x(ast.top())
    forms: List[int] = [
        a0, ast.atom(b), ast.neg(a0), ast.or_(a0, a1), ast.x(a0),
        ast.neg(xtop), ast.xu(a0, a1), ast.u(a0, a1),
        ast.xu(ast.top(), ast.and_(a1, ast.x(a0))),
        ast.xu(ast.xu(a0, a1), a1),
    ]
    n = 0
    for c in (0, 1, 2):
        for w in words([0, 1, 2], 5):
            bfp = w[:w.index(b)] if b in w else w
            for f in forms:
                got = sat(ast, ast.lift(f, b), [c] + w, 0)
                want = sat(ast, f, [c] + bfp, 0)
                assert got == want, \
                    f"lift: node {f}, c={c}, w={w}: {got} != {want}"
                n += 1
    return n


def check_tilde(ast: Ast) -> int:
    # Toy instance: Δ = {c=0, a=1}, monoid {1, s} with h(a) = s, s·s = s.
    # Compressed atoms: 0 = T₁:1, 1 = T₁:s, 2 = T₂:[ε], 3 = T₂:fiber-s.
    c = 0
    catom = ast.atom(c)
    empty_block = ast.neg(ast.x(ast.top()))      # L_{c,A}(·) = {ε}
    some_block = ast.x(ast.top())                # L_{c,A}(·) = A⁺ (= fiber s)
    sub_map: Dict[int, int] = {
        0: ast.and_(ast.lift(empty_block, c), ast.xf(catom)),
        1: ast.and_(ast.lift(some_block, c), ast.xf(catom)),
        2: ast.and_(ast.lift(empty_block, c), ast.neg(ast.xf(catom))),
        3: ast.and_(ast.lift(some_block, c), ast.neg(ast.xf(catom))),
    }
    sub: Callable[[int], int] = sub_map.__getitem__

    def sigma(v: List[int]) -> List[int]:
        blocks: List[List[int]] = [[]]
        for letter in v:
            if letter == c:
                blocks.append([])
            else:
                blocks[-1].append(letter)
        return ([0 if len(blk) == 0 else 1 for blk in blocks[:-1]]
                + [2 if len(blocks[-1]) == 0 else 3])

    t0, t1, t2, t3 = (ast.atom(i) for i in range(4))
    forms: List[int] = [
        t0, t1, t2, t3, ast.neg(t3), ast.or_(t0, t3), ast.x(t3),
        ast.xu(t1, t3), ast.xu(ast.top(), t2), ast.u(t1, t3),
    ]
    n = 0
    for v in words([0, 1], 6):
        sv = sigma(v)
        for f in forms:
            got = sat(ast, ast.tilde(f, c, sub), [c] + v, 0)
            want = sat(ast, f, sv, 0)
            assert got == want, f"tilde: node {f}, v={v}: {got} != {want}"
            n += 1
    return n


def check_pe(ast: Ast) -> int:
    fresh = 3
    a0, a1, a3 = ast.atom(0), ast.atom(1), ast.atom(fresh)
    forms: List[int] = [
        a0, a3, ast.neg(a3), ast.or_(a0, a3), ast.x(a0),
        ast.xu(a0, a1), ast.u(a0, a1), ast.and_(a3, ast.x(a1)),
        ast.neg(ast.x(ast.top())),
    ]
    n = 0
    for w in words([0, 1, 2], 5):
        if not w:
            continue
        for f in forms:
            got = sat(ast, ast.pe(f, fresh), w, 0)
            want = sat(ast, f, [fresh] + w, 0)
            assert got == want, f"pe: node {f}, w={w}: {got} != {want}"
            n += 1
    return n


def check_consing(ast: Ast) -> int:
    a0, a1 = ast.atom(0), ast.atom(1)
    assert ast.and_(a0, a1) == ast.and_(a0, a1)
    f = ast.xu(a0, a1)
    assert ast.lift(f, 2) == ast.lift(f, 2)
    size = len(ast)
    ast.lift(f, 2)
    ast.u(a0, a1)
    assert len(ast) == size, "re-building known terms grew the arena"
    assert ast.to_spot(ast.x(a0), ["p", "q"]) == "X(!1 U (p))"
    return 4


def main() -> int:
    ast = Ast()
    total = 0
    for name, chk in (("lift", check_lift), ("tilde", check_tilde),
                      ("pe", check_pe), ("consing", check_consing)):
        n = chk(ast)
        total += n
        print(f"dg_formulas: {name:8s} ok ({n} checks)")
    print(f"dg_formulas: SUCCESS ({total} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
