"""FIG-2 — the doubled-word cut on F-D (paper §3.1, Lemma 3.1).

    python3 -m tests.quant.figs.fig2 SRC.sos [OUT.tex]
    python3 -m tests.quant.figs.fig2 SRC.sos --scan   # seed search, report only

Lemma 3.1's mechanism on one concrete random word over the §3.4 example,
whose kernel idempotent ``k = fold(aa)`` has ``H(k) ≅ ℤ/2`` — the one case
where the maximal group is drawable as a parity. The probe seeds an RNG,
samples a uniform word, finds the disjoint occurrences of ``w·w = aaaa``,
cuts at their midpoints, folds each inter-cut block (its fold lands in
``H(k)``, shown as its parity), forms the cumulative product, picks the
recurring group value ``g`` — its cut positions are the ``J``-cuts — and
verifies each inter-``J`` block folds to ``k`` exactly. Everything drawn is
computed by folding substrings with the engine's `Table`.
"""
from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple

from sosl.sos import Letter, load_invariant
from sosl.sos.calculus import Table
from sosl.quant import kernel_idempotent

from tests.quant.figs import tikz

A, B = Letter(1), Letter(0)             # a = mask 1, b = mask 0 (renders !a)
SEED = 20260887                          # a length-56 word with a clean H(k) excursion
LENGTH = 56
W = (A, A)                              # fold(W) = k; the doubled word is W.W = aaaa


@dataclass
class Cut:
    """One midpoint cut of a disjoint ``aaaa`` occurrence."""
    occ_start: int                      # index where the aaaa occurrence begins
    pos: int                            # the midpoint (occ_start + 2)


@dataclass
class Structure:
    word: Tuple[Letter, ...]
    cuts: List[Cut]
    stem_class: int
    block_parity: List[int]             # H(k) value (r-coord) of each inter-cut block
    cumulative: List[int]               # running product parity after each cut
    g: int                              # the recurring group value
    j_cuts: List[int]                   # indices into `cuts` where cumulative == g


def _r(tab: Table, c: int) -> int:
    """The ℤ/2 length-parity coordinate of class ``c`` (``len(key) mod 2``);
    on ``H(k)`` this is the group element, ``k`` being the even one."""
    return len(tab.keys[c]) % 2


def _occurrences(word: Tuple[Letter, ...]) -> List[Cut]:
    """Left-to-right disjoint occurrences of ``aaaa`` and their midpoints."""
    cuts: List[Cut] = []
    i, n = 0, len(word)
    while i + 4 <= n:
        if word[i:i + 4] == (A, A, A, A):
            cuts.append(Cut(i, i + 2))
            i += 4
        else:
            i += 1
    return cuts


def analyze(inv, word: Tuple[Letter, ...]) -> Optional[Structure]:
    tab = Table.of(inv)
    k = kernel_idempotent(inv)
    cuts = _occurrences(word)
    if len(cuts) < 2:
        return None
    positions = [c.pos for c in cuts]
    stem_class = tab.fold(word[:positions[0]])
    block_parity: List[int] = []
    for i in range(len(positions) - 1):
        block = word[positions[i]:positions[i + 1]]
        cls = tab.fold(block)
        assert _r(tab, cls) == len(block) % 2         # fold in H(k): parity = length parity
        block_parity.append(_r(tab, cls))
    cumulative: List[int] = []
    acc = 0
    for p in block_parity:
        acc ^= p
        cumulative.append(acc)
    # recurring value g: the parity most frequent among the cut states.
    g = 0 if cumulative.count(0) >= cumulative.count(1) else 1
    j_cuts = [i for i, v in enumerate(cumulative) if v == g]
    # inter-J blocks fold to k exactly (the H(k) identity, parity 0).
    for a, b in zip(j_cuts, j_cuts[1:]):
        seg = word[positions[a + 1]:positions[b + 1]]
        assert tab.fold(seg) == k, "inter-J block does not fold to k"
    return Structure(word, cuts, stem_class, block_parity, cumulative, g, j_cuts)


def _sample(seed: int, n: int) -> Tuple[Letter, ...]:
    rng = random.Random(seed)
    return tuple(Letter(rng.randint(0, 1)) for _ in range(n))


def _grow(inv, seed: int) -> Tuple[Structure, int]:
    """The structure at ``seed``, lengthening the word until it has at least
    three ``J``-cuts (so at least two inter-``J`` blocks to bracket)."""
    n = LENGTH
    while n <= 4 * LENGTH:
        st = analyze(inv, _sample(seed, n))
        if st is not None and len(st.j_cuts) >= 3:
            return st, n
        n += 16
    raise RuntimeError(f"seed {seed} never reached three J-cuts by n={n}")


def scan(inv) -> None:
    """Rank seeds by word length; flag an *excursion* — the cumulative
    parity leaving ``g`` and returning — the interesting recurrence."""
    rows = []
    for seed in range(SEED, SEED + 300):
        try:
            st, n = _grow(inv, seed)
        except RuntimeError:
            continue
        span = st.cumulative[st.j_cuts[0]:st.j_cuts[-1] + 1]
        excursion = any(v != st.g for v in span)
        rows.append((n, excursion, seed, st.g, st.block_parity, st.cumulative))
    rows.sort(key=lambda r: (not r[1], r[0]))         # excursions first, then short
    for n, exc, seed, g, par, cum in rows[:16]:
        print(f"seed {seed} n {n} {'EXC' if exc else '   '} g={g} "
              f"parities {par} cum {cum}")


def report(inv) -> None:
    st, n = _grow(inv, SEED)
    txt = "".join("a" if x == A else "b" for x in st.word)
    print(f"seed {SEED}, n {n}")
    print(f"word {txt}")
    print(f"cuts at {[c.pos for c in st.cuts]} (occurrences at "
          f"{[c.occ_start for c in st.cuts]})")
    print(f"stem class {st.stem_class} (key {' '.join(map(str, Table.of(inv).keys[st.stem_class])) or 'eps'})")
    print(f"block parities {st.block_parity}")
    print(f"cumulative    {st.cumulative}")
    print(f"g = {st.g}; J-cuts at block indices {st.j_cuts} -> "
          f"cut positions {[st.cuts[i + 1].pos for i in st.j_cuts]}")


def main() -> None:
    inv = load_invariant(open(sys.argv[1]).read())
    if len(sys.argv) > 2 and sys.argv[2] == "--scan":
        scan(inv)
    elif len(sys.argv) > 2:
        from tests.quant.figs.fig2_draw import draw
        open(sys.argv[2], "w").write(draw(inv, *_grow(inv, SEED)))
        print(f"wrote {sys.argv[2]}")
    else:
        report(inv)


if __name__ == "__main__":
    main()
