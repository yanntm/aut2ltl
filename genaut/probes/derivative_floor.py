"""Construct a derivative-regime inhabitant of `3state1ap2acc_parity` directly.

    python3 genaut/probes/derivative_floor.py

The derivative regime `m >= 1 & n+ = n-` has its sharp floor at three states
and two parity colours (sos_classification.md §7), yet uniform sampling of the
`3state1ap2acc_parity` id space (max-even parity, the census family) finds no
inhabitant. This probe *constructs* one: a routing state whose two letters
enter two absorbing one-state basins — under `parity max even 2` (accept iff
`Fin(1) & Inf(0)`) the `a`-basin marks `a`-steps `{0}` and `!a`-steps `{1}`
(accepts `FG a`: a positive chain), the `!a`-basin marks `!a`-steps `{0}`
(accepts `GF !a`: a negative chain), the basins are mutually unreachable —
so the language is `(a & FGa) | (!a & GF!a)`, the polarity flip of `Fork`.
The probe encodes the combo, recovers its generator id, runs the census chain
on it, asserts the classifier lands PARTIAL at coordinates `(1, 1, 0, 0)`, and
checks the language equals `Fork` up to AP relabeling (the `canon_key` fold).
Prints the id — a concrete regime witness in the shape's id space.
"""
from __future__ import annotations

import os
import signal
import sys
from typing import Dict, Tuple

_GEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "gen")
sys.path.insert(0, os.path.normpath(_GEN))

import spot                                              # noqa: E402

from build import build_aut, reduce_aut                  # noqa: E402
from sample import canon_key, combo_of                   # noqa: E402
from shape import Markset, Shape                         # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
for p in (os.path.join(_REPO, "sosl"), _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

from sosl.sos.build.importer import canonical            # noqa: E402
from sosl.sos.classify import classify                   # noqa: E402
from sosl.sos.core.quotient import invariant_of          # noqa: E402

FORK = "(a & GFa) | (!a & FG!a)"
# guard codes for k=1 (shape.guard_alphabet): 0 absent, 1 !a, 2 a, 3 true
_A, _NOT_A = 2, 1
# (src, dst, markset) -> guard: the three-state construction above
EDGES: Dict[Tuple[int, int, Markset], int] = {
    (0, 1, ()): _A,          # route: first letter a  -> basin q1
    (0, 2, ()): _NOT_A,      # route: first letter !a -> basin q2
    (1, 1, (0,)): _A,        # q1: a-loop {0} }  Fin(1) & Inf(0) = FG a
    (1, 1, (1,)): _NOT_A,    # q1: !a-loop {1} }  (positive chain)
    (2, 2, ()): _A,          # q2: a-loop  {} }  Inf(0) = GF !a
    (2, 2, (0,)): _NOT_A,    # q2: !a-loop {0} }  (negative chain)
}


def main() -> int:
    signal.alarm(15)
    shape = Shape(3, 1, 2, "parity")
    combo = tuple(EDGES.get(slot, 0) for slot in shape.slots)
    ident = 0                                 # slots big-endian, base |guards|
    for g in combo:
        ident = ident * len(shape.guards) + g
    assert combo_of(shape, ident) == combo, "id round-trip"
    print(f"combo id = {ident}  ({shape.tag}, id-space {shape.num_combos})")

    D = canonical(reduce_aut(build_aut(shape, combo, spot.make_bdd_dict())))
    rec = classify(invariant_of(D))
    coords = (rec.m_plus, rec.m_minus, rec.n_plus, rec.n_minus)
    print(f"classified: coords {coords}, mu = {rec.mu}, sign = {rec.sign}, "
          f"LTL = {rec.aperiodic}, stutter-inv = {rec.stutter_invariant}")
    assert coords == (1, 1, 0, 0), coords
    assert rec.gamma_partial and rec.sign == "PARTIAL", rec.sign

    fork = canonical(spot.translate(FORK))
    same = canon_key(D) == canon_key(fork)
    print(f"language equals Fork up to AP relabeling: {same}")
    assert same, "expected the polarity flip of Fork"
    print(f"OK: the derivative regime is inhabited at {shape.tag}, "
          f"witness id {ident}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
