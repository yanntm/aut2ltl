"""The E7 dual-scan + ω-blindness tiers, ventilated by Wagner degree.

    python3 -m tests.sos2ltl.e7_tiers <e7.jsonl> [<e7b.jsonl> ...] \
        [--sos-dir genaut/corpus/flat_canon/sos]

Reads the per-non-LTL-language records `e7_ledger` writes (each carries
`h5_hit`, `right_ideal`, `phase_collapse`, and the `linear`/`omega` family
rows) and places each language in its **Wagner degree** bucket (`ϕ=(γ,s)` from
its `.cat` sidecar). Per degree it reports:

  * the **dual-scan shape** — both context shapes separate / ω-only / linear-only
    (= H5, the F₂-blind stratum);
  * the **ω-blindness tier** of the H5 hits — right-ideal ⊊ phase-collapse ⊊
    P-level (the sufficient-condition hierarchy F7 + addendum);
  * the containment / sufficiency **guards** that must hold: `right ideal ⟹ PC`
    (no RI &¬PC) and `PC ⟹ H5` (no ¬H5 & PC). A violation is a stop-the-line
    bug and exits nonzero.

`flat_canon` is complement-closed and relabel-canonical, so there are no
`_parity`/relabel twins to drop — the old `--distinct` flag is gone.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List

from tests.sos2ltl.cat_sidecar import PHI_LABEL, cat_for, phi_rank

DEFAULT_SOS_DIR = "genaut/corpus/flat_canon/sos"


def _tier(r: Dict) -> str:
    if not r["h5_hit"]:
        return "non-H5"
    if r["right_ideal"]:
        return "right-ideal"
    return "phase-collapse" if r["phase_collapse"] else "P-level"


def _shape(r: Dict) -> str:
    if r["linear"] is not None and r["omega"] is not None:
        return "both"
    return "linear-only" if r["linear"] is not None else "omega-only"


def _row(label: str, c: Counter, s: Counter) -> str:
    h5 = c["right-ideal"] + c["phase-collapse"] + c["P-level"]
    return (f"  {label:16s} {sum(c.values()):6d} {s['both']:5d} "
            f"{s['omega-only']:6d} {h5:5d} "
            f"{c['right-ideal']:4d} {c['phase-collapse']:8d} {c['P-level']:8d}")


def main(argv: List[str]) -> int:
    sos_dir = DEFAULT_SOS_DIR
    if "--sos-dir" in argv:
        sos_dir = argv[argv.index("--sos-dir") + 1]
    paths = [a for a in argv if not a.startswith("--") and a != sos_dir]

    by_phi: Dict[str, Counter] = {}          # degree -> tier counts
    shape_by_phi: Dict[str, Counter] = {}    # degree -> dual-scan shape counts
    pooled_tier: Counter = Counter()
    pooled_shape: Counter = Counter()
    bug: List[str] = []
    for p in paths:
        for l in Path(p).read_text().splitlines():
            if not l:
                continue
            r = json.loads(l)
            cat = cat_for(sos_dir, r["id"])
            phi = cat.phi if cat else "?"
            by_phi.setdefault(phi, Counter())[_tier(r)] += 1
            shape_by_phi.setdefault(phi, Counter())[_shape(r)] += 1
            pooled_tier[_tier(r)] += 1
            pooled_shape[_shape(r)] += 1
            if r["right_ideal"] and not r["phase_collapse"]:
                bug.append(f"{r['id']}:RI&¬PC")
            if r["phase_collapse"] and not r["h5_hit"]:
                bug.append(f"{r['id']}:PC&¬H5")

    print("=== E7 dual-scan shape + ω-blindness tiers, non-LTL, by Wagner degree ===")
    print(f"  (H5 = linear-only = F₂-blind; tiers: right-ideal ⊊ "
          f"phase-collapse ⊊ P-level)")
    print(f"  {'ϕ=(γ,s)':16s} {'nonLTL':>6} {'both':>5} {'ω-only':>6} "
          f"{'H5':>5} {'RI':>4} {'PC-only':>8} {'P-level':>8}")
    for phi in sorted(by_phi, key=phi_rank):
        print(_row(PHI_LABEL.get(phi, phi), by_phi[phi], shape_by_phi[phi]))
    print(_row("POOLED", pooled_tier, pooled_shape))

    print(f"\n  guards: right-ideal⟹PC and PC⟹H5  ->  "
          f"{'HOLD' if not bug else 'VIOLATED ' + str(bug)}")
    return 1 if bug else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
