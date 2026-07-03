"""Dump the compression tables of the root node of ONE HOA file — the display
client of `aut2ltl/bls/definability/dg/compress.py`: v0 pivot, sub-alphabet,
divisor, `T₁`/`T₂` with the ω-letters' member pairs, the `g`-images, the
`X_{n,m}` tables, `K₀` and the per-`n` `K₂` class sets (`dg/algorithm.md`
layers 4-6; expected values: the layer 12-13 walks).

Usage:  python3 tests/probes/dg_compress.py <file.hoa>

The input must be LTL-definable (aperiodic quotient); group-bearing exits 2.
"""
from __future__ import annotations

import sys
from typing import FrozenSet, Tuple

from aut2ltl.bls.definability.dg.compress import NodeData, T2Letter, compress
from aut2ltl.bls.definability.dg.frame import Frame, Target, root_frame, root_target
from dg_common import print_d_line, quotient_of_hoa


def t2_str(nd: NodeData, tl: T2Letter) -> str:
    if tl[0] == "eps":
        return "eps"
    if tl[0] == "fib":
        return f"fib{tl[1]}"
    return "om{" + " ".join(f"({s},{e})" for (s, e) in nd.fa.omega[tl[1]]) + "}"


def set_str(xs: FrozenSet[int], base: Tuple[int, ...]) -> str:
    """A set of divisor positions, shown as base element ids; '-' if empty."""
    return "{" + ",".join(str(base[p]) for p in sorted(xs)) + "}" if xs else "-"


def main(path: str) -> int:
    data = quotient_of_hoa(path)
    if data is None:
        print("closure  : blew the cap")
        return 2
    print_d_line(data)
    if data.group is not None:
        print("verdict  : NOT aperiodic -- not a dg input")
        return 2
    alg = data.alg

    frame: Frame = root_frame(alg)
    target: Target = root_target(alg, frame)
    print(f"root     : {len(frame.omega)} omega-classes, target om = "
          + " ".join(f"c{i}{{{','.join(f'({s},{e})' for (s, e) in frame.omega[i])}}}"
                     for i in sorted(target.om)))

    visible = [li for li in range(len(alg.letters))
               if frame.images[li] != frame.unit]
    if not visible:
        print("pivot    : none (all letters invisible -- base case)")
        return 0
    c: int = visible[0]
    nd: NodeData = compress(frame, target, c)

    print(f"pivot    : {alg.letters[c]!r} (letter {c}), m = {nd.m} "
          f"[{alg.key(nd.m)}];  A = {[alg.letters[li] for li in nd.A]}")
    print(f"divisor  : carrier {{{','.join(map(str, nd.div.carrier))}}}, "
          f"unit pos {nd.div.unit}   ({len(frame.mult)} -> {len(nd.div)})")
    print(f"T1       : {{{','.join(map(str, nd.t1))}}}   "
          f"(h(A+) = {{{','.join(map(str, nd.fa.gen))}}})")
    print("T2       : " + " | ".join(t2_str(nd, tl) for tl in nd.t2))
    print("g        : " + ", ".join(
        f"t1:{n} -> {nd.div.carrier[nd.g_img[i]]}" for i, n in enumerate(nd.t1))
        + f";  T2 -> {nd.div.carrier[nd.div.unit]}   (as base ids)")
    print("X[n][m]  :  rows n in T1, cols T2 (T' base ids; '-' empty)")
    for i, n in enumerate(nd.t1):
        print(f"  {n}: " + " ".join(set_str(nd.x[i][j], nd.div.carrier)
                                    for j in range(len(nd.t2))))
    k0 = ((["eps"] if nd.k0_eps else [])
          + [f"fib{f}" for f in sorted(nd.k0_fib)]
          + [f"om{i}" for i in sorted(nd.k0_om)])
    print("K0       : " + (" ".join(k0) if k0 else "-"))
    print("K2       :  fc omega-classes (pairs as T' base ids)")
    for cid, members in enumerate(nd.fc.omega):
        pairs = " ".join(f"({nd.div.carrier[s]},{nd.div.carrier[e]})"
                         for (s, e) in members)
        print(f"  c{cid}: {pairs}")
    for i, n in enumerate(nd.t1):
        print(f"  n={n}: " + ("{" + ",".join(f"c{cid}" for cid in sorted(nd.k2[i]))
                              + "}" if nd.k2[i] else "-"))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
