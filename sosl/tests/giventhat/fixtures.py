"""The given-that fixture pair (spec §3.5): two DELAs over the single AP `p`,
with letters `a := p` and `b := !p`.

- `D_ab` — `L = {(ab)^w}`: the paper's six-class language (`[eps]`, four
  alternating classes by first/last letter, junk).
- `D_K`  — `L = {(ab)^w, (ba)^w}`: "the system alternates, in one of the two
  phases".

`build()` writes the hand-coded HOAs under `logs/fixtures/tgba/gtfix/`, carries
them through `genaut/gen/canonize.py` (default flags; `--out` redirected under
`logs/fixtures/`), and returns the four cached paths (`.sos` + det `.hoa` per
language). Rebuild is skipped when all four outputs exist; `--force` rebuilds.

Run as a module to build and check the spec's expected facts:

    cd sosl && python3 -m tests.giventhat.fixtures [--force]

Asserted: `|C(D_ab)| == 6` (paper §5.2 hand count; a mismatch is a spec §8/E1
escalation, not something to patch). `|C(D_K)|` is printed as a datum.
"""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[2]
_FIX = _HERE / "logs" / "fixtures"
_CANONIZE = _REPO / "genaut" / "gen" / "canonize.py"
_TAG = "gtfix"

# `a := p` is `[0]`, `b := !p` is `[!0]`. Both automata are deterministic and
# complete, transition-based Buchi (Inf(0)), with an explicit rejecting sink.

_D_AB_HOA = """\
HOA: v1
name: "D_ab: {(ab)^w}"
States: 3
Start: 0
AP: 1 "p"
acc-name: Buchi
Acceptance: 1 Inf(0)
properties: trans-labels explicit-labels trans-acc deterministic complete
--BODY--
State: 0
[0] 1
[!0] 2
State: 1
[!0] 0 {0}
[0] 2
State: 2
[t] 2
--END--
"""

_D_K_HOA = """\
HOA: v1
name: "D_K: {(ab)^w, (ba)^w}"
States: 6
Start: 0
AP: 1 "p"
acc-name: Buchi
Acceptance: 1 Inf(0)
properties: trans-labels explicit-labels trans-acc deterministic complete
--BODY--
State: 0
[0] 1
[!0] 3
State: 1
[!0] 2 {0}
[0] 5
State: 2
[0] 1
[!0] 5
State: 3
[0] 4 {0}
[!0] 5
State: 4
[!0] 3
[0] 5
State: 5
[t] 5
--END--
"""


@dataclass(frozen=True)
class FixturePair:
    """The four canonized artifacts of the spec §3.5 pair."""

    sos_ab: Path
    sos_k: Path
    det_ab: Path
    det_k: Path

    def paths(self) -> List[Path]:
        return [self.sos_ab, self.sos_k, self.det_ab, self.det_k]


def _pair() -> FixturePair:
    out = _FIX / "out"
    return FixturePair(
        sos_ab=out / "sos" / _TAG / "d_ab.sos",
        sos_k=out / "sos" / _TAG / "d_k.sos",
        det_ab=out / "det" / _TAG / "d_ab.hoa",
        det_k=out / "det" / _TAG / "d_k.hoa",
    )


def build(force: bool = False) -> FixturePair:
    """Build (or reuse) the canonized fixture pair and return its paths."""
    pair = _pair()
    if not force and all(p.exists() for p in pair.paths()):
        return pair
    src = _FIX / "tgba" / _TAG
    src.mkdir(parents=True, exist_ok=True)
    (src / "d_ab.hoa").write_text(_D_AB_HOA)
    (src / "d_k.hoa").write_text(_D_K_HOA)
    subprocess.run(
        [sys.executable, str(_CANONIZE), _TAG,
         "--in", str(src), "--out", str(_FIX / "out")],
        check=True, timeout=120, cwd=str(_REPO),
    )
    missing = [p for p in pair.paths() if not p.exists()]
    assert not missing, f"canonize did not produce: {missing}"
    return pair


# --- the GT2 worked-example fixture (spec §4 gate 5, paper §4.6) --------------

_GT2_TAG = "gt2fix"
_GT2_FORMULAS = {
    "negphi": "F(a & c) | (GFb & GF!b)",
    "k": "FGb & Gc",
    "ref_open": "F(a | !c)",   # the co-safety kernel's reduce target
    "ref_least": "F(a & c)",   # the least co-safety member's reduce target
}


@dataclass(frozen=True)
class Gt2Fixture:
    """The canonized artifacts of the paper §4.6 worked example, by name
    (`negphi`, `k`, `ref_open`, `ref_least`). APs are per formula (Spot keeps
    only the mentioned ones); gates extend to the common alphabet through
    `inverse_substitution` + `reduce`."""

    sos: Dict[str, Path]
    det: Dict[str, Path]

    def paths(self) -> List[Path]:
        return [*self.sos.values(), *self.det.values()]


def _gt2_fixture() -> Gt2Fixture:
    out = _FIX / "out"
    return Gt2Fixture(
        sos={n: out / "sos" / _GT2_TAG / f"{n}.sos" for n in _GT2_FORMULAS},
        det={n: out / "det" / _GT2_TAG / f"{n}.hoa" for n in _GT2_FORMULAS},
    )


def build_gt2(force: bool = False) -> Gt2Fixture:
    """Build (or reuse) the §4.6 fixture: `ltl2tgba` each formula (bounded),
    then canonize the tag folder. Same cache discipline as `build`."""
    fx = _gt2_fixture()
    if not force and all(p.exists() for p in fx.paths()):
        return fx
    src = _FIX / "tgba" / _GT2_TAG
    src.mkdir(parents=True, exist_ok=True)
    for name, formula in _GT2_FORMULAS.items():
        hoa = subprocess.run(
            ["ltl2tgba", "-D", formula],
            check=True, timeout=60, capture_output=True, text=True,
        ).stdout
        (src / f"{name}.hoa").write_text(hoa)
    subprocess.run(
        [sys.executable, str(_CANONIZE), _GT2_TAG,
         "--in", str(src), "--out", str(_FIX / "out")],
        check=True, timeout=120, cwd=str(_REPO),
    )
    missing = [p for p in fx.paths() if not p.exists()]
    assert not missing, f"canonize did not produce: {missing}"
    return fx


def main(argv: List[str]) -> int:
    pair = build(force="--force" in argv)
    from sosl.sos import load_invariant

    inv_ab = load_invariant(pair.sos_ab.read_text())
    inv_k = load_invariant(pair.sos_k.read_text())
    print(f"D_ab: |C| = {inv_ab.n}  ({pair.sos_ab})")
    print(f"D_K : |C| = {inv_k.n}  ({pair.sos_k})")
    assert inv_ab.n == 6, (
        f"|C(D_ab)| = {inv_ab.n} != 6 — spec §8/E1: suspect the HOA encoding, "
        "then canonize, then the paper's §5.2 hand count; report, do not patch")
    print("OK: |C(D_ab)| == 6 (paper §5.2); |C(D_K)| recorded as a datum")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
