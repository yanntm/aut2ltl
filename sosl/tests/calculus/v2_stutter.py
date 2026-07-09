"""V2 — the stutter read-off vs Spot over the flat_canon census (spec §8.6).

    python3 -m tests.calculus.v2_stutter --one <basename> [--corpus DIR]
    python3 -m tests.calculus.v2_stutter --campaign [--corpus DIR] [--limit N] [--budget S]

Our verdict is the `.cat` `stutter:` tag (the classification read-off, paper
Prop 3.3), read for free — V2 does not recompute it. Spot's verdict is
`spot.is_stutter_invariant` on the paired deterministic HOA. The campaign scans
every language, tabulates agreement, and — the point of the exercise — turns
each disagreement into a replayable dossier under the F1 discipline (dictionary
first, a bug only on a failed witness replay):

- WE sensitive, Spot invariant: the §8.6 divergence search yields two
  stutter-equivalent lassos; replay both against the det HOA. Different det
  verdicts ⟹ the det language is sensitive, so Spot's verdict is wrong (report).
- WE invariant, Spot sensitive: suspect us — but our tag is invariant only when
  every letter is idempotent, so no bounded divergence can exist; a clean
  enumeration with Spot still disagreeing is an F1 dossier line against Spot.

Repo discipline (§8.1): per-case budget, a checkpoint so a Spot stall loses one
case, deterministic byte-stable output (timing columns aside). Working rows go
to `tests/calculus/logs/`; the validated summary is copied to
`reference/calculus/v2_stutter.md`.
"""
from __future__ import annotations

import csv
import os
import signal
import subprocess
import sys
import time
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import spot

from sosl.sos import load_invariant
from sosl.sos.calculus import Table
from sosl.sos.calculus.decide import member
from sosl.sos.classify.io import parse_cat
from sosl.teacher.whitebox import HoaTeacher

from tests.calculus.stutter import find_divergence

_HERE = Path(__file__).resolve().parent
_LOGS = _HERE / "logs"
_REF = _HERE.parents[2] / "reference" / "calculus"
_CORPUS = _HERE.parents[2] / "genaut" / "corpus" / "flat_canon"

_FIELDS = ["case", "aps", "classes", "ours", "spot", "agree", "ltl",
           "spot_ms", "note"]


class _Budget(Exception):
    """The per-case watchdog fired."""


def _git_rev() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=_HERE, text=True).strip()
    except Exception:
        return "unknown"


def _dossier(basename: str, sos_dir: Path, det_dir: Path,
             ours_inv: bool, spot_inv: bool) -> Tuple[str, List[str]]:
    """Classify one disagreement and build its dossier lines. Returns a short
    note tag for the CSV and the human dossier block."""
    inv = load_invariant((sos_dir / f"{basename}.sos").read_text())
    table = Table.of(inv)
    pairs = inv.accept
    det = HoaTeacher.of_hoa(str(det_dir / f"{basename}.hoa"))
    lines: List[str] = []

    if not ours_inv and spot_inv:
        div = find_divergence(table, pairs)
        assert div is not None, "sensitive tag with no divergence — read-off bug"
        w, wd = div
        dw, dwd = det.member(w), det.member(wd)
        alph = table.alphabet
        from sosl.sos.io.serialize import render_word
        render = lambda la: f"{render_word(alph, la.stem)}·({render_word(alph, la.loop)})^ω"
        lines.append(f"- **{basename}** — we: sensitive, Spot: invariant.")
        lines.append(f"  - stutter-equivalent pair (our `member`: "
                     f"{int(member(table, pairs, w))} vs {int(member(table, pairs, wd))}):")
        lines.append(f"    - `{render(w)}`")
        lines.append(f"    - `{render(wd)}`")
        lines.append(f"  - det HOA replay: {int(dw)} vs {int(dwd)} — "
                     + ("**det is sensitive → Spot verdict wrong (F1-Spot)**"
                        if dw != dwd else
                        "det agrees on both (no separation here); inconclusive"))
        return ("F1-Spot" if dw != dwd else "F1-inconclusive"), lines

    # ours invariant, spot sensitive
    div = find_divergence(table, pairs)
    if div is not None:
        lines.append(f"- **{basename}** — we: invariant, Spot: sensitive; but the "
                     f"scan DID find a divergence — **read-off bug (F1-us)**.")
        return "F1-us", lines
    lines.append(f"- **{basename}** — we: invariant, Spot: sensitive; no bounded "
                 f"divergence exists (every letter idempotent). F1 against Spot.")
    return "F1-Spot", lines


def _one(basename: str, sos_dir: Path, det_dir: Path, budget: int) -> Dict:
    """One census row: the `.cat` tag vs Spot on the det HOA."""
    cat = parse_cat((sos_dir / f"{basename}.cat").read_text())
    ours_inv = cat["stutter_invariant"]
    inv = load_invariant((sos_dir / f"{basename}.sos").read_text())
    row: Dict = {"case": basename, "aps": len(inv.alphabet.aps), "classes": inv.n,
                 "ltl": "yes" if cat["ltl"] else "no", "note": ""}
    signal.setitimer(signal.ITIMER_REAL, budget)
    try:
        aut = spot.automaton(str(det_dir / f"{basename}.hoa"))
        t0 = time.perf_counter()
        spot_inv = spot.is_stutter_invariant(aut)
        row["spot_ms"] = round(1000 * (time.perf_counter() - t0), 2)
        signal.setitimer(signal.ITIMER_REAL, 0)
    except _Budget:
        row.update(ours="invariant" if ours_inv else "sensitive",
                   spot="BUDGET", agree="", spot_ms="", note="F2-timeout")
        return row
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    row["ours"] = "invariant" if ours_inv else "sensitive"
    row["spot"] = "invariant" if spot_inv else "sensitive"
    row["agree"] = "yes" if ours_inv == spot_inv else "no"
    if ours_inv != spot_inv:
        note, _ = _dossier(basename, sos_dir, det_dir, ours_inv, spot_inv)
        row["note"] = note
    return row


def _cases(sos_dir: Path) -> List[str]:
    return sorted(p.stem for p in sos_dir.glob("*.sos"))


def _summary(rows: List[Dict], corpus: Path, seed_note: str) -> str:
    """The reference `.md`: header, the census split by the LTL bit, the
    agreement matrix, and the disagreement dossier."""
    sos_dir, det_dir = corpus / "sos", corpus / "det"
    n = len(rows)
    si = sum(1 for r in rows if r["ours"] == "invariant")
    si_ltl = sum(1 for r in rows if r["ours"] == "invariant" and r["ltl"] == "yes")
    ss_ltl = sum(1 for r in rows if r["ours"] == "sensitive" and r["ltl"] == "yes")
    ss_non = sum(1 for r in rows if r["ours"] == "sensitive" and r["ltl"] == "no")
    agree_inv = sum(1 for r in rows if r["agree"] == "yes" and r["ours"] == "invariant")
    agree_sen = sum(1 for r in rows if r["agree"] == "yes" and r["ours"] == "sensitive")
    disagree = [r for r in rows if r["agree"] == "no"]
    f2 = [r for r in rows if r["spot"] == "BUDGET"]
    scored = n - len(f2)
    times = sorted(r["spot_ms"] for r in rows
                   if isinstance(r.get("spot_ms"), (int, float)))
    med = times[len(times) // 2] if times else 0.0
    mx = times[-1] if times else 0.0

    L: List[str] = []
    L.append(f"date: {date.today().isoformat()}")
    L.append(f"git: {_git_rev()}")
    L.append(f"seed: {seed_note}")
    L.append(f"corpus: {corpus.relative_to(_HERE.parents[2])}")
    L.append("")
    L.append("# V2 — stutter read-off vs Spot")
    L.append("")
    L.append(f"Our verdict is the `.cat` `stutter:` tag (classify's Prop 3.3 "
             f"read-off); Spot's is `spot.is_stutter_invariant` on the paired "
             f"deterministic HOA. {n} languages, {scored} scored"
             + (f", {len(f2)} skipped (F2 budget)" if f2 else "") + ".")
    L.append("")
    L.append("## Census — the stutter read-off, split by the LTL bit")
    L.append("")
    L.append("Stutter-invariance is the X-free refinement of LTL, so every "
             "stutter-invariant language is LTL-definable.")
    L.append("")
    L.append("| | LTL | non-LTL | total |")
    L.append("|---|--:|--:|--:|")
    L.append(f"| stutter-invariant | {si_ltl} | {si - si_ltl} | {si} |")
    L.append(f"| stutter-sensitive | {ss_ltl} | {ss_non} | {n - si} |")
    L.append(f"| total | {si_ltl + ss_ltl} | {si - si_ltl + ss_non} | {n} |")
    L.append("")
    L.append(f"Stutter-invariant share: **{100*si/n:.1f}%** of the census "
             f"({si}/{n}), **{100*si/(si_ltl+ss_ltl):.1f}%** of the LTL languages.")
    L.append("")
    L.append("## Agreement with Spot")
    L.append("")
    L.append("| | Spot invariant | Spot sensitive |")
    L.append("|---|--:|--:|")
    di = sum(1 for r in disagree if r["ours"] == "invariant")
    ds = sum(1 for r in disagree if r["ours"] == "sensitive")
    L.append(f"| **ours invariant** | {agree_inv} | {di} |")
    L.append(f"| **ours sensitive** | {ds} | {agree_sen} |")
    L.append("")
    rate = 100 * (agree_inv + agree_sen) / scored if scored else 0.0
    L.append(f"Agreement: **{agree_inv + agree_sen}/{scored} = {rate:.2f}%**"
             f"{' (perfect)' if not disagree else ''}. Spot `is_stutter_invariant` "
             f"on these tiny deterministic automata is near-instant: median "
             f"{med:.3f} ms, max {mx:.2f} ms.")
    L.append("")
    L.append("## Disagreement dossier")
    L.append("")
    if not disagree:
        L.append("None — the algebraic read-off and Spot agree on every scored "
                 "language.")
    else:
        for r in sorted(disagree, key=lambda r: r["case"]):
            _, block = _dossier(r["case"], sos_dir, det_dir,
                                r["ours"] == "invariant", r["spot"] == "invariant")
            L += block
    L.append("")
    return "\n".join(L)


def run_campaign(argv: List[str]) -> int:
    corpus, limit, budget = _CORPUS, None, 10
    it = iter(argv)
    for a in it:
        if a == "--corpus":
            corpus = Path(next(it))
        elif a == "--limit":
            limit = int(next(it))
        elif a == "--budget":
            budget = int(next(it))
    sos_dir, det_dir = corpus / "sos", corpus / "det"

    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(_Budget()))
    _LOGS.mkdir(exist_ok=True)
    ckpt = _LOGS / "v2_stutter.ckpt"
    done: Dict[str, Dict] = {}
    if ckpt.exists():
        with open(ckpt, newline="") as fh:
            for r in csv.DictReader(fh):
                done[r["case"]] = r

    cases = _cases(sos_dir)
    if limit is not None:
        cases = cases[:limit]
    todo = [c for c in cases if c not in done]
    print(f"=== V2 stutter: {len(cases)} cases, {len(done)} checkpointed, "
          f"{len(todo)} to run ===")

    new = not ckpt.exists()
    with open(ckpt, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=_FIELDS)
        if new:
            w.writeheader()
        for i, basename in enumerate(todo, 1):
            row = _one(basename, sos_dir, det_dir, budget)
            w.writerow(row)
            fh.flush()
            done[basename] = row
            if i % 500 == 0:
                print(f"  {i}/{len(todo)}")

    rows = [done[c] for c in cases]
    # normalize checkpoint-read strings to a uniform shape for the summary
    for r in rows:
        try:
            r["spot_ms"] = float(r["spot_ms"])
        except (ValueError, TypeError):
            r["spot_ms"] = ""
    disagree = sum(1 for r in rows if r.get("agree") == "no")
    f2 = sum(1 for r in rows if r.get("spot") == "BUDGET")
    print(f"agreement: {sum(1 for r in rows if r.get('agree')=='yes')}/"
          f"{len(rows)-f2}  disagreements: {disagree}  F2: {f2}")

    _REF.mkdir(parents=True, exist_ok=True)
    (_REF / "v2_stutter.csv").write_text(_csv_text(rows))
    (_REF / "v2_stutter.md").write_text(_summary(rows, corpus, "full sweep (no sampling)"))
    print(f"wrote {_REF/'v2_stutter.md'} and .csv")
    return 0 if disagree == 0 else 1


def _csv_text(rows: List[Dict]) -> str:
    import io
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=_FIELDS)
    w.writeheader()
    for r in sorted(rows, key=lambda r: r["case"]):
        w.writerow({k: r.get(k, "") for k in _FIELDS})
    return buf.getvalue()


def run_one(argv: List[str]) -> int:
    corpus = _CORPUS
    basename = argv[0]
    if "--corpus" in argv:
        corpus = Path(argv[argv.index("--corpus") + 1])
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(_Budget()))
    row = _one(basename, corpus / "sos", corpus / "det", 10)
    print(row)
    if row.get("agree") == "no":
        _, block = _dossier(basename, corpus / "sos", corpus / "det",
                            row["ours"] == "invariant", row["spot"] == "invariant")
        print("\n".join(block))
    return 0


def main(argv: List[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    if argv[0] == "--campaign":
        return run_campaign(argv[1:])
    if argv[0] == "--one":
        return run_one(argv[1:])
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
