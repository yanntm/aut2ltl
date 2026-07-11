"""E1 covariate pass — the two §4.2 columns the census driver does not
carry: constant/shared slots and mark upward-closure. Pure explicit
Python over the digest (no engine, no libDDD — safe in one process):
EM¹ is closed by BFS over letter maps, so the pass only fits instances
the census completed (it skips rows without an `em1` and self-checks
its element count against the census column — a mismatch is
stop-the-line, the census em1 is a model count of the same set).

Per completed instance, with `val_u(q) = (δ_u(q), M_u(q))` the slot-q
value of element `u` (destination + accumulated marks; identity =
`(q, ∅)`):

- `const_slots`  — #states q whose value set `{val_u(q) : u ∈ EM¹}` is
  a singleton (the paper's constant-slot source, completion sinks);
- `distinct_cells` — `Σ_q |{val_u(q) : u}|` (explicit cells after
  per-slot sharing; the shared-slot source, to correlate with nodes);
- `upclosed_pairs` / `mark_pairs` — over (q, q′) with
  `F = {M : val_u(q) = (q′, M) for some u}` non-empty, how many have F
  upward-closed inside `2^marks` (the monotone-marks source; the paper
  leaves the metric ⟨TBD⟩ — this operationalization is flagged to
  Theory in the report).

Usage: e1_covariates.py <name> [...] | --all  (rows with an em1 in
tests/sos_sdd/logs/e1/census.csv). Appends to
logs/e1/covariates.csv, resume by name-skip like the census driver."""

import csv
import sys
from pathlib import Path
from typing import Dict, FrozenSet, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import spot  # noqa: E402

from sos_sdd.hoa import digest_twa  # noqa: E402
from sos_sdd.model import Automaton  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
CORPUS_DET = REPO / "genaut" / "corpus" / "flat_canon" / "det"
OUT = Path(__file__).resolve().parent / "logs" / "e1"

FIELDS = ["name", "em1_check", "const_slots", "states", "distinct_cells",
          "cells", "upclosed_pairs", "mark_pairs"]

Val = Tuple[int, FrozenSet[int]]      # (destination state, marks seen)
Elem = Tuple[Val, ...]                # one value per slot/state


def letter_maps(aut: Automaton) -> List[Elem]:
    """One element per concrete letter mask (deterministic + complete:
    exactly one transition matches each (state, mask))."""

    def matches(cube: str, mask: int) -> bool:
        if cube == "1":
            return True
        for lit in cube.split("&"):
            neg = lit.startswith("!")
            bit = bool(mask & (1 << aut.ap.index(lit.lstrip("!"))))
            if bit == neg:
                return False
        return True

    out: List[Elem] = []
    for mask in range(1 << len(aut.ap)):
        vals: List[Val] = []
        for q in range(aut.states):
            t = next(t for t in aut.trans if t.src == q and matches(t.cube, mask))
            vals.append((t.dst, frozenset(t.marks)))
        out.append(tuple(vals))
    return out


def close_em1(aut: Automaton) -> List[Elem]:
    """EM¹ by explicit BFS from the identity under right letter action."""
    letters = letter_maps(aut)
    ident: Elem = tuple((q, frozenset()) for q in range(aut.states))
    seen = {ident}
    frontier = [ident]
    while frontier:
        nxt: List[Elem] = []
        for u in frontier:
            for a in letters:
                ua: Elem = tuple((a[dq][0], m | a[dq][1]) for dq, m in u)
                if ua not in seen:
                    seen.add(ua)
                    nxt.append(ua)
        frontier = nxt
    return list(seen)


def covariates(name: str) -> dict:
    aut = digest_twa(spot.automaton(str(CORPUS_DET / f"{name}.hoa")), name)
    em1 = close_em1(aut)
    n = aut.states
    const = cells = 0
    up = pairs = 0
    for q in range(n):
        vals = {u[q] for u in em1}
        cells += len(vals)
        const += len(vals) == 1
        by_dst: Dict[int, set] = {}
        for dst, m in vals:
            by_dst.setdefault(dst, set()).add(m)
        marks = frozenset(range(aut.marks))
        for fam in by_dst.values():
            pairs += 1
            up += all((m | {x}) in fam for m in fam for x in marks - m)
    return {"name": name, "em1_check": len(em1), "const_slots": const,
            "states": n, "distinct_cells": cells, "cells": len(em1) * n,
            "upclosed_pairs": up, "mark_pairs": pairs}


def main() -> None:
    census = OUT / "census.csv"
    with census.open() as fh:
        em1_of = {r["name"]: r["em1"] for r in csv.DictReader(fh) if r["em1"]}
    names = sorted(em1_of) if sys.argv[1:] == ["--all"] else sys.argv[1:]
    if not names:
        print(__doc__)
        return
    out = OUT / "covariates.csv"
    done: set = set()
    if out.exists():
        with out.open() as fh:
            done = {r["name"] for r in csv.DictReader(fh)}
    with out.open("a", newline="") as fh:
        w = csv.DictWriter(fh, FIELDS)
        if not done:
            w.writeheader()
        bad = 0
        for k, name in enumerate(n for n in names if n not in done):
            row = covariates(name)
            if str(row["em1_check"]) != em1_of.get(name, ""):
                bad += 1
                print(f"*** {name}: explicit |EM1| {row['em1_check']} != "
                      f"census {em1_of.get(name)} — stop-the-line")
            w.writerow(row)
            fh.flush()
            if (k + 1) % 500 == 0:
                print(f"[{k + 1}] ...")
            elif len(names) <= 10:
                print(row)
        print(f"done: em1 cross-check mismatches: {bad}")


if __name__ == "__main__":
    main()
