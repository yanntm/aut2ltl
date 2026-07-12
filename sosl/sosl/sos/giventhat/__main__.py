"""The tool: `python3 -m sosl.sos.giventhat NEG_PHI.sos K.sos [-o B.sos]`.

Two `.sos` invariants in — the complement of the property and the prior
knowledge — one smaller `.sos` out. Loads through `sosl.sos.io`, adapts the two
alphabets to their union (Spot keeps only the APs a formula mentions, so `K` may
know fewer), builds the interval (GT1), runs the greedy (GT4), and writes the
`.gtr` report (`giventhat.report`) to stdout. On SETTLED / REFUTED the
model-checking question is already answered: the witness lasso is in the report
and no `.sos` is emitted.

Thin by contract: argv, load, adapt, call, print, dump. The math lives in
`simplify.py`; see README.md.
"""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from ..alphabet import Alphabet, Letter
from ..calculus import Table, inverse_substitution, reduce
from ..invariant import Invariant
from ..io import dump_invariant, load_invariant
from .interval import given_that
from .report import dump_report
from .simplify import Options, simplify


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

    sys.stdout.write(dump_report(sm))
    if sm.invariant is not None and args.out:
        with open(args.out, "w") as fh:
            fh.write(dump_invariant(sm.invariant))

    return 0


if __name__ == "__main__":
    sys.exit(main())
