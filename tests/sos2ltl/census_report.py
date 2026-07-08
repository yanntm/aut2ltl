"""E1/E2 tables from language-keyed census JSONLs, per the §3b discipline.

    python3 -m tests.sos2ltl.census_report <e12_TAG.jsonl> [<e12_TAG2.jsonl> ...]

Each input is one shape's records (built by `tests.sos2ltl.census_build` over
`corpus/sos/<tag>`, one record per distinct language: `n`, `aperiodic`,
`degenerate`, `prefix_independent`, and a `layers` list of per-layer
`a_width` / `kinds` / `b_status` / `b_width` / `b_trivial`). Prints, per §3b:

  * the **frame** (states / AP / acceptance-set count and family, from the tag);
  * the **degenerate line** — empty/universal specimens split out, so the
    headline E1/E2 fractions are restated over the non-degenerate languages;
  * **per-shape rows** for E1 (condition A) and E2 (condition B), with a
    pooled total alongside — never instead of — the rows;
  * the **presentation multiplicity** (the tgba→language collapse) read from
    each shape's `corpus/det/<tag>/census.md`.

The unit throughout is the language (a `corpus/sos` file); automaton counts
live only in the multiplicity column.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

DET_CENSUS = "genaut/corpus/det/{tag}/census.md"


def _frozen(layer: Dict[str, Any]) -> bool:
    """A final-candidate layer with no within-layer movement: an internal
    cycle (non-TRANSIENT) yet every letter neutral or exiting."""
    kinds = layer["kinds"]
    return (layer["b_status"] != "TRANSIENT"
            and "reset" not in kinds and "mixed" not in kinds)


def _pct(num: int, den: int) -> str:
    return f"{100.0 * num / den:.1f}%" if den else "—"


def _tag_of(path: str) -> str:
    """The shape tag from an `e12_<tag>.jsonl` path (or the bare stem)."""
    stem = Path(path).stem
    return stem[4:] if stem.startswith("e12_") else stem


def _frame(tag: str) -> str:
    """The §3b frame caption parsed from a shape tag."""
    m = re.match(r"(\d+)state(\d+)ap(\d+)acc(_parity)?$", tag)
    if not m:
        return tag
    st, ap, acc, par = m.groups()
    fam = "parity" if par else "gba (Inf-conjunction, Büchi-flavoured)"
    return (f"{st} state / {ap} AP / {acc} acceptance set(s), family {fam}; "
            f"deterministic Emerson–Lei, exhaustive over the shape")


def _multiplicity(tag: str) -> str:
    """The tgba→language collapse from `corpus/det/<tag>/census.md`, or '—'."""
    p = Path(DET_CENSUS.format(tag=tag))
    if not p.exists():
        return "—"
    txt = p.read_text()
    coll = re.search(r"collapse:\s*([\d.]+)x", txt)
    ab = re.search(r"median (\d+), max (\d+)", txt)
    parts = []
    if coll:
        parts.append(f"{coll.group(1)}x")
    if ab:
        parts.append(f"med {ab.group(1)}/max {ab.group(2)}")
    return " ".join(parts) or "—"


def _stats(recs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """E1/E2 aggregates over one shape's records (§3b: over the non-degenerate
    LTL languages; degenerate and non-LTL counts kept alongside)."""
    errors = [r for r in recs if "error" in r]
    ltl = [r for r in recs if r.get("aperiodic") and "error" not in r]
    nonltl = [r for r in recs if not r.get("aperiodic") and "error" not in r]
    degen = Counter(r["degenerate"] for r in ltl if r.get("degenerate"))
    nd = [r for r in ltl if not r.get("degenerate")]
    single = sum(r["n"] <= 2 for r in nd)  # one non-ε word class

    layers = [la for r in nd for la in r["layers"]]
    awid: Counter = Counter(
        "FAIL" if la["a_width"] is None else la["a_width"] for la in layers)
    frozen = sum(_frozen(la) for la in layers)
    full_k3 = sum(
        all(la["a_width"] is not None and la["a_width"] <= 3 for la in r["layers"])
        for r in nd)
    pind = sum(bool(r.get("prefix_independent")) for r in nd)

    finals = [la for la in layers if la["b_status"] != "TRANSIENT"]
    bstat: Counter = Counter(la["b_status"] for la in finals)
    passes = [la for la in finals if la["b_status"] == "PASS"]
    bwid: Counter = Counter(la["b_width"] for la in passes)

    return {
        "langs": len(recs), "ltl": len(ltl), "nonltl": len(nonltl),
        "errors": len(errors), "degen": degen, "nd": len(nd), "single": single,
        "layers": layers, "awid": awid, "frozen": frozen, "full_k3": full_k3,
        "pind": pind, "finals": finals, "bstat": bstat, "passes": passes,
        "bwid": bwid,
    }


def _e1_row(tag: str, s: Dict[str, Any]) -> str:
    layers, awid = s["layers"], s["awid"]
    nl = len(layers)
    at1 = awid.get(1, 0)
    at3 = sum(awid.get(k, 0) for k in (1, 2, 3))
    fail = awid.get("FAIL", 0)  # (A)-tester tops out at k=3: the gap is FAIL
    return (f"  {tag:24s} {s['nd']:5d} {nl:7d} "
            f"{_pct(at1, nl):>7} {_pct(at3, nl):>7} {fail:5d} "
            f"{_pct(s['frozen'], nl):>7} {_pct(s['full_k3'], s['nd']):>7} "
            f"{_pct(s['pind'], s['nd']):>7}")


def _e2_row(tag: str, s: Dict[str, Any]) -> str:
    finals, passes, bwid = s["finals"], s["passes"], s["bwid"]
    nf = len(finals)
    det2 = sum(la["b_width"] <= 2 for la in passes)
    npass = s["bstat"].get("PASS", 0)
    nund = s["bstat"].get("UNDECIDED", 0)
    nfail = s["bstat"].get("FAIL", 0)
    return (f"  {tag:24s} {nf:6d} {npass:6d} {nund:5d} {nfail:5d} "
            f"{_pct(det2, nf):>7} {str(dict(sorted(bwid.items(), key=lambda x: str(x[0])))):>16}")


def main(argv: List[str]) -> int:
    paths = [a for a in argv if not a.startswith("--")]
    shapes = [(_tag_of(p), _stats(
        [json.loads(l) for l in Path(p).read_text().splitlines() if l]))
        for p in paths]

    print("=== frame (§3b) ===")
    for tag, _ in shapes:
        print(f"  {tag:24s} {_frame(tag)}")

    print("\n=== degenerate + presentation multiplicity (per shape) ===")
    print(f"  {'shape':24s} {'langs':>5} {'LTL':>5} {'nonLTL':>6} "
          f"{'empty':>5} {'univ':>5} {'1cls*':>5} {'mult(tgba→lang)':>18}")
    for tag, s in shapes:
        print(f"  {tag:24s} {s['langs']:5d} {s['ltl']:5d} {s['nonltl']:6d} "
              f"{s['degen'].get('empty', 0):5d} {s['degen'].get('universal', 0):5d} "
              f"{s['single']:5d} {_multiplicity(tag):>18}")
    print("  (* single non-ε word class, among non-degenerate; "
          "E1/E2 below are over non-degenerate LTL)")

    print("\n=== E1 — anchoring (condition A), non-degenerate LTL ===")
    print(f"  {'shape':24s} {'langs':>5} {'layers':>7} "
          f"{'A@1':>7} {'A≤3':>7} {'FAIL':>5} {'frozen':>7} {'stemk3':>7} {'pfxind':>7}")
    for tag, s in shapes:
        print(_e1_row(tag, s))
    if len(shapes) > 1:
        print(_e1_row("POOLED", _pool(shapes)))

    print("\n=== E2 — window determinacy (condition B), non-degenerate LTL ===")
    print(f"  {'shape':24s} {'final':>6} {'PASS':>6} {'UND':>5} {'FAIL':>5} "
          f"{'k′≤2':>7} {'PASSwidth':>16}")
    for tag, s in shapes:
        print(_e2_row(tag, s))
    if len(shapes) > 1:
        print(_e2_row("POOLED", _pool(shapes)))
    return 0


def _pool(shapes: List[Any]) -> Dict[str, Any]:
    """Pooled aggregates across shapes (§3b: alongside, never instead of, the
    per-shape rows)."""
    ss = [s for _, s in shapes]
    layers = [la for s in ss for la in s["layers"]]
    finals = [la for s in ss for la in s["finals"]]
    passes = [la for s in ss for la in s["passes"]]
    awid: Counter = Counter()
    bwid: Counter = Counter()
    bstat: Counter = Counter()
    for s in ss:
        awid.update(s["awid"]); bwid.update(s["bwid"]); bstat.update(s["bstat"])
    return {
        "nd": sum(s["nd"] for s in ss), "layers": layers, "awid": awid,
        "frozen": sum(s["frozen"] for s in ss),
        "full_k3": sum(s["full_k3"] for s in ss),
        "pind": sum(s["pind"] for s in ss), "finals": finals,
        "bstat": bstat, "passes": passes, "bwid": bwid,
    }


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
