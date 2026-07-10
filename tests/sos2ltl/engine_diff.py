"""Ground the engine's per-class labels against the invariant, on ONE input.

    python3 -m tests.sos2ltl.engine_diff <file.sos> [--stem N] [--loop N] [--plain]

``--plain`` builds the memo with residual indexing off (`Rendering`), which
isolates whether a divergence lives in the bricks or in the exit-child
residual substitution.

Stop-the-line diagnostics for a conformance FAIL: rebuilds the engine's
class-indexed memo (`engine.labels`), searches the shortest lasso (stems up
to ``--stem``, loops up to ``--loop``, shortlex) on which the root label
disagrees with the invariant's own membership read-off, then walks that
witness through `Cay(L)` and checks, at every suffix position `j`, the
label `Final(c_j)` against the ground-truth tail verdict of `T_{c_j}`
(computed from the invariant alone). The deepest disagreeing position
localizes the broken brick; the per-layer width/committed table prints
alongside. One input per invocation (repo discipline: ≤ 15 s per example).
"""
from __future__ import annotations

import itertools
import sys
from typing import Dict, List, Optional, Tuple

import spot

from aut2ltl.sos2ltl import anchoring, engine
from aut2ltl.sos2ltl.cayley import build
from aut2ltl.sos2ltl.witness.spot_oracle import render_lasso
from aut2ltl.verifier.check import member
from sosl.sos import Invariant, Lasso, load_invariant


def tail_verdict(inv: Invariant, c: int, lasso: Lasso) -> bool:
    """Ground truth: is the lasso in `T_c`? Fold the stem from `c`, absorb
    the loop's idempotent, look the linked pair up in `P`."""
    s = c
    for a in lasso.stem:
        s = inv.mult[s][inv.letter_class[a]]
    e = inv.idempotent_power(inv.fold(lasso.loop))
    return (inv.mult[s][e], e) in inv.accept


class _Labels:
    """The memo's labels as Spot acceptors, translated once per class."""

    def __init__(self, inv: Invariant, memo: Dict[int, "spot.formula"]):
        self.inv = inv
        self.memo = memo
        self._auts: Dict[int, "spot.twa_graph"] = {}

    def accepts(self, c: int, lasso: Lasso) -> bool:
        aut = self._auts.get(c)
        if aut is None:
            aut = spot.translate(self.memo[c])
            self._auts[c] = aut
        return member(aut, render_lasso(self.inv.alphabet, lasso))


def lassos(inv: Invariant, stem_max: int, loop_max: int):
    """All lassos with |stem| ≤ stem_max, 1 ≤ |loop| ≤ loop_max, shortlex."""
    letters = inv.alphabet.letters()
    for total in range(1, stem_max + loop_max + 1):
        for ls in range(1, min(loop_max, total) + 1):
            st = total - ls
            if st > stem_max:
                continue
            for stem in itertools.product(letters, repeat=st):
                for loop in itertools.product(letters, repeat=ls):
                    yield Lasso(stem=stem, loop=loop)


def classes_along(inv: Invariant, lasso: Lasso) -> List[int]:
    """`c_j` for `j = 0 .. |stem| + 2|loop|`: the class of the prefix read."""
    out = [inv.identity]
    c = inv.identity
    for a in tuple(lasso.stem) + tuple(lasso.loop) * 2:
        c = inv.mult[c][inv.letter_class[a]]
        out.append(c)
    return out


def suffix_at(lasso: Lasso, j: int) -> Lasso:
    """The suffix of the lasso word at position `j`, as a lasso."""
    stem, loop = tuple(lasso.stem), tuple(lasso.loop)
    if j <= len(stem):
        return Lasso(stem=stem[j:], loop=loop)
    i = (j - len(stem)) % len(loop)
    return Lasso(stem=(), loop=loop[i:] + loop[:i])


def main(argv: List[str]) -> int:
    path = argv[0]
    stem_max = int(argv[argv.index("--stem") + 1]) if "--stem" in argv else 5
    loop_max = int(argv[argv.index("--loop") + 1]) if "--loop" in argv else 4
    with open(path) as f:
        inv = load_invariant(f.read())

    cay = build(inv)
    anch = anchoring.analyze(cay)
    print(f"{path}: |C| = {inv.n}, {len(cay.layers)} layers")
    for i, la in enumerate(anch):
        comm = [c for c in la.layer if engine._committed(cay, c)]
        print(f"  layer {i}: classes {la.layer} width {la.width}"
              f" committed {comm}")

    rend = (engine.Rendering(residual=False) if "--plain" in argv
            else engine.DEFAULT)
    memo = engine.labels(inv, rend=rend)
    assert memo is not None, "engine declined — nothing to diff"
    lab = _Labels(inv, memo)

    root = inv.identity
    hit: Optional[Lasso] = None
    for lasso in lassos(inv, stem_max, loop_max):
        if tail_verdict(inv, root, lasso) != lab.accepts(root, lasso):
            hit = lasso
            break
    if hit is None:
        print(f"no disagreement up to stems {stem_max} / loops {loop_max}")
        return 0

    render = render_lasso(inv.alphabet, hit)
    gt_root = tail_verdict(inv, root, hit)
    print(f"witness: {render}  (language: {gt_root},"
          f" label: {not gt_root})")
    cj = classes_along(inv, hit)
    n = len(tuple(hit.stem)) + 2 * len(tuple(hit.loop))
    for j in range(n + 1):
        suf = suffix_at(hit, j)
        gt = tail_verdict(inv, cj[j], suf)
        got = lab.accepts(cj[j], suf)
        mark = "" if gt == got else "   <-- DIVERGES"
        lay = next(i for i, la in enumerate(anch) if cj[j] in la.layer)
        print(f"  pos {j}: class {cj[j]} (layer {lay})"
              f" suffix {render_lasso(inv.alphabet, suf)}"
              f" GT {gt} label {got}{mark}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
