"""Harness 7: the corpus as an equality oracle.

    python3 -m tests.calculus.corpus_oracle DIR [COUNT] [SEED]

`flat_canon/` holds one file per language, so **language equality is filename
equality** — an answer key the calculus never sees. Sample ``COUNT`` files over
one alphabet and demand:

- a file against a separately loaded copy of *itself*: `equivalent` says yes,
  and `byte_equivalent` of the reduced sides agrees;
- a file against any *other* file: `equivalent` says no, and its counterexample
  replays correctly against **both** `.sos` sides — positive on the left,
  negative on the right.

Per the expected-failure table, a disagreement here indicts the calculus first
and the corpus dedup second; it is reported, never "fixed" in the corpus. The
alignment ratio of every pair is accumulated: this is the V1 ledger's raw
material.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path
from statistics import median
from typing import List, Tuple

from sosl.sos import Invariant, Lasso, load_invariant
from sosl.sos.calculus import Table, align, byte_equivalent, equivalent, reduce

DEFAULT_COUNT = 10
"""Files sampled; the gate runs all COUNT^2 ordered pairs."""


def load_sample(directory: Path, count: int, seed: int) -> List[Tuple[Path, Invariant]]:
    """``count`` `.sos` files drawn at random, restricted to the alphabet of the
    first draw — `align` compares languages over one alphabet only."""
    rng = random.Random(seed)
    paths = sorted(directory.glob("*.sos"))
    assert len(paths) >= count, f"{directory} holds only {len(paths)} files"
    rng.shuffle(paths)

    out: List[Tuple[Path, Invariant]] = []
    alphabet = None
    for path in paths:
        inv = load_invariant(path.read_text())
        if alphabet is None:
            alphabet = inv.alphabet
        if inv.alphabet != alphabet:
            continue
        out.append((path, inv))
        if len(out) == count:
            break
    assert len(out) == count, f"only {len(out)} files over ap {alphabet}"
    return out


def check_same(path: Path, inv: Invariant) -> float:
    """A file against a fresh copy of itself: equivalent, and byte-equal once
    reduced."""
    twin = load_invariant(path.read_text())
    product = align(Table.of(inv).language(inv.accept),
                    Table.of(twin).language(twin.accept))
    eq, w = equivalent(product)
    assert eq, f"{path.name} is not equivalent to itself: {w.render() if w else ''}"
    left = reduce(Table.of(inv), inv.accept, check=False)
    right = reduce(Table.of(twin), twin.accept, check=False)
    assert byte_equivalent(left, right), f"{path.name}: reduced copies differ"
    return product.ratio


def check_distinct(
    left_path: Path, left: Invariant, right_path: Path, right: Invariant
) -> float:
    """Two different files: not equivalent, with a replayable separator."""
    product = align(Table.of(left).language(left.accept),
                    Table.of(right).language(right.accept))
    eq, w = equivalent(product)
    assert not eq, (
        f"{left_path.name} and {right_path.name} are one language to the scan, "
        f"but the corpus stores them apart"
    )
    assert w is not None
    w.replay(lambda u, v: left.member(Lasso(u, v)))
    assert right.member(w.lasso) != w.expected, (
        f"{left_path.name} vs {right_path.name}: witness {w.render()} "
        f"does not separate them"
    )
    assert not byte_equivalent(
        reduce(Table.of(left), left.accept, check=False),
        reduce(Table.of(right), right.accept, check=False),
    ), "scan separates them but the reduced bytes agree"
    return product.ratio


def main(argv: List[str]) -> int:
    directory = Path(argv[1])
    count = int(argv[2]) if len(argv) > 2 else DEFAULT_COUNT
    seed = int(argv[3]) if len(argv) > 3 else 0
    sample = load_sample(directory, count, seed)
    aps = " ".join(sample[0][1].alphabet.aps) or "(none)"
    sizes = [inv.n for _, inv in sample]
    print(f"{directory}: {count} files over ap {aps}, "
          f"|C| in [{min(sizes)}, {max(sizes)}], seed {seed}")

    ratios: List[float] = []
    for path, inv in sample:
        ratios.append(check_same(path, inv))
    print(f"  same-file pairs: {count} equivalent, reduced bytes equal")

    pairs = 0
    for i, (lp, left) in enumerate(sample):
        for rp, right in sample[i + 1:]:
            ratios.append(check_distinct(lp, left, rp, right))
            pairs += 1
    print(f"  cross-file pairs: {pairs} separated, every witness replays on both sides")
    print(f"  alignment ratio |nodes|/(n_A*n_B): min {min(ratios):.4f}, "
          f"median {median(ratios):.4f}, max {max(ratios):.4f}")
    print("SUCCESS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
