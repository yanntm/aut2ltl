"""How much of a fired query is still decidable by its keyed lassos? (item 12)

    python3 -m tests.sosl.exact_ref_residue <case_id> [--nosat]

The localization theorem (theory, 2026-07-09): a firing does not poison a whole
equivalence query, only the cells that *touch the split classes*. With
`Split` the reference classes carrying two or more hypothesis partners in the
aligned graph, a cell `(c, d)` is **quiet** when every class of the loop's power
orbit `{d^j}` is unsplit and so is the stabilized stem class `c·d^k` — and a
quiet cell is decided by its keyed lasso even on a non-functional graph. Only the
**residue** needs the closure.

This is the instrument that says whether building the localization is worth it:
for each fired query of a case it reports `|Split|` against `N_R` and the residue
fraction (cells that are not quiet, over all cells). A small residue means the
closure would be called on a sliver rather than on everything, which is where the
sweep's ~33 → ~0.9 cases/s collapse comes from. Nothing is built here; this only
measures.
"""
from __future__ import annotations

import sys
from statistics import median
from typing import FrozenSet, List, Optional, Tuple

from sosl.experiment.manifest import flat_canon_cases
from sosl.learn import learn
from sosl.sos import load_invariant
from sosl.sos.invariant import Invariant
from sosl.teacher import HoaTeacher
from sosl.teacher.exact_ref import NotFunctional


def _orbit(ref: Invariant, d: int, limit: int) -> List[int]:
    """``[d, d^2, ..., d^limit]`` in the reference algebra."""
    out = [d]
    for _ in range(limit - 1):
        out.append(ref.mult[out[-1]][d])
    return out


def _stabilization(partners, orbit: List[int]) -> Optional[int]:
    """The power ``k`` at which the *hypothesis* fold of the loop stabilizes,
    read off the orbit's unique partners. ``None`` if any orbit class is split
    (the fold value is then not determined by the cell)."""
    folds = []
    for c in orbit:
        hs = partners.get(c, ())
        if len(hs) != 1:
            return None
        folds.append(hs[0])
    for k in range(1, len(folds) // 2 + 1):
        if folds[2 * k - 1] == folds[k - 1]:
            return k
    return None


def residue(ref: Invariant, exc: NotFunctional) -> Tuple[int, int, float]:
    """``(quiet cells, total cells, residue fraction)`` for one fired query."""
    split: FrozenSet[int] = exc.split
    loops = [d for d in range(ref.n) if d != ref.identity]
    limit = 4 * max(len(hs) for hs in exc.partners.values()) + 2 * ref.n
    quiet = 0
    for d in loops:
        orbit = _orbit(ref, d, limit)
        if any(c in split for c in orbit):
            continue
        k = _stabilization(exc.partners, orbit)
        if k is None:
            continue
        dk = orbit[k - 1]
        for c in range(ref.n):
            if ref.mult[c][dk] not in split:
                quiet += 1
    total = ref.n * len(loops)
    return quiet, total, 1.0 - quiet / total


def main(argv: List[str]) -> int:
    case_id = argv[1]
    saturation = "--nosat" not in argv
    case = next(c for c in flat_canon_cases() if c.case_id == case_id)
    with open(case.sos, encoding="utf-8") as fh:
        ref = load_invariant(fh.read())

    teacher = HoaTeacher.of_hoa(case.hoa, eq_mode="exact", reference=ref)
    teacher.cap_escape = saturation
    learn(teacher, teacher.alphabet, saturation=saturation)

    leg = "default" if saturation else "no-saturation"
    fired = teacher.guard_firings
    print(f"{case_id} [{leg}]: reference {ref.n} classes, "
          f"{len(fired)} fired {'query' if len(fired) == 1 else 'queries'}")
    if not fired:
        print("  guard green throughout: no residue to measure")
        return 0

    fractions: List[float] = []
    for i, exc in enumerate(fired, 1):
        quiet, total, frac = residue(ref, exc)
        fractions.append(frac)
        print(f"  query {i}: |Split| = {len(exc.split)} of {exc.n_ref} classes "
              f"({exc.n_nodes} nodes); residue {total - quiet}/{total} cells "
              f"= {frac:.1%}")
    print(f"  residue fraction: min {min(fractions):.1%}, "
          f"median {median(fractions):.1%}, max {max(fractions):.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
