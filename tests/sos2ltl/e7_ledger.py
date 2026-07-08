"""E7 dual-scan certificate ledger over one census shape (language-keyed).

    python3 -m tests.sos2ltl.e7_ledger <corpus/sos/TAG> [--out <file.jsonl>]

Consumes a genaut `corpus/sos/<tag>/` folder — one `.sos` per distinct
language (§3b's unit is structural here) — and the matching
`corpus/det/<tag>/` automata (the membership acceptors). Per language:
`dual_scan` partitions LTL (aperiodic ⇒ None) from non-LTL (a `DualScan`).
For every non-LTL language it records both context scans run to completion
(the E7 datum: linear-separating / ω-separating / `all-constant` each), the
H5 read-off (ω-power all-constant ⇒ linear-only certificate), the component
lengths against the Theorem-4.4 `< |𝒞|` bound, and a presentation-agnostic
replay of each separating family against the canonical automaton `D` by
membership only (`spot_oracle`) — the verifier holds no algebra.

Writes one JSON record per non-LTL language to `--out` (default under
`tests/sos2ltl/logs/`) and prints a per-shape summary. The `det/` replay is
a stop-the-line check: a family that does not toggle against `D` is a bug.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from typing import Dict, List, Optional

from aut2ltl.sos2ltl.witness import (
    DualScan, Family, dual_scan, extract_family, omega_blind_by_right_ideal,
    toggles)
from aut2ltl.sos2ltl.witness.spot_oracle import oracle_for_hoa
from sosl.sos import load_invariant


def _family_row(fam: Optional[Family]) -> Optional[Dict[str, object]]:
    """A separating family's component lengths and period, or None for an
    all-constant shape."""
    if fam is None:
        return None
    tail = len(fam.y) if fam.omega_power else \
        len(fam.x_prefix or ()) + len(fam.x_loop or ())
    return {
        "period": fam.period, "pattern": list(fam.pattern),
        "u": len(fam.u), "v": len(fam.v), "tail": tail,
    }


def main(argv: List[str]) -> int:
    sos_dir = argv[0].rstrip("/")
    tag = os.path.basename(sos_dir)
    det_dir = sos_dir.replace("/sos/", "/det/")
    out = None
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    else:
        out = f"tests/sos2ltl/logs/e7_{tag}.jsonl"
    os.makedirs(os.path.dirname(out), exist_ok=True)

    files = sorted(f for f in os.listdir(sos_dir) if f.endswith(".sos"))
    n_lang = len(files)
    n_ltl = 0
    rows: List[Dict[str, object]] = []
    replay_fail: List[str] = []
    shape_split = {"both": 0, "linear-only": 0, "omega-only": 0}
    h5 = 0
    mech: Counter = Counter()          # (h5?, right-ideal?) cross-tab
    mech_finding: List[str] = []       # H5 & not right-ideal — a real finding
    mech_bug: List[str] = []           # non-H5 & right-ideal — stop-the-line

    for fn in files:
        stem = fn[:-4]
        with open(os.path.join(sos_dir, fn)) as f:
            inv = load_invariant(f.read())
        ds: Optional[DualScan] = dual_scan(inv)
        if ds is None:
            n_ltl += 1
            continue

        if ds.linear is not None and ds.omega is not None:
            shape_split["both"] += 1
        elif ds.linear is not None:
            shape_split["linear-only"] += 1
        else:
            shape_split["omega-only"] += 1
        if ds.h5_hit:
            h5 += 1

        # Mechanism column (Prop 4.5): every period>1 cycle a right ideal
        # ⟹ ω-blind (H5) by theorem. Cross-checked against the dual scan.
        ri = omega_blind_by_right_ideal(inv)
        mech[("h5" if ds.h5_hit else "nonh5", "ri" if ri else "nori")] += 1
        if ds.h5_hit and not ri:
            mech_finding.append(stem)      # column-false H5 — a real finding
        if not ds.h5_hit and ri:
            mech_bug.append(stem)          # column-true non-H5 — stop-the-line

        det_hoa = os.path.join(det_dir, stem + ".hoa")
        member = oracle_for_hoa(det_hoa, inv.alphabet) if os.path.exists(det_hoa) else None
        replay: Dict[str, Optional[bool]] = {}
        for name, fam in (("linear", ds.linear), ("omega", ds.omega)):
            if fam is None or member is None:
                continue
            ok = toggles(fam, member)
            replay[name] = ok
            if not ok:
                replay_fail.append(f"{stem}:{name}")

        canon = extract_family(inv)
        rows.append({
            "id": stem, "classes": inv.n,
            "linear": _family_row(ds.linear),
            "omega": _family_row(ds.omega),
            "h5_hit": ds.h5_hit,
            "right_ideal": ri,
            "canonical": "omega" if canon and canon.omega_power else "linear",
            "det_replay": replay,
        })

    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    n_nonltl = len(rows)
    max_comp = max((max(r["linear"]["u"] if r["linear"] else 0,        # type: ignore[index]
                        r["linear"]["v"] if r["linear"] else 0,        # type: ignore[index]
                        r["linear"]["tail"] if r["linear"] else 0,     # type: ignore[index]
                        r["omega"]["u"] if r["omega"] else 0,          # type: ignore[index]
                        r["omega"]["v"] if r["omega"] else 0,          # type: ignore[index]
                        r["omega"]["tail"] if r["omega"] else 0)       # type: ignore[index]
                    for r in rows), default=0)
    max_cls = max((r["classes"] for r in rows), default=0)  # type: ignore[type-var]

    print(f"E7 ledger [{tag}]: {n_lang} languages — {n_ltl} LTL, {n_nonltl} non-LTL")
    if n_nonltl:
        print(f"  dual-scan shape: {shape_split}  (H5 hits: {h5})")
        print(f"  det/ membership replay: "
              f"{'ALL REPLAYED' if not replay_fail else 'FAILURES ' + str(replay_fail)}")
        print(f"  max component length {max_comp} vs max |𝒞| {max_cls} "
              f"(Thm 4.4: each < |𝒞|)")
        # Mechanism column (Prop 4.5): right-ideal ⟺ H5, theory's prediction.
        print(f"  mechanism (right-ideal ω-blind) × H5: "
              f"H5&RI={mech[('h5','ri')]} H5&¬RI={mech[('h5','nori')]} "
              f"¬H5&RI={mech[('nonh5','ri')]} ¬H5&¬RI={mech[('nonh5','nori')]}")
        if mech_finding:
            print(f"  ** FINDING: H5 & not-right-ideal (2nd ω-blind mechanism): {mech_finding}")
        if mech_bug:
            print(f"  ** BUG: right-ideal & not-H5 (theorem violated): {mech_bug}")
    print(f"  -> {out}")
    return 1 if (replay_fail or mech_bug) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
