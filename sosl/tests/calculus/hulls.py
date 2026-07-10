"""CAL5 gate: the hull surgeries — safety closure, interior, liveness part.

    python3 -m tests.calculus.hulls PATH.sos [SEED]

Over the input's own language, the constants, and random saturated pair sets:

1. **Closure laws** — `safety_closure` is extensive, monotone and idempotent;
   `interior` is its dual fixpoint (contractive, idempotent); both outputs and
   `liveness_part` satisfy the saturation law.
2. **Duality** — ``interior(P) == complement(safety_closure(complement(P)))``.
3. **Decomposition** — ``P == safety_closure(P) & liveness_part(P)``, and every
   class is `live` for ``liveness_part(P)`` (its closure is the universal
   language): Alpern–Schneider on one table.
4. **Rung read-offs** — ``is_safety`` / ``is_cosafety`` hold exactly on the
   fixpoints; hulls and their Boolean combinations are obligations
   (`is_obligation`).
5. **Metamorphic HOA replay** — against the paired deterministic HOA
   (``…/det/<base>.hoa`` when the input sits in a corpus ``sos/`` folder):
   for every lasso with ``|u|, |v|`` up to the exhaustive bound, `member` of
   ``safety_closure(P)`` equals prefix-liveness of the lasso on the automaton,
   where a prefix is live iff the state it reaches has a nonempty language
   (per-state emptiness, Spot). Skipped with a note when no HOA is paired.

Single input; ends SUCCESS.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from sosl.sos import Lasso, load_invariant
from sosl.sos.calculus import (
    PairSet,
    Table,
    complement,
    interior,
    intersection,
    is_cosafety,
    is_obligation,
    is_safety,
    is_saturated,
    live,
    liveness_part,
    member,
    safety_closure,
    union,
    xor,
)

from tests.calculus.laws import lassos, random_languages, replay_bound


def check_closure_laws(table: Table, langs: Sequence[PairSet]) -> None:
    """Gate 1: closure-operator laws and the saturation of every output."""
    for p in langs:
        hull = safety_closure(table, p)
        inner = interior(table, p)
        assert p <= hull, "safety_closure is not extensive"
        assert inner <= p, "interior is not contractive"
        assert safety_closure(table, hull) == hull, "safety_closure not idempotent"
        assert interior(table, inner) == inner, "interior not idempotent"
        for out in (hull, inner, liveness_part(table, p)):
            assert is_saturated(table, out), "hull emitted a non-language"
        for q in langs:
            meet, join = intersection(table, p, q), union(table, p, q)
            assert safety_closure(table, meet) <= safety_closure(table, p), (
                "safety_closure is not monotone"
            )
            assert safety_closure(table, p) <= safety_closure(table, join), (
                "safety_closure is not monotone"
            )
    print(f"  1. closure laws: {len(langs)} languages, "
          f"{len(langs)}^2 monotonicity pairs, outputs saturated")


def check_duality(table: Table, langs: Sequence[PairSet]) -> None:
    """Gate 2: the interior is the complement-conjugate of the closure."""
    for p in langs:
        assert interior(table, p) == complement(
            table, safety_closure(table, complement(table, p))
        ), "interior != ~cl(~P)"
    print(f"  2. duality: interior == complement . safety_closure . complement "
          f"on {len(langs)} languages")


def check_decomposition(table: Table, langs: Sequence[PairSet]) -> None:
    """Gate 3: Alpern–Schneider — P is its closure meet its liveness part, and
    the liveness part is live everywhere."""
    every = frozenset(range(table.n))
    for p in langs:
        lively = liveness_part(table, p)
        assert p == intersection(table, safety_closure(table, p), lively), (
            "P != cl(P) & liveness_part(P)"
        )
        assert live(table, lively) == every, (
            "liveness_part has a dead class — its closure is not universal"
        )
    print(f"  3. decomposition: safety * liveness factoring on {len(langs)} languages")


def check_rungs(table: Table, langs: Sequence[PairSet]) -> None:
    """Gate 4: the fixpoint read-offs, and hull combinations are obligations."""
    hulls: List[PairSet] = []
    for p in langs:
        hull, inner = safety_closure(table, p), interior(table, p)
        hulls.append(hull)
        assert is_safety(table, hull), "a closure is not a safety property"
        assert is_cosafety(table, inner), "an interior is not co-safety"
        assert is_safety(table, p) == (p == hull), "is_safety read-off"
        assert is_cosafety(table, p) == (p == inner), "is_cosafety read-off"
        assert is_obligation(table, hull), "a safety property is not an obligation"
        assert is_obligation(table, complement(table, hull)), (
            "a co-safety complement is not an obligation"
        )
    combos = 0
    for h in hulls:
        for k in hulls:
            assert is_obligation(table, xor(table, h, k)), (
                "a Boolean combination of closed sets is not an obligation"
            )
            combos += 1
    print(f"  4. rung read-offs: fixpoints exact, {combos} hull combinations "
          f"are obligations")


def _paired_hoa(path: Path) -> Optional[Path]:
    """The corpus companion ``…/det/<base>.hoa`` of a ``…/sos/<base>.sos``."""
    candidate = path.parent.parent / "det" / (path.stem + ".hoa")
    return candidate if candidate.exists() else None


def check_hoa_replay(table: Table, pairs: PairSet, hoa: Path, bound: int) -> None:
    """Gate 5: `member` of the safety closure vs prefix-liveness on the paired
    deterministic automaton, exhaustively over bounded lassos."""
    from sosl.teacher.whitebox import HoaTeacher

    det = HoaTeacher.of_hoa(str(hoa))
    assert det.alphabet == table.alphabet, "paired HOA is over another alphabet"
    aut = det.aut
    saved = aut.get_init_state_number()
    nonempty: List[bool] = []
    for q in range(aut.num_states()):
        aut.set_init_state(q)
        nonempty.append(not aut.is_empty())
    aut.set_init_state(saved)

    def prefix_live(lasso: Lasso) -> bool:
        q = det.init
        if not nonempty[q]:
            return False
        for a in lasso.stem:
            q = det._dst[a][q]
            if not nonempty[q]:
                return False
        seen = set()
        pos = 0
        while (q, pos) not in seen:
            seen.add((q, pos))
            q = det._dst[lasso.loop[pos]][q]
            if not nonempty[q]:
                return False
            pos = (pos + 1) % len(lasso.loop)
        return True

    hull = safety_closure(table, pairs)
    count = 0
    for lasso in lassos(table.alphabet, bound):
        assert member(table, hull, lasso) == prefix_live(lasso), (
            f"safety_closure disagrees with automaton prefix-liveness on {lasso}"
        )
        count += 1
    print(f"  5. HOA replay: {count} lassos (|u|,|v| <= {bound}), "
          f"{aut.num_states()} states, closure == prefix-liveness")


def main(argv: List[str]) -> int:
    path = Path(argv[1])
    seed = int(argv[2]) if len(argv) > 2 else 0
    rng = random.Random(seed)
    inv = load_invariant(path.read_text())
    table = Table.of(inv)
    langs = random_languages(table, rng) + [inv.accept]
    print(f"{path.name}: |C| = {table.n}, |linked| = {len(table.linked)}, seed {seed}")

    check_closure_laws(table, langs)
    check_duality(table, langs)
    check_decomposition(table, langs)
    check_rungs(table, langs)
    hoa = _paired_hoa(path)
    if hoa is None:
        print("  5. HOA replay: no paired det HOA; skipped")
    else:
        check_hoa_replay(table, inv.accept, hoa, replay_bound(table.alphabet))
    print("SUCCESS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
