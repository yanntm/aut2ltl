#!/usr/bin/env python3
"""Replay an EXTRACTED witness through the membership certificate checker.

Pull (v, p) from `extract_witness` on the counter example, supply the canonical
phase tail x = (!a)^w (stage-2 x not built yet), and check that u.v^n.x toggles
membership on the INPUT automaton, via the suggestive membership tier of the
certificate verifier. Closes the loop GAP-witness -> letters -> input automaton.

    python3 -m tests.probes.witness.replay_certificate
"""
import spot

from aut2ltl.language import Language
from aut2ltl.bls.definability.witness import extract_witness
from tests.probes.certificate.verify_smoke import verify_suggestive

PARITY = "samples/fixtures/hoa/various/parity_a.hoa"


def main() -> int:
    aut = spot.automaton(PARITY)
    w = extract_witness(Language.of(aut))
    if w is None:
        print("no witness extracted")
        return 1
    print(f"witness   : p={w.p}  v={w.v_str()}")

    # x is the canonical phase-discriminating tail until stage 2 synthesises it.
    ok, pattern = verify_suggestive(aut, u=[], v=w.v, x_prefix=[], x_cycle=["!a"], p=w.p)
    marks = "".join("1" if b else "0" for b in pattern)
    print(f"u.v^n.x   : pattern={marks} (n=0..2p)  -> {'ACCEPT' if ok else 'REJECT'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
