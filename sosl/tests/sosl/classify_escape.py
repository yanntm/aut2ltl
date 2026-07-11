"""The escape language — the derivation's non-empty kept core (C section 4).

    python3 -m tests.sosl.classify_escape

Over `Sigma = {a, b, c, d}` the escape language `X = c*.a.K- | c*.b.K+`
(`K+`/`K-` = infinitely/finitely many `a` over `{a,b}^omega`; any `d`, or a
`c` past the leading block, is fatal) is C section 4's running example: the
smallest derivative-regime language whose kept core is non-empty — the hub's
`[c]` class survives the collapse, and the level-1 sign comes from a descent
ending at a virtual sink (`n'- = 1 > n'+ = 0`), resolving `phi = (omega+1,
sigma)` (and `(omega+1, pi)` for the complement). This exercises exactly the
branch `Fork` cannot: `Fork`'s collapse keeps no stem, the escape language's
keeps one. The four-letter alphabet is encoded on two APs (`a = p&q`,
`b = p&!q`, `c = !p&q`, `d = !p&!q`); the presentation is the four-state
Emerson-Lei automaton below (hub, one state per `K`-component, dead sink).
Prints one OK line per side, or raises on the first mismatch.
"""
from __future__ import annotations

import signal
import sys

import spot

from sosl.sos import Invariant
from sosl.sos.build.importer import canonical
from sosl.sos.classify import classify
from sosl.sos.core.quotient import invariant_of

# State 0 = hub (c-loop), 1 = K- (accept: finitely many a, Fin(0) with its
# b-loop marked 2 to demand staying alive), 2 = K+ (accept: Inf(1)), 3 = dead.
_HOA = """HOA: v1
States: 4
Start: 0
AP: 2 "p" "q"
Acceptance: 3 (Fin(0) & Inf(2)) | Inf(1)
--BODY--
State: 0
[!0&1] 0
[0&1] 1
[0&!1] 2
[!0&!1] 3
State: 1
[0&1] 1 {0}
[0&!1] 1 {2}
[!0] 3
State: 2
[0&1] 2 {1}
[0&!1] 2
[!0] 3
State: 3
[t] 3
--END--
"""


def build_escape() -> Invariant:
    """The escape language's syntactic invariant, from the four-state EL
    presentation through the canonical deterministic form."""
    return invariant_of(canonical(spot.automaton(_HOA)))


def _assert_side(inv: Invariant, sign: str, level1: tuple, side: str) -> None:
    """One side's record: the tied coordinates, one derivation level with a
    non-empty kept core, and the resolved `(omega+1, <sign>)` degree."""
    rec = classify(inv)
    coords = (rec.m_plus, rec.m_minus, rec.n_plus, rec.n_minus)
    assert coords == (1, 1, 0, 0), (side, coords)
    assert str(rec.mu) == "omega", (side, rec.mu)
    assert not rec.gamma_partial, side
    assert rec.phi == ("omega+1", sign), (side, rec.phi)
    trace = rec.witnesses["derivation"]
    assert [lv["mu"] for lv in trace] == ["omega", "1"], (side, trace)
    assert trace[1]["coords"] == level1, (side, trace[1])
    assert len(trace[1]["kept"]) >= 1, (side, trace[1])  # the hub class survives
    print(f"OK {side}: coords {coords}, kept core {trace[1]['kept']}, "
          f"phi = (omega+1, {sign})")


def main() -> int:
    signal.alarm(15)                                # self-bound (repo cap)
    inv = build_escape()
    # X: the level-1 negative descent (kept core -> accepting sink) wins.
    _assert_side(inv, "sigma", (0, 0, 0, 1), "escape")
    # Complement: the duality swap on the nose (gamma equal, sigma <-> pi).
    _assert_side(inv.complement(), "pi", (0, 0, 1, 0), "escape complement")
    return 0


if __name__ == "__main__":
    sys.exit(main())
