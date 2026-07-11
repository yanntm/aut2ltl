"""The four symmetry fixtures (spec §3.4/§6.3): build the DELAs, canonize,
cache the canonical `.sos` paths.

    python3 -m tests.symmetry.fixtures        # build all, print paths + |C|

- FIX_A  `GF a` over AP {a, b} — hand HOA canonized at {a}, then
         alphabet-EXTENDED to {a, b} in the calculus (see below).
- FIX_B  `GF a ∧ GF b`         — `ltl2tgba -D`, bounded.
- FIX_C  `a·Σ^ω` over {a}      — `ltl2tgba -D`, bounded.
- FIX_E  `{a^{2n}·b^ω}` over {a} — HAND-BUILT (not LTL, ltl2tgba cannot).

Each fixture's raw HOA goes to `logs/fixtures/hoa/<name>/fix.hoa`; one
`genaut/gen/canonize.py` run per fixture (its defaults trusted) yields
`logs/fixtures/out/<name>/sos/<name>/*.sos` — exactly one file, the cached
canonical invariant. Rebuilds are skipped when the `.sos` already exists;
delete `logs/fixtures/` to force.

FIX_A deviation from spec §3.4 (recorded in the report): the whole
canonization pipeline sheds free APs (spot label simplification +
`remove_free_aps` — flat_canon is alphabet-minimal by construction), so NO
HOA encoding of `GF a` can carry the unused `b` through it. The invariant
over {a, b} is instead produced in the calculus: `inverse_substitution`
along the projection `2^{a,b} → 2^{a}` (alphabet extension by duplication)
followed by `reduce` — the canonical `𝓘(GF a)` at alphabet {a, b}, `b`
free by construction. Same language, same three classes, exactly the
paper's Example A.
"""
from __future__ import annotations

import glob
import os
import subprocess
import sys
from typing import Dict

from sosl.sos import Alphabet, Invariant, Letter, dump_invariant, load_invariant
from sosl.sos.calculus import Table, reduce
from sosl.sos.calculus.surgery import inverse_substitution

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_FIXDIR = os.path.join(_HERE, "logs", "fixtures")

_SPOT_BUDGET_S = 10  # bounded-or-skipped; a timeout raises, never waits

# GFa over {a, b}: one state, every letter loops, a-letters marked.
_FIX_A_HOA = """\
HOA: v1
States: 1
Start: 0
AP: 2 "a" "b"
acc-name: Buchi
Acceptance: 1 Inf(0)
properties: trans-labels explicit-labels trans-acc deterministic complete
--BODY--
State: 0
[0&1] 0 {0}
[0&!1] 0 {0}
[!0&1] 0
[!0&!1] 0
--END--
"""

# EvenHead {a^{2n}·b^ω}, b := ¬a: q0 even / q1 odd / qb b-run (accepting
# loop) / D dead. Deterministic, complete, Inf(0).
_FIX_E_HOA = """\
HOA: v1
States: 4
Start: 0
AP: 1 "a"
acc-name: Buchi
Acceptance: 1 Inf(0)
properties: trans-labels explicit-labels trans-acc deterministic complete
--BODY--
State: 0
[0] 1
[!0] 2
State: 1
[0] 0
[!0] 3
State: 2
[!0] 2 {0}
[0] 3
State: 3
[t] 3
--END--
"""

_LTL_FIXTURES: Dict[str, str] = {
    "FIX_B": "GFa & GFb",
    "FIX_C": "a",
}
_HAND_FIXTURES: Dict[str, str] = {
    "FIX_A": _FIX_A_HOA,
    "FIX_E": _FIX_E_HOA,
}
NAMES = ("FIX_A", "FIX_B", "FIX_C", "FIX_E")


def _hoa_of(name: str) -> str:
    """The raw HOA text of a fixture (hand-built or a bounded ltl2tgba)."""
    if name in _HAND_FIXTURES:
        return _HAND_FIXTURES[name]
    formula = _LTL_FIXTURES[name]
    proc = subprocess.run(
        ["ltl2tgba", "-D", formula],
        capture_output=True,
        text=True,
        timeout=_SPOT_BUDGET_S,
        check=True,
    )
    return proc.stdout


def _canonize(name: str, hoa_dir: str) -> str:
    """One canonize.py run over ``hoa_dir``; returns the single `.sos` path."""
    out_root = os.path.join(_FIXDIR, "out", name)
    subprocess.run(
        [
            sys.executable,
            os.path.join(_REPO, "genaut", "gen", "canonize.py"),
            name,
            "--in",
            hoa_dir,
            "--out",
            out_root,
        ],
        cwd=_REPO,
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    hits = sorted(glob.glob(os.path.join(out_root, "sos", name, "*.sos")))
    if len(hits) != 1:
        raise RuntimeError(f"{name}: expected exactly one .sos, got {hits}")
    return hits[0]


def _extend_fix_a(base_sos: str) -> str:
    """FIX_A at alphabet {a, b}: extend the canonized 1-AP `GF a` by the free
    ``b`` (inverse substitution along the projection dropping ``b``), reduce
    back to canonical form, and cache the dump. See the module docstring for
    why this cannot go through canonize.py."""
    out = os.path.join(_FIXDIR, "out", "FIX_A", "sos_ab", "fix.sos")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    base = load_invariant(open(base_sos).read())
    ab = Alphabet.of(("a", "b"))
    # {a,b}-mask: a on bit 1, b on bit 0; {a}-mask: a on bit 0.
    table, moved = inverse_substitution(
        Table.of(base), base.accept, ab, lambda m: Letter((m >> 1) & 1)
    )
    with open(out, "w") as fh:
        fh.write(dump_invariant(reduce(table, moved)))
    return out


def fixture_paths() -> Dict[str, str]:
    """Build (if absent) and return ``{name: canonical .sos path}``."""
    paths: Dict[str, str] = {}
    for name in NAMES:
        out_root = os.path.join(_FIXDIR, "out", name)
        hits = sorted(glob.glob(os.path.join(out_root, "sos", name, "*.sos")))
        if len(hits) != 1:
            hoa_dir = os.path.join(_FIXDIR, "hoa", name)
            os.makedirs(hoa_dir, exist_ok=True)
            with open(os.path.join(hoa_dir, "fix.hoa"), "w") as fh:
                fh.write(_hoa_of(name))
            hits = [_canonize(name, hoa_dir)]
        paths[name] = hits[0]
        if name == "FIX_A":
            ext = os.path.join(out_root, "sos_ab", "fix.sos")
            if not os.path.exists(ext):
                ext = _extend_fix_a(hits[0])
            paths[name] = ext
    return paths


def load(name: str) -> Invariant:
    """The canonical invariant of one fixture."""
    return load_invariant(open(fixture_paths()[name]).read())


def main() -> None:
    for name, path in fixture_paths().items():
        inv = load_invariant(open(path).read())
        print(
            f"{name}: |C| = {inv.n}  APs = {inv.alphabet.aps}  "
            f"|P| = {len(inv.accept)}  |linked| = {len(inv.linked_pairs())}  "
            f"({os.path.relpath(path, _REPO)})"
        )


if __name__ == "__main__":
    main()
