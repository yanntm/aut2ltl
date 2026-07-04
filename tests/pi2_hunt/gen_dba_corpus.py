"""Generate a corpus of minimal deterministic recurrence automata for the Π₂ hunt.

Two sources, both aimed at languages with "detection memory" (where a group can
hide in the transition monoid): (a) STRUCTURED templates over a small AP set --
GF/FG wrappers, nested runs GF(x & Xy), GF(x & XFy), fairness conjunctions,
booleans; (b) a RANDLTL stream over the same APs across several seeds and tree
sizes, for breadth beyond the hand-picked shapes.

Every candidate formula is translated and reduced to its SAT-min-backed minimal
deterministic form (Language.det_generic_minimal); only genuine recurrences are
kept (acceptance mentions Inf -- trivial all-accept / all-reject safety forms are
dropped) within a state bound. Survivors are deduped by their AP-normalised
minimal HOA and written one-per-file, so the corpus carries no relabel twins and
each language appears once.

Usage:  python3 tests/pi2_hunt/gen_dba_corpus.py [--aps a,b] [--out DIR]
                 [--max-states N] [--random K] [--seeds S] [--tree LO,HI]

Writes HOA into --out (default tests/pi2_hunt/corpus_3a/) and prints a summary.
"""
from __future__ import annotations

import argparse
import itertools
import os
import sys
from typing import Iterable, List, Sequence, Tuple

import spot

from aut2ltl.language import Language
from survey.normalize import normalize_hoa


def _booleans(aps: Sequence[str]) -> List[str]:
    """A small basis of boolean guards over the APs (single + a few pairs)."""
    lits = [f"{p}" for p in aps] + [f"!{p}" for p in aps]
    out: List[str] = list(lits)
    for x, y in itertools.combinations(aps, 2):
        out += [f"({x} & {y})", f"({x} & !{y})", f"(!{x} & {y})",
                f"({x} | {y})", f"({x} ^ {y})"]
    return out


def _structured(aps: Sequence[str]) -> Iterable[str]:
    """Structured recurrence templates over the APs -- the detection-memory shapes."""
    B = _booleans(aps)
    for x in B:
        yield f"GF{x}"
        yield f"FG{x}"
    for x, y in itertools.product(B, repeat=2):
        yield f"GF({x} & X{y})"
        yield f"GF({x} & XF{y})"
        yield f"G({x} -> F{y})"
        yield f"GF{x} & FG{y}"
        yield f"GF{x} & GF{y}"
        yield f"GF{x} | FG{y}"
    for x, y, z in itertools.product(B, repeat=3):
        yield f"GF({x} & X({y} & X{z}))"


def _random(aps: Sequence[str], k: int, seeds: int, tree: Tuple[int, int]) -> Iterable[str]:
    """A randltl stream over the APs across several seeds."""
    per = max(1, k // max(1, seeds))
    for s in range(1, seeds + 1):
        g = spot.randltl(list(aps), tree_size=tree, seed=s)
        for _ in range(per):
            yield str(next(g))


def _minimal_recurrence(f_str: str, max_states: int) -> "spot.twa_graph | None":
    """Minimal deterministic form of the formula, or None if it is not a genuine
    recurrence within the state bound (trivial acceptance or too large)."""
    try:
        f = spot.formula(f_str)
    except Exception:
        return None
    det = Language.of(spot.translate(f)).det_generic_minimal()
    n = det.num_states()
    if n < 2 or n > max_states:
        return None
    acc = str(det.get_acceptance())
    if "Inf" not in acc:  # drop all-accept / all-reject safety forms
        return None
    return det


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--aps", default="a,b")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus_3a"))
    ap.add_argument("--max-states", type=int, default=8)
    ap.add_argument("--random", type=int, default=4000)
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--tree", default="3,12")
    args = ap.parse_args(argv)

    aps = [s.strip() for s in args.aps.split(",") if s.strip()]
    lo, hi = (int(x) for x in args.tree.split(","))
    os.makedirs(args.out, exist_ok=True)

    seen: set = set()
    kept = 0
    considered = 0
    for f_str in itertools.chain(_structured(aps), _random(aps, args.random, args.seeds, (lo, hi))):
        considered += 1
        det = _minimal_recurrence(f_str, args.max_states)
        if det is None:
            continue
        hoa = det.to_str("hoa")
        key = normalize_hoa(hoa)
        if key in seen:
            continue
        seen.add(key)
        name = f"c3a_{kept:04d}_s{det.num_states()}"
        det.set_name(f_str)
        with open(os.path.join(args.out, f"{name}.hoa"), "w") as fh:
            fh.write(det.to_str("hoa"))
        kept += 1

    print(f"considered={considered} kept={kept} -> {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
