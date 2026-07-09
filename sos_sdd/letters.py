"""Letter-class refinement: the guard cubes of a digest partitioned into
letter-behavior classes. Two letters are guard-equal when they select the
same (destination, mark set) row at every state; the engine then works
per class — the class count is bounded by the digest's cube structure,
and the alphabet is never enumerated. Letters are canonically ordered by
their characteristic tuple over the AP list (absent 0 < present 1); each
class carries its least letter, which is what shortlex extraction reads."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .model import Automaton

# A cube is a partial assignment of the APs: ap index -> bool.
CubeMap = Dict[int, bool]
Bits = Tuple[int, ...]


def parse_cube(s: str, ap: Tuple[str, ...]) -> CubeMap:
    """Parse "a&!b" (or "1" for true) against the ordered AP list."""
    if s == "1":
        return {}
    cube: CubeMap = {}
    for lit in s.split("&"):
        neg = lit.startswith("!")
        name = lit[1:] if neg else lit
        try:
            idx = ap.index(name)
        except ValueError:
            raise ValueError(f"unknown AP {name!r} in cube {s!r}") from None
        if cube.get(idx) == neg:  # both polarities: empty cube
            raise ValueError(f"contradictory cube {s!r}")
        cube[idx] = not neg
    return cube


def _meet(a: CubeMap, b: CubeMap) -> Optional[CubeMap]:
    """Conjunction of two cubes, or None when contradictory."""
    out = dict(a)
    for k, v in b.items():
        if out.get(k, v) != v:
            return None
        out[k] = v
    return out


def _split(a: CubeMap, b: CubeMap, n_ap: int) -> Tuple[Optional[CubeMap], List[CubeMap]]:
    """(a ∧ b, a ∧ ¬b as disjoint cubes) — the refinement step."""
    inside = _meet(a, b)
    outside: List[CubeMap] = []
    prefix = dict(a)
    for k in sorted(b):  # AP order keeps the split canonical
        v = b[k]
        if prefix.get(k) == v:
            continue
        if prefix.get(k) == (not v):
            return inside, [dict(a)]  # a entirely outside b
        piece = dict(prefix)
        piece[k] = not v
        outside.append(piece)
        prefix[k] = v
    return inside, outside


def _count(c: CubeMap, n_ap: int) -> int:
    return 1 << (n_ap - len(c))


def _least_bits(c: CubeMap, n_ap: int) -> Bits:
    return tuple(1 if c.get(i, False) else 0 for i in range(n_ap))


def _bits_to_cube(bits: Bits, ap: Tuple[str, ...]) -> str:
    return "&".join(a if b else f"!{a}" for a, b in zip(ap, bits)) if ap else "1"


@dataclass(frozen=True)
class LetterClass:
    """One guard-equality class of letters: `least` is its lex-least
    letter as a full-valuation cube, `count` how many letters it holds,
    `dst[q]` / `marks[q]` the per-state row (marks as a bit mask), and
    `cubes` a disjoint cover of the class for later guard emission."""

    least: str
    least_bits: Bits
    count: int
    dst: Tuple[int, ...]
    marks: Tuple[int, ...]
    cubes: Tuple[str, ...]


def letter_classes(aut: Automaton) -> List[LetterClass]:
    """Refine the digest's cubes into behavior classes, sorted by least
    letter. Raises ValueError on a nondeterministic or incomplete digest
    (the engine's Phase 1 assumes one row per (state, letter))."""
    n_ap = len(aut.ap)
    parsed = [(t.src, parse_cube(t.cube, aut.ap), t.dst,
               sum(1 << m for m in t.marks)) for t in aut.trans]

    # Refine 2^AP into atoms, each inside or outside every digest cube.
    atoms: List[List[CubeMap]] = [[{}]]
    for _, cube, _, _ in parsed:
        nxt: List[List[CubeMap]] = []
        for region in atoms:
            inside: List[CubeMap] = []
            outside: List[CubeMap] = []
            for c in region:
                i, o = _split(c, cube, n_ap)
                if i is not None:
                    inside.append(i)
                outside.extend(o)
            if inside:
                nxt.append(inside)
            if outside:
                nxt.append(outside)
        atoms = nxt

    # Row signature of each atom; merge equal signatures.
    merged: Dict[Tuple[Tuple[int, int], ...], List[List[CubeMap]]] = {}
    for region in atoms:
        probe = region[0]
        sig: List[Tuple[int, int]] = []
        for q in range(aut.states):
            rows = {(dst, mk) for src, cube, dst, mk in parsed
                    if src == q and _meet(probe, cube) is not None}
            if len(rows) != 1:
                letter = _bits_to_cube(_least_bits(probe, n_ap), aut.ap)
                kind = "nondeterministic" if rows else "incomplete"
                raise ValueError(
                    f"{aut.name}: {kind} at state {q} on letter {letter}")
            sig.append(next(iter(rows)))
        merged.setdefault(tuple(sig), []).append(region)

    classes: List[LetterClass] = []
    for sig, regions in merged.items():
        cubes = [c for region in regions for c in region]
        least = min(_least_bits(c, n_ap) for c in cubes)
        classes.append(LetterClass(
            least=_bits_to_cube(least, aut.ap),
            least_bits=least,
            count=sum(_count(c, n_ap) for c in cubes),
            dst=tuple(d for d, _ in sig),
            marks=tuple(m for _, m in sig),
            cubes=tuple(_bits_to_cube(_least_bits(c, n_ap), aut.ap)
                        if len(c) == n_ap else
                        "&".join((aut.ap[k] if v else f"!{aut.ap[k]}")
                                 for k, v in sorted(c.items())) or "1"
                        for c in cubes)))
    classes.sort(key=lambda c: c.least_bits)
    assert sum(c.count for c in classes) == 1 << n_ap
    return classes
