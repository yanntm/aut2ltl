"""E1/E2 tables from the language-keyed census, ventilated by Wagner degree.

    python3 -m tests.sos2ltl.census_report <e12.jsonl> [<e12b.jsonl> ...] \
        [--sos-dir genaut/corpus/flat_canon/sos]

The input records are built by `tests.sos2ltl.census_build` over the
`flat_canon/sos` catalogue — one record per distinct language (`id`,
`aperiodic`, `degenerate`, `prefix_independent`, and a `layers` list of
per-layer `a_width` / `kinds` / `b_status` / `b_width` / `b_trivial`). The
catalogue is a single cross-shape, complement-closed pool, so there are no
per-shape rows to print; instead each language is placed in its **Wagner
degree** bucket (`ϕ = (γ, s)`, read from its `.cat` sidecar under `--sos-dir`),
and E1/E2 are ventilated by degree — the language-complexity axis that replaces
the old per-shape ventilation. Prints:

  * the **frame** — catalogue size, the LTL cut, the degenerate line
    (empty/universal, split out of the headline fractions);
  * **E1** (condition A) and **E2** (condition B) per Wagner degree over the
    non-degenerate LTL languages, with a pooled total alongside the rows.

The unit throughout is the language (a `flat_canon/sos` file).
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from tests.sos2ltl.cat_sidecar import PHI_LABEL, cat_for, phi_rank

DEFAULT_SOS_DIR = "genaut/corpus/flat_canon/sos"


def _frozen(layer: Dict[str, Any]) -> bool:
    """A final-candidate layer with no within-layer movement: an internal
    cycle (non-TRANSIENT) yet every letter neutral or exiting."""
    kinds = layer["kinds"]
    return (layer["b_status"] != "TRANSIENT"
            and "reset" not in kinds and "mixed" not in kinds)


def _pct(num: int, den: int) -> str:
    return f"{100.0 * num / den:.1f}%" if den else "—"


def _stats(recs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """E1/E2 aggregates over a bucket of non-degenerate LTL records."""
    single = sum(r["n"] <= 2 for r in recs)  # one non-ε word class

    layers = [la for r in recs for la in r["layers"]]
    awid: Counter = Counter(
        "FAIL" if la["a_width"] is None else la["a_width"] for la in layers)
    frozen = sum(_frozen(la) for la in layers)
    full_k3 = sum(
        all(la["a_width"] is not None and la["a_width"] <= 3 for la in r["layers"])
        for r in recs)
    pind = sum(bool(r.get("prefix_independent")) for r in recs)

    finals = [la for la in layers if la["b_status"] != "TRANSIENT"]
    bstat: Counter = Counter(la["b_status"] for la in finals)
    passes = [la for la in finals if la["b_status"] == "PASS"]
    bwid: Counter = Counter(la["b_width"] for la in passes)

    return {
        "nd": len(recs), "single": single, "layers": layers, "awid": awid,
        "frozen": frozen, "full_k3": full_k3, "pind": pind, "finals": finals,
        "bstat": bstat, "passes": passes, "bwid": bwid,
    }


def _e1_row(label: str, s: Dict[str, Any]) -> str:
    layers, awid = s["layers"], s["awid"]
    nl = len(layers)
    at1 = awid.get(1, 0)
    at3 = sum(awid.get(k, 0) for k in (1, 2, 3))
    fail = awid.get("FAIL", 0)  # (A)-tester tops out at k=3: the gap is FAIL
    return (f"  {label:16s} {s['nd']:5d} {nl:7d} "
            f"{_pct(at1, nl):>7} {_pct(at3, nl):>7} {fail:5d} "
            f"{_pct(s['frozen'], nl):>7} {_pct(s['full_k3'], s['nd']):>7} "
            f"{_pct(s['pind'], s['nd']):>7}")


def _e2_row(label: str, s: Dict[str, Any]) -> str:
    finals, passes, bwid = s["finals"], s["passes"], s["bwid"]
    nf = len(finals)
    det2 = sum(la["b_width"] <= 2 for la in passes)
    npass = s["bstat"].get("PASS", 0)
    nund = s["bstat"].get("UNDECIDED", 0)
    nfail = s["bstat"].get("FAIL", 0)
    return (f"  {label:16s} {nf:6d} {npass:6d} {nund:5d} {nfail:5d} "
            f"{_pct(det2, nf):>7} "
            f"{str(dict(sorted(bwid.items(), key=lambda x: str(x[0])))):>16}")


def main(argv: List[str]) -> int:
    sos_dir = DEFAULT_SOS_DIR
    if "--sos-dir" in argv:
        sos_dir = argv[argv.index("--sos-dir") + 1]
    paths = [a for a in argv if not a.startswith("--")
             and a != sos_dir]

    recs: List[Dict[str, Any]] = []
    for p in paths:
        recs += [json.loads(l) for l in Path(p).read_text().splitlines() if l]

    errors = [r for r in recs if "error" in r]
    ltl = [r for r in recs if r.get("aperiodic") and "error" not in r]
    nonltl = [r for r in recs if not r.get("aperiodic") and "error" not in r]
    degen = Counter(r["degenerate"] for r in ltl if r.get("degenerate"))
    nd = [r for r in ltl if not r.get("degenerate")]

    print("=== frame ===")
    print(f"  catalogue     genaut/corpus/flat_canon/sos — one deterministic "
          f"Emerson–Lei automaton per distinct language, complement-closed")
    print(f"  languages     {len(recs)}  ({len(ltl)} LTL / {len(nonltl)} non-LTL"
          f"{f'; {len(errors)} error' if errors else ''})")
    print(f"  degenerate    empty {degen.get('empty', 0)}, "
          f"universal {degen.get('universal', 0)} (split out of E1/E2 below)")
    print(f"  E1/E2 over    {len(nd)} non-degenerate LTL languages, "
          f"ventilated by Wagner degree ϕ=(γ,s) from the .cat sidecars")

    # Bucket the non-degenerate LTL languages by Wagner degree.
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    no_cat = 0
    for r in nd:
        cat = cat_for(sos_dir, r["id"]) if "id" in r else None
        if cat is None:
            no_cat += 1
            continue
        buckets.setdefault(cat.phi, []).append(r)
    phis = sorted(buckets, key=phi_rank)
    pooled = _stats(nd)
    if no_cat:
        print(f"  (warning: {no_cat} records had no .cat sidecar — "
              f"pooled only, no degree row)")

    print("\n=== E1 — anchoring (condition A), non-degenerate LTL, by degree ===")
    print(f"  {'ϕ=(γ,s)':16s} {'langs':>5} {'layers':>7} "
          f"{'A@1':>7} {'A≤3':>7} {'FAIL':>5} {'frozen':>7} {'stemk3':>7} "
          f"{'pfxind':>7}")
    for phi in phis:
        print(_e1_row(PHI_LABEL.get(phi, phi), _stats(buckets[phi])))
    print(_e1_row("POOLED", pooled))

    print("\n=== E2 — window determinacy (condition B), non-degen LTL, by degree ===")
    print(f"  {'ϕ=(γ,s)':16s} {'final':>6} {'PASS':>6} {'UND':>5} {'FAIL':>5} "
          f"{'k′≤2':>7} {'PASSwidth':>16}")
    for phi in phis:
        print(_e2_row(PHI_LABEL.get(phi, phi), _stats(buckets[phi])))
    print(_e2_row("POOLED", pooled))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
