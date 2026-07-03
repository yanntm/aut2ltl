"""The local divisor — the monoid-shrinking step of the synthesis.

For a finite monoid given by its multiplication table and a non-identity
element `m`, the local divisor (`algorithm.md` layer 3, [DG] §8.1) is the
monoid on

    T' = mT ∩ Tm        with        xm ∘ my = xmy        identity: m

It divides the base monoid, hence stays aperiodic when the base is; and on an
aperiodic base the identity never lands in the carrier (`1 = mx` would force
`m = 1`), so `|T'| < |T|` — the strict decrease that drives the induction.
Both facts are guarded by asserts: a firing assert means the input carried a
group and should have been refused upstream.

Carrier elements keep their base indices (sorted ascending — base indices are
canonical, so this order is too); the `∘` table is on carrier positions. The
input is any monoid table, so the construction applies uniformly to a base
`Alg` and to a `Divisor`'s own table further down the descent.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple


@dataclass(frozen=True)
class Divisor:
    """The local divisor at `m`, as pure tables — hashable, like `Alg`.

    `carrier[i]` is the base index of divisor element `i`; `unit` is the
    position of `m` in the carrier; `mult` is the `∘` table on positions.
    """

    m: int                             # the pivot image, a base index
    carrier: Tuple[int, ...]           # divisor elements, base indices, ascending
    unit: int                          # position of m in carrier
    mult: Tuple[Tuple[int, ...], ...]  # position × position -> position

    def __len__(self) -> int:
        return len(self.carrier)


def local_divisor(mult: Sequence[Sequence[int]], m: int, unit: int = 0) -> Divisor:
    """Build the local divisor of the monoid `mult` at element `m ≠ unit`.

    `mult` is a total multiplication table with identity at index `unit`.
    The `∘` product is computed through a witness per carrier element: any
    `t` with `m·t = y` gives `x ∘ y = x·t`, independent of the choice when
    `x ∈ Tm` — the least such `t` is taken, for determinism. Asserts guard
    aperiodicity's two consequences: the identity stays out of the carrier
    (strict decrease) and `∘` closes over it.
    """
    assert m != unit, "the pivot image must not be the identity"
    k: int = len(mult)
    m_left: List[int] = list(mult[m])                 # mT, indexed by t
    right_set = {mult[t][m] for t in range(k)}        # Tm
    carrier: Tuple[int, ...] = tuple(sorted(set(m_left) & right_set))
    assert unit not in carrier, \
        "identity in mT ∩ Tm: the monoid carries a group (not a dg input)"

    pos = {y: i for i, y in enumerate(carrier)}
    wit: List[int] = [m_left.index(y) for y in carrier]   # least t with m·t = y
    table: List[Tuple[int, ...]] = []
    for x in carrier:
        row: List[int] = []
        for j in range(len(carrier)):
            xy: int = mult[x][wit[j]]
            assert xy in pos, "∘ left the carrier: not a local divisor"
            row.append(pos[xy])
        table.append(tuple(row))

    return Divisor(m=m, carrier=carrier, unit=pos[m], mult=tuple(table))


__all__ = ["Divisor", "local_divisor"]
