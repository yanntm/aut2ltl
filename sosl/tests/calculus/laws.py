"""Harness 1-4: the algebraic laws of the free fragment, on one `.sos`.

    python3 -m tests.calculus.laws PATH.sos [SEED]

1. **Boolean laws** — over random languages: double complement, De Morgan,
   ``xor = union \\ intersection``, the empty/universal identities, and
   pointwise `Val` agreement on every cell.
2. **Saturation law** — every catalog output is conjugation-closed. A violation
   convicts the operation; it is never repaired by saturating the output.
3. **Metamorphic replay** — for every operation and every lasso up to the
   exhaustive bound, `member` of the result is the Boolean combination of
   `member` of the inputs (complement flips, union ors, rooting prepends a key,
   inverse substitution maps letters).
4. **Rooting laws** — ``P_{M(c,d)} = (P_c)_d`` on class pairs, and
   ``P_[eps] = P``.

Checks quadratic in the class count are run over a **sampled** class set once
the table is large, so that one table stays inside the per-example diagnostic
budget; each line prints what it covered. Single input; ends SUCCESS.
"""
from __future__ import annotations

import random
import sys
from itertools import product
from pathlib import Path
from typing import Iterator, List, Sequence

from sosl.sos import Alphabet, Lasso, Letter, Word, load_invariant
from sosl.sos.calculus import (
    PairSet,
    Table,
    complement,
    difference,
    empty,
    intersection,
    inverse_substitution,
    is_saturated,
    member,
    rooting,
    saturate,
    union,
    universal,
    xor,
)

RANDOM_SETS = 3
"""How many random languages to draw, beyond the constants and the input's own."""

CLASS_SAMPLE = 16
"""Above this class count, quadratic class sweeps run over a random sample."""


def random_languages(table: Table, rng: random.Random) -> List[PairSet]:
    """Random *languages* (saturated pair sets), plus the two constants: a
    Boolean law is a claim about legal operands, and saturating a random draw is
    how one gets those."""
    linked = sorted(table.linked)
    out = [empty(table), universal(table)]
    for _ in range(RANDOM_SETS):
        out.append(saturate(table, frozenset(p for p in linked if rng.random() < 0.5)))
    return out


def sample_classes(table: Table, rng: random.Random) -> List[int]:
    """The classes a quadratic sweep visits: all of them on a small table, else
    a random sample (the identity always included)."""
    if table.n <= CLASS_SAMPLE:
        return list(range(table.n))
    rest = [c for c in range(table.n) if c != table.identity]
    return sorted([table.identity] + rng.sample(rest, CLASS_SAMPLE - 1))


def lassos(alphabet: Alphabet, bound: int) -> Iterator[Lasso]:
    """Every lasso with ``|stem| <= bound`` and ``1 <= |loop| <= bound``."""
    letters = alphabet.letters()
    stems: List[Word] = [w for n in range(bound + 1) for w in product(letters, repeat=n)]
    loops: List[Word] = [w for n in range(1, bound + 1)
                         for w in product(letters, repeat=n)]
    for u in stems:
        for v in loops:
            yield Lasso(u, v)


def replay_bound(alphabet: Alphabet) -> int:
    """The exhaustive lasso bound: three letters deep, dropped to two on a big
    alphabet so the sweep stays inside the diagnostic budget."""
    return 3 if alphabet.size <= 4 else 2


# --- the four checks --------------------------------------------------------


def check_boolean(table: Table, langs: Sequence[PairSet]) -> None:
    """Harness 1: set algebra on every pair of languages, and `Val` agreeing
    with it pointwise on every cell."""
    cells = list(table.cells())
    for p in langs:
        assert complement(table, complement(table, p)) == p, "double complement"
        assert union(table, p, empty(table)) == p, "union with empty"
        assert intersection(table, p, universal(table)) == p, "meet with universal"
        cp = complement(table, p)
        for q in langs:
            cq = complement(table, q)
            u, i = union(table, p, q), intersection(table, p, q)
            assert complement(table, u) == intersection(table, cp, cq), "De Morgan"
            assert complement(table, i) == union(table, cp, cq), "De Morgan"
            assert xor(table, p, q) == difference(table, u, i), "xor"
            assert difference(table, p, q) == intersection(table, p, cq), "difference"
            for c, d in cells:
                vp, vq = table.val(p, c, d), table.val(q, c, d)
                assert table.val(cp, c, d) == (not vp), "Val vs complement"
                assert table.val(u, c, d) == (vp or vq), "Val vs union"
                assert table.val(i, c, d) == (vp and vq), "Val vs intersection"
                assert table.val(xor(table, p, q), c, d) == (vp != vq), "Val vs xor"
    print(f"  1. boolean laws: {len(langs)}^2 language pairs x {len(cells)} cells")


def check_saturation(table: Table, langs: Sequence[PairSet], classes: Sequence[int]) -> None:
    """Harness 2: every catalog output is a language (conjugation-closed)."""
    outputs = 0
    for p in langs:
        for out in (complement(table, p), *(rooting(table, p, c) for c in classes)):
            assert is_saturated(table, out), "operation emitted a non-language"
            outputs += 1
        for q in langs:
            for out in (union(table, p, q), intersection(table, p, q),
                        difference(table, p, q), xor(table, p, q)):
                assert is_saturated(table, out), "operation emitted a non-language"
                outputs += 1
    print(f"  2. saturation law: {outputs} operation outputs conjugation-closed "
          f"({len(classes)} rooting classes)")


def check_metamorphic(
    table: Table, langs: Sequence[PairSet], classes: Sequence[int], bound: int
) -> None:
    """Harness 3: the membership of an operation's result is the operation on
    the memberships of its inputs. Exhaustive over lassos up to ``bound``."""
    words = list(lassos(table.alphabet, bound))
    p, q = langs[2], langs[3]
    cp, u, i, x = (complement(table, p), union(table, p, q),
                   intersection(table, p, q), xor(table, p, q))
    roots = {c: rooting(table, p, c) for c in classes}
    for lasso in words:
        mp, mq = member(table, p, lasso), member(table, q, lasso)
        assert member(table, cp, lasso) == (not mp), "member vs complement"
        assert member(table, u, lasso) == (mp or mq), "member vs union"
        assert member(table, i, lasso) == (mp and mq), "member vs intersection"
        assert member(table, x, lasso) == (mp != mq), "member vs xor"
        for c, pc in roots.items():
            shifted = Lasso(table.keys[c] + lasso.stem, lasso.loop)
            assert member(table, pc, lasso) == member(table, p, shifted), "rooting"
    print(f"  3. metamorphic replay: {len(words)} lassos (|u|,|v| <= {bound}) "
          f"x {len(roots)} rooting classes")
    _check_substitution(table, p, bound)


def _check_substitution(table: Table, pairs: PairSet, bound: int) -> None:
    """Harness 3, the alphabet move: ``w in pi^{-1}(L)`` iff ``pi(w) in L``."""
    ab = table.alphabet
    maps = {"identity": lambda a: a, "collapse": lambda a: Letter(0)}
    if ab.size >= 2:
        maps["swap01"] = lambda a: Letter(a ^ 1) if a < 2 else a
    for name, pi in maps.items():
        sub_table, sub_pairs = inverse_substitution(table, pairs, ab, pi)
        for lasso in lassos(ab, bound):
            image = Lasso(tuple(pi(a) for a in lasso.stem),
                          tuple(pi(a) for a in lasso.loop))
            assert member(sub_table, sub_pairs, lasso) == member(table, pairs, image), (
                f"inverse_substitution/{name} disagrees on {lasso}"
            )
        assert is_saturated(sub_table, sub_pairs), f"{name}: output not a language"
    print(f"  3. inverse substitution: {len(maps)} maps ({', '.join(maps)})")


def check_rooting(table: Table, langs: Sequence[PairSet], classes: Sequence[int]) -> None:
    """Harness 4: the action laws of the left quotient."""
    for p in langs:
        assert rooting(table, p, table.identity) == p, "P_[eps] != P"
        for c in classes:
            pc = rooting(table, p, c)
            for d in classes:
                assert rooting(table, p, table.mult[c][d]) == rooting(table, pc, d), (
                    f"action law fails at ({c}, {d})"
                )
    print(f"  4. rooting laws: {len(classes)}^2 class pairs x {len(langs)} languages")


def main(argv: List[str]) -> int:
    path = Path(argv[1])
    seed = int(argv[2]) if len(argv) > 2 else 0
    rng = random.Random(seed)
    inv = load_invariant(path.read_text())
    table = Table.of(inv)
    langs = random_languages(table, rng) + [inv.accept]
    classes = sample_classes(table, rng)
    scope = "all" if len(classes) == table.n else f"{len(classes)} sampled"
    print(f"{path.name}: |C| = {table.n}, |linked| = {len(table.linked)}, "
          f"seed {seed}, classes {scope}")

    check_boolean(table, langs)
    check_saturation(table, langs, classes)
    check_metamorphic(table, langs, classes, replay_bound(table.alphabet))
    check_rooting(table, langs, classes)
    print("SUCCESS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
