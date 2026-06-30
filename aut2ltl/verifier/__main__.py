#!/usr/bin/env python3
"""aut2ltl.verifier CLI — replay a non-LTL witness against an input automaton.

    python3 -m aut2ltl.verifier INPUT "NOT_LTL p=3 u=[] v=[a; a] x=[cycle{!a}]"

INPUT is a HOA automaton file or an LTL/PSL formula (auto-detected; force with
--ltl / --hoa). The witness is the serialized one-liner the front end prints on a
NOT_LTL verdict. The check samples membership of `u . v^n . x` for n = 0..2p and
reports whether it toggles with period p.

stdout carries one parseable marker line; the exit code is the verdict:
    VERIFY: ok pattern=1001001     exit 0   (toggles with period p)
    VERIFY: fail pattern=1111111   exit 1   (constant / wrong period -- bad certificate)
    VERIFY: no-witness             exit 2   (the family is incomplete -- nothing to replay)
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional

import spot

from aut2ltl.witness import Witness
from aut2ltl.verifier.check import verify

_FILE_EXTS = (".hoa", ".aut", ".hoaf")


def _load_aut(inp: str, *, force_ltl: bool, force_hoa: bool) -> "spot.twa_graph":
    """Auto-detect HOA-file vs LTL/PSL string (same rule as the front end) and
    return an automaton: a HOA file is loaded as-is; a formula is translated."""
    is_file = force_hoa or (
        not force_ltl and (os.path.exists(inp) or inp.lower().endswith(_FILE_EXTS))
    )
    if is_file:
        return spot.automaton(inp)
    return spot.formula(inp).translate()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="aut2ltl.verifier",
        description="Replay a non-LTL witness against an input automaton by "
                    "membership and report whether it toggles with its period.",
    )
    p.add_argument("input", help="a HOA automaton file or an LTL/PSL formula")
    p.add_argument("witness", help="the serialized witness line "
                                   "(e.g. 'NOT_LTL p=3 u=[] v=[a; a] x=[cycle{!a}]')")
    p.add_argument("--ltl", action="store_true", help="force INPUT as an LTL formula")
    p.add_argument("--hoa", action="store_true", help="force INPUT as a HOA file path")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        w = Witness.parse(args.witness)
        aut = _load_aut(args.input, force_ltl=args.ltl, force_hoa=args.hoa)
    except (ValueError, RuntimeError) as e:
        print(f"aut2ltl.verifier: {e}", file=sys.stderr)
        return 2

    ok, pattern = verify(aut, w)
    if ok is None:
        print("VERIFY: no-witness")
        return 2
    marks = "".join("1" if b else "0" for b in pattern)
    print(f"VERIFY: {'ok' if ok else 'fail'} pattern={marks}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
