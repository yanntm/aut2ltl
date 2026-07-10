"""Harness: the product-table materialization law (`calculus.product`).

    python3 -m tests.calculus.product_gate A.sos B.sos
    python3 -m tests.calculus.product_gate --sample [N] [--corpus DIR] [--seed S]

`materialize(align(a, b), a, b)` builds the product omega-semigroup and carries
each side as a pair set over it. The gate reduces the Boolean combinations and
checks, over EVERY canonical cell lasso of the aligned product, that the built
object denotes the right language:

- `member(reduce(a ∩ b), w) == member(a, w) and member(b, w)`
- `member(reduce(a ∪ b), w) == member(a, w) or  member(b, w)`

for all `w = key(c)·key(d)^ω`. It also asserts both carried sides are saturated
pair sets (the internal legality invariant of the surgery catalog), and that the
product intersection is empty exactly when `intersecting_word` on the aligned
product reports no shared word — the align-side decision cross-check.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import List, Tuple

from sosl.sos import Invariant, load_invariant
from sosl.sos.calculus import (
    Table,
    align,
    intersection,
    intersecting_word,
    is_empty,
    is_saturated,
    materialize,
    member,
    reduce,
    union,
)

_HERE = Path(__file__).resolve().parent
_CORPUS = _HERE.parents[2] / "genaut" / "corpus" / "flat_canon"


def _lang(inv: Invariant):
    return Table.of(inv).language(inv.accept)


def check_pair(inv_a: Invariant, inv_b: Invariant, name: str) -> None:
    """The materialization law for one pair over the same alphabet."""
    la, lb = _lang(inv_a), _lang(inv_b)
    assert la.alphabet == lb.alphabet, f"{name}: alphabets differ"
    aligned = align(la, lb)
    prod = materialize(aligned, la, lb)

    assert is_saturated(prod.table, prod.pairs_a), f"{name}: a-side not saturated"
    assert is_saturated(prod.table, prod.pairs_b), f"{name}: b-side not saturated"

    inter = reduce(prod.table, intersection(prod.table, prod.pairs_a, prod.pairs_b))
    uni = reduce(prod.table, union(prod.table, prod.pairs_a, prod.pairs_b))
    ti, ai = Table.of(inter), inter.accept
    tu, au = Table.of(uni), uni.accept

    checked = 0
    for cell in aligned.cells():
        w = aligned.cell_lasso(cell)
        ma = member(la.table, la.pairs, w)
        mb = member(lb.table, lb.pairs, w)
        assert member(ti, ai, w) == (ma and mb), f"{name}: ∩ law at {w.render()}"
        assert member(tu, au, w) == (ma or mb), f"{name}: ∪ law at {w.render()}"
        checked += 1

    shared, _ = intersecting_word(aligned)
    empty, _ = is_empty(ti, ai)
    assert shared == (not empty), f"{name}: ∩ emptiness disagrees with intersecting_word"
    print(f"  {name}: nodes {aligned.n} (ratio {aligned.ratio:.4f}), "
          f"|∩|={inter.n} |∪|={uni.n}, {checked} cells checked")


def _pairs_of_stratum(sos_dir: Path, n: int, seed: int
                      ) -> List[Tuple[str, str]]:
    """`n` random same-alphabet basename pairs from the corpus."""
    groups: dict = {}
    for p in sorted(sos_dir.glob("*.sos")):
        inv = load_invariant(p.read_text())
        groups.setdefault(tuple(inv.alphabet.aps), []).append(p.stem)
    big = [g for g, lst in sorted(groups.items()) if len(lst) >= 2]
    rng = random.Random(seed)
    out: List[Tuple[str, str]] = []
    while len(out) < n:
        g = rng.choice(big)
        lst = groups[g]
        i, j = rng.sample(range(len(lst)), 2)
        out.append((lst[i], lst[j]))
    return out


def main(argv: List[str]) -> int:
    if argv and argv[0] == "--sample":
        n = 20
        corpus, seed = _CORPUS, 20260710
        rest = argv[1:]
        if rest and rest[0].isdigit():
            n = int(rest[0]); rest = rest[1:]
        it = iter(rest)
        for a in it:
            if a == "--corpus":
                corpus = Path(next(it))
            elif a == "--seed":
                seed = int(next(it))
        sos_dir = corpus / "sos"
        print(f"=== product_gate: {n} sampled same-alphabet pairs (seed {seed}) ===")
        for x, y in _pairs_of_stratum(sos_dir, n, seed):
            ix = load_invariant((sos_dir / f"{x}.sos").read_text())
            iy = load_invariant((sos_dir / f"{y}.sos").read_text())
            check_pair(ix, iy, f"{x} × {y}")
        print("SUCCESS")
        return 0
    if len(argv) == 2:
        ix = load_invariant(Path(argv[0]).read_text())
        iy = load_invariant(Path(argv[1]).read_text())
        check_pair(ix, iy, f"{Path(argv[0]).stem} × {Path(argv[1]).stem}")
        print("SUCCESS")
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
