"""The tool: `python3 -m sosl.sos.giventhat NEG_PHI.sos K.sos [-o B.sos]`.

Two `.sos` invariants in — the complement of the property and the prior
knowledge — one smaller `.sos` out. Loads through `sosl.sos.io`, adapts the two
alphabets to their union (Spot keeps only the APs a formula mentions, so `K` may
know fewer), builds the interval (GT1), runs the greedy (GT4), and prints the
reference-point table. On SETTLED / REFUTED the model-checking question is
already answered: the minimal witness lasso is printed and no `.sos` is emitted.

Thin by contract: argv, load, adapt, call, print, dump. The math lives in
`simplify.py`; see README.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from ..alphabet import Alphabet, Letter
from ..calculus import Table, inverse_substitution, reduce
from ..invariant import Invariant
from ..io import dump_invariant, load_invariant
from .interval import given_that
from .simplify import Options, Simplification, simplify


def _extend(inv: Invariant, alphabet: Alphabet) -> Invariant:
    """`inv` reinterpreted over the (larger) `alphabet`, new letters mapping by
    dropping the APs `inv` does not know, canonically reduced — the sanctioned
    alphabet adapter (`inverse_substitution` + `reduce`), never a hand-pad."""
    if inv.alphabet.aps == alphabet.aps:
        return inv
    table = Table.of(inv)
    keep = set(inv.alphabet.aps)

    def pi(a: Letter) -> Letter:
        return inv.alphabet.letter_of(
            [ap for ap in alphabet.true_aps(a) if ap in keep])

    t2, moved = inverse_substitution(table, inv.accept, alphabet, pi)
    return reduce(t2, moved)


def _print_report(sm: Simplification) -> None:
    """The reference-point table of spec §6.6 to stdout."""
    if sm.verdict in ("SETTLED", "REFUTED"):
        verb = "settles" if sm.verdict == "SETTLED" else "refutes"
        print(f"{sm.verdict}: K {verb} the property — no B emitted.")
        if sm.witness is not None:
            w = sm.witness
            print(f"  minimal witness: {w.stem!r}.{w.loop!r}^ω")
        return

    c = sm.classes
    print(f"SIMPLIFIED via {sm.seed} seed ({sm.side}); freedom |F| = {sm.bits} bits")
    print(f"  {'¬φ  (input)':<16} |𝒞| = {c['neg_phi']}")
    print(f"  {'K':<16} |𝒞| = {c['k']}")
    print(f"  {'T  (product)':<16} |𝒞| = {c['table']}")
    print(f"  {'P_min = min|K':<16} |𝒞| = {c['p_min']}   [DPT25] reference")
    print(f"  {'P_max = max|K':<16} |𝒞| = {c['p_max']}   [DPT25] reference")
    print(f"  {'B  (result)':<16} |𝒞| = {c['b']}   <-- emitted")
    floor = min(c['neg_phi'], c['p_min'], c['p_max'])
    verdict = "beats all references" if c['b'] < floor else \
              ("ties best reference" if c['b'] == floor else "WORSE than a reference (!)")
    print(f"  rung:    {sm.rung[0]} -> {sm.rung[1]}")
    print(f"  stutter: {sm.stutter[0]} -> {sm.stutter[1]}   (∃ stutter-inv B: {sm.stutter_verdict})")
    print(f"  => B {verdict} (best reference {floor})")


def _json_report(sm: Simplification) -> dict:
    return {
        "verdict": sm.verdict,
        "seed": sm.seed,
        "side": sm.side,
        "bits": sm.bits,
        "classes": sm.classes,
        "rung": list(sm.rung),
        "stutter": list(sm.stutter),
        "stutter_verdict": sm.stutter_verdict,
        "witness": (None if sm.witness is None
                    else {"stem": sm.witness.stem, "loop": sm.witness.loop}),
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python3 -m sosl.sos.giventhat",
        description="simplify(I(¬φ), I(K)) -> a smaller legal I(B)")
    ap.add_argument("neg_phi", help="the property complement, as a .sos file")
    ap.add_argument("k", help="the prior knowledge, as a .sos file")
    ap.add_argument("-o", "--out", help="write the simplified B to this .sos")
    ap.add_argument("--no-stutter", action="store_true",
                    help="drop the stutter congruence seed")
    ap.add_argument("--require", default=None,
                    help="constrain B to a rung: safety|obligation|recurrence|stutter")
    ap.add_argument("--json", help="write a machine report to this JSON file")
    args = ap.parse_args(argv)

    neg_phi = load_invariant(open(args.neg_phi).read())
    k = load_invariant(open(args.k).read())

    union = Alphabet.of(tuple(sorted(set(neg_phi.alphabet.aps) | set(k.alphabet.aps))))
    neg_phi = _extend(neg_phi, union)
    k = _extend(k, union)

    iv = given_that(neg_phi, k)
    try:
        sm = simplify(iv, Options(stutter=not args.no_stutter, require=args.require))
    except NotImplementedError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    _print_report(sm)

    if sm.invariant is not None and args.out:
        with open(args.out, "w") as fh:
            fh.write(dump_invariant(sm.invariant))
        print(f"  wrote {args.out}")
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(_json_report(sm), fh, indent=2)

    return 0


if __name__ == "__main__":
    sys.exit(main())
