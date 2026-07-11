"""The `Fork` specimen — the derivative regime, resolved (K4's fixture).

    python3 -m tests.sosl.classify_fork

`Fork = (a & GF a) | (!a & FG !a)` (C section 5) is the smallest language in
the derivative regime `m >= 1 & n+ = n-`: the one case whose degree needs
Wagner's derivative, run by `classify` as C section 8's restricted table
recursion. This probe builds Fork's invariant from the formula (Spot
translate -> canonical D -> quotient), gates the bytes against the committed
fixture `samples/fixtures/hoa/sos/fork.sos` (written on first run), and
asserts the full C section 5 record: four classes, aperiodic (LTL) and
stutter-invariant, coordinates `(1, 1, 0, 0)`, `mu = omega`, and the degree
resolved through one derivation to `phi = (omega+1, delta)` with the level
trace `omega, 1` and an empty kept core — with the same assertions on the
complement (the coordinates and the self-dual sign are fixed points of the
duality swap). The same record is asserted on the corpus-native twin
`fork_floor.sos` (the floor-shape witness, Fork up to AP relabeling) when
that fixture is present. Also smoke-tests the CLI, which must now exit 0.
Prints one OK line per check, or raises on the first mismatch.
"""
from __future__ import annotations

import os
import signal
import sys

import spot

from sosl.sos import Invariant, load_invariant
from sosl.sos.build.importer import canonical
from sosl.sos.classify import classify
from sosl.sos.classify.__main__ import main as cli_main
from sosl.sos.core.quotient import invariant_of
from sosl.sos.io.serialize import dump_invariant

FORK = "(a & GFa) | (!a & FG!a)"
_SOS = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir,
                    os.pardir, "samples", "fixtures", "hoa", "sos")
_FIXTURE = os.path.join(_SOS, "fork.sos")
_FLOOR = os.path.join(_SOS, "fork_floor.sos")


def build_fork() -> Invariant:
    """`Fork`'s syntactic invariant, from the formula through the canonical
    deterministic presentation."""
    D = canonical(spot.translate(FORK))
    return invariant_of(D)


def _gate_fixture(sos_text: str) -> str:
    """Byte-gate `sos_text` against the committed fixture (written on first
    run); returns the fixture path."""
    path = os.path.abspath(_FIXTURE)
    if os.path.isfile(path):
        with open(path) as fh:
            assert fh.read() == sos_text, "fork.sos drifted from the build"
        print(f"OK fixture byte-identical: {path}")
    else:
        with open(path, "w") as fh:
            fh.write(sos_text)
        print(f"OK fixture written: {path}")
    return path


def _assert_record(inv: Invariant, side: str) -> None:
    """The C section 5 record — derivation included — asserted on one side."""
    rec = classify(inv)
    assert rec.aperiodic, side                      # Fork is LTL-definable
    assert rec.stutter_invariant, side              # ... and X-free (all letters idempotent)
    coords = (rec.m_plus, rec.m_minus, rec.n_plus, rec.n_minus)
    assert coords == (1, 1, 0, 0), (side, coords)   # the tied case, smallest instance
    assert str(rec.mu) == "omega", (side, rec.mu)
    assert not rec.gamma_partial, side              # the derivation resolves it
    assert rec.phi == ("omega+1", "delta"), (side, rec.phi)
    assert rec.parity_length == 2 and rec.co_parity_length == 2, side
    trace = rec.witnesses["derivation"]
    assert [lv["mu"] for lv in trace] == ["omega", "1"], (side, trace)
    assert trace[1]["coords"] == (0, 0, 0, 0), (side, trace)
    assert trace[1]["kept"] == (), (side, trace)    # Fork's collapse keeps no stem
    print(f"OK {side}: coords {coords}, one derivation, phi = (omega+1, delta)")


def main() -> int:
    signal.alarm(15)                                # self-bound (repo cap)
    inv = build_fork()
    assert len(inv.keys) == 4, inv.keys             # [eps], [!a], [a], [!a.a]
    path = _gate_fixture(dump_invariant(inv))

    _assert_record(inv, "Fork")
    with open(path) as fh:
        _assert_record(load_invariant(fh.read()).complement(), "Fork complement")
    if os.path.isfile(_FLOOR):
        with open(_FLOOR) as fh:
            _assert_record(load_invariant(fh.read()), "fork_floor (floor-shape twin)")

    code = cli_main([path])
    assert code == 0, code                          # resolved: no PARTIAL exit
    print("OK cli: exit code 0 (degree resolved by derivation)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
