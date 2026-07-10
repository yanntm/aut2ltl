"""V1b — operation costs, calculus vs Spot, over flat_canon (spec §8.4).

    python3 -m tests.calculus.v1_ops --one A B [--corpus DIR]
    python3 -m tests.calculus.v1_ops --campaign [--corpus DIR] [--limit N] [--budget S]

Fills the paper §4 ledger TBD. Framing (§8.4, verbatim intent): the corpus
automata are DETERMINISTIC, so Spot's complement is `spot.dualize` — cheap and
correct — and nothing here exhibits the 2^Θ(n log n) NBA complementation of the
theory row. V1b measures the HELD-OBJECT economy (what an operation costs once
you hold the canonical object vs a deterministic automaton), NOT the
nondeterministic entry story; the theory row stands on [TFVT10], not these
timings. `reduce` is a normal form and Spot's simplification a heuristic — they
sit in SEPARATE columns, never a ratio (trap #12).

Sample: the first 1000 `uniform` pairs of V1a (same seed), plus each distinct
language for the unary rows. Warm/cold policy (§8.1, trap #5): the memoized
idem/linked/keys are part of the held object, so per-op timings are WARM
(1 warmup + median of 7); `align` is reported COLD and its time is excluded from
the per-op rows (reported as align-amortized figures instead). Every wall clock
carries abstract counts (|nodes|, cells, |linked|) — the paper argues with
counts, the times corroborate (trap #4). Spot is bounded-or-skipped (budget,
checkpoint; a stall loses one case as F2, trap #2). Complement on the Spot side
is `dualize`, never NBA complementation (trap #8).

Working rows go to `tests/calculus/logs/`; the validated summary is copied to
`reference/calculus/v1_ops.{md,csv}`.
"""
from __future__ import annotations

import csv
import io
import signal
import statistics
import subprocess
import sys
import time
from datetime import date
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import spot

from sosl.sos import Invariant, dump_invariant, load_invariant
from sosl.sos.calculus import (
    Table,
    align,
    complement,
    equivalent,
    included,
    intersecting_word,
    intersection,
    materialize,
    member,
    reduce,
)
from sosl.teacher.whitebox import HoaTeacher

from tests.calculus.v1_align import _Corpus, _pairs_for

_HERE = Path(__file__).resolve().parent
_LOGS = _HERE / "logs"
_REF = _HERE.parents[2] / "reference" / "calculus"
_CORPUS = _HERE.parents[2] / "genaut" / "corpus" / "flat_canon"

_N_PAIRS = 1000
_FIELDS = ["op", "case", "calc_ms", "spot_ms", "spot2_ms",
           "nodes", "cells", "linked", "note"]


class _Budget(Exception):
    """The per-op watchdog fired (Spot side)."""


def _git_rev() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=_HERE, text=True).strip()
    except Exception:
        return "unknown"


def _median_ms(fn: Callable[[], object], reps: int = 7) -> float:
    """Warm median wall time in ms: one warmup, then median of `reps` calls."""
    fn()
    ts = [(_t(fn)) for _ in range(reps)]
    return round(1000 * statistics.median(ts), 4)


def _t(fn: Callable[[], object]) -> float:
    t0 = time.perf_counter()
    fn()
    return time.perf_counter() - t0


# --- Spot side, bounded -----------------------------------------------------

def _spot_ms(fn: Callable[[], object], budget: int) -> Tuple[Optional[float], str]:
    """Warm median of a Spot call under the watchdog. Returns (ms, note); on a
    fired budget (or a raised Spot error) ms is None and the note records it."""
    signal.setitimer(signal.ITIMER_REAL, budget)
    try:
        ms = _median_ms(fn)
        return ms, ""
    except _Budget:
        return None, "F2-timeout"
    except Exception as e:  # a Spot binding refusal is a datum, not a crash
        return None, f"F2-{type(e).__name__}"
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


# --- the measured pair ------------------------------------------------------

def _binary_rows(corpus: _Corpus, a: str, b: str, det: Path, budget: int
                 ) -> List[Dict]:
    """The binary-operation rows for one pair (inclusion, equivalence,
    intersection-word, intersection-object). `align` is built once and priced
    cold as its own row; the per-op rows exclude it."""
    inv_a, inv_b = corpus.inv(a), corpus.inv(b)
    la = corpus.table(a).language(inv_a.accept)
    lb = corpus.table(b).language(inv_b.accept)
    case = f"{a}×{b}"
    rows: List[Dict] = []
    if la.alphabet != lb.alphabet:
        return [{"op": "align", "case": case, "note": "alphabet-mismatch",
                 **{k: "" for k in _FIELDS if k not in ("op", "case", "note")}}]

    # align: cold, single call (its ratio/nodes feed the amortized figures)
    t0 = time.perf_counter()
    aligned = align(la, lb)
    align_ms = round(1000 * (time.perf_counter() - t0), 4)
    nodes, cells = aligned.n, aligned.n * aligned.n
    lk = len(corpus.table(a).linked) + len(corpus.table(b).linked)
    rows.append({"op": "align", "case": case, "calc_ms": align_ms, "spot_ms": "",
                 "spot2_ms": "", "nodes": nodes, "cells": cells, "linked": lk,
                 "note": "cold"})

    aut_a = spot.automaton(str(det / f"{a}.hoa"))
    aut_b = spot.automaton(str(det / f"{b}.hoa"))

    # inclusion: L(a) ⊆ L(b)  vs  spot.contains(b, a)
    calc = _median_ms(lambda: included(aligned))
    sp, note = _spot_ms(lambda: spot.contains(aut_b, aut_a), budget)
    rows.append(_row("inclusion", case, calc, sp, "", nodes, cells, lk, note))

    # equivalence: equivalent(aligned)  vs  a.equivalent_to(b)
    calc = _median_ms(lambda: equivalent(aligned))
    sp, note = _spot_ms(lambda: aut_a.equivalent_to(aut_b), budget)
    rows.append(_row("equivalence", case, calc, sp, "", nodes, cells, lk, note))

    # intersection-word: intersecting_word(aligned)  vs  a.intersecting_word(b)
    calc = _median_ms(lambda: intersecting_word(aligned))
    sp, note = _spot_ms(lambda: aut_a.intersecting_word(aut_b), budget)
    rows.append(_row("intersect_word", case, calc, sp, "", nodes, cells, lk, note))

    # intersection-object: materialize + pointwise ∧ + reduce(check=False)
    #   vs spot.product (raw) and spot.product + simplification (separate col)
    def calc_intersect() -> object:
        prod = materialize(aligned, la, lb)
        return reduce(prod.table,
                      intersection(prod.table, prod.pairs_a, prod.pairs_b),
                      check=False)
    calc = _median_ms(calc_intersect)
    sp, note = _spot_ms(lambda: spot.product(aut_a, aut_b), budget)
    sp2, note2 = _spot_ms(
        lambda: spot.product(aut_a, aut_b).postprocess("Small"), budget)
    if sp2 is None:
        note = (note + " " + note2).strip()
    prod_linked = len(materialize(aligned, la, lb).table.linked)
    rows.append(_row("intersect_obj", case, calc, sp, sp2 if sp2 is not None else "",
                     nodes, cells, prod_linked, note))
    return rows


def _unary_rows(corpus: _Corpus, name: str, det: Path, budget: int) -> List[Dict]:
    """The unary-operation rows for one language (complement, membership)."""
    inv = corpus.inv(name)
    table = corpus.table(name)
    lk = len(table.linked)
    rows: List[Dict] = []
    aut = spot.automaton(str(det / f"{name}.hoa"))

    # complement: complement + reduce(check=False)  vs  spot.dualize
    def calc_complement() -> object:
        return reduce(table, complement(table, inv.accept), check=False)
    calc = _median_ms(calc_complement)
    sp, note = _spot_ms(lambda: spot.dualize(aut), budget)
    rows.append(_row("complement", name, calc, sp, "", inv.n, "", lk, note))

    # membership: member on a canonical witness lasso  vs teacher HOA replay
    lasso = table.cell_lasso(next(table.cells()))
    calc = _median_ms(lambda: member(table, inv.accept, lasso))
    teacher = HoaTeacher.of_hoa(str(det / f"{name}.hoa"))
    sp, note = _spot_ms(lambda: teacher.member(lasso), budget)
    rows.append(_row("membership", name, calc, sp, "", inv.n, "", lk, note))
    return rows


def _row(op: str, case: str, calc: Optional[float], sp: Optional[float],
         sp2, nodes, cells, linked, note: str) -> Dict:
    return {"op": op, "case": case,
            "calc_ms": "" if calc is None else calc,
            "spot_ms": "" if sp is None else sp,
            "spot2_ms": sp2, "nodes": nodes, "cells": cells,
            "linked": linked, "note": note}


# --- summary ----------------------------------------------------------------

def _med(xs: List[float]) -> float:
    return statistics.median(xs) if xs else float("nan")


def _headline(rows: List[Dict]) -> Optional[str]:
    """The one-paragraph headline for the abstract (deliverable §8.9 item 6):
    corpus size, V1a median uniform ratio, a representative held-object op time,
    and the V2 stutter agreement rate — pulled from the delivered V1a/V2 CSVs so
    it stays reproducible from the committed artifacts. None if they are absent."""
    align_csv, stutter_csv = _REF / "v1_align_ratio.csv", _REF / "v2_stutter.csv"
    if not (align_csv.exists() and stutter_csv.exists()):
        return None
    uni = sorted(float(r["ratio"]) for r in csv.DictReader(open(align_csv))
                 if r["pop"] == "uniform" and r["ratio"] not in ("", None))
    srows = list(csv.DictReader(open(stutter_csv)))
    agree = sum(1 for r in srows if r.get("agree") == "yes")
    total = sum(1 for r in srows if r.get("agree") in ("yes", "no"))
    incl = sorted(float(r["calc_ms"]) for r in rows
                  if r["op"] == "inclusion" and r["calc_ms"] not in ("", None))
    return (
        f"Over the {len(srows)}-language flat_canon census the generated product "
        f"is affordable — median uniform alignment ratio {_med(uni):.3f} of the "
        f"`n_A·n_B` rectangle (V1a) — and held-object operations are microsecond-"
        f"scale: a containment decision runs in {_med(incl):.4f} ms once the "
        f"product is aligned (V1b). The stutter read-off agrees with Spot on "
        f"{agree}/{total} languages (V2).")


def _summary(rows: List[Dict], corpus_path: Path, n_pairs: int,
             n_langs: int) -> str:
    def col(op: str, key: str) -> List[float]:
        return sorted(float(r[key]) for r in rows
                      if r["op"] == op and r[key] not in ("", None))

    ops = ["complement", "membership", "inclusion", "equivalence",
           "intersect_word", "intersect_obj"]
    L: List[str] = []
    L.append("# V1b — operation costs, calculus vs Spot")
    L.append("")
    L.append(f"- date: {date.today().isoformat()}")
    L.append(f"- git: {_git_rev()}")
    L.append(f"- sample: first {n_pairs} uniform pairs of V1a "
             f"({n_langs} distinct languages for the unary rows)")
    L.append(f"- corpus: {corpus_path}")
    L.append("")
    head = _headline(rows)
    if head:
        L.append("**Headline.** " + head)
        L.append("")
    L.append("Held-object economy (§8.4): inputs are deterministic, so Spot "
             "complement is `dualize`; the NBA-complementation theory row stands "
             "on [TFVT10], not these timings. Per-op times are WARM (median of "
             "7); `align` is COLD and excluded from per-op rows. Counts are the "
             "argument, times corroborate.")
    L.append("")
    L.append("| operation | calc median ms | Spot median ms | median nodes "
             "| median cells | median linked | F2 |")
    L.append("|---|---|---|---|---|---|---|")
    for op in ops:
        calc = col(op, "calc_ms")
        sp = col(op, "spot_ms")
        nd = col(op, "nodes")
        ce = col(op, "cells")
        lk = col(op, "linked")
        f2 = sum(1 for r in rows if r["op"] == op and r["note"].startswith("F2"))
        cells = f"{_med(ce):.0f}" if ce else "—"
        L.append(f"| {op} | {_med(calc):.4f} | {_med(sp):.4f} | "
                 f"{_med(nd):.0f} | {cells} | {_med(lk):.0f} | {f2} |")
    L.append("")
    sp2 = sorted(float(r["spot2_ms"]) for r in rows
                 if r["op"] == "intersect_obj" and r["spot2_ms"] not in ("", None))
    if sp2:
        L.append(f"`intersect_obj` calc is the canonical `reduce` (a normal form); "
                 f"its Spot column is raw `spot.product`. A SEPARATE "
                 f"`product + postprocess(Small)` simplification (a heuristic, NOT "
                 f"compared to `reduce` as a ratio — trap #12) has median "
                 f"{_med(sp2):.4f} ms.")
        L.append("")

    # align-amortized on a representative decision op, where align's cold entry
    # price is comparable to the warm op cost (on intersect_obj the op dwarfs it).
    align_cold = col("align", "calc_ms")
    incl = col("inclusion", "calc_ms")
    if align_cold and incl:
        ac, iw = _med(align_cold), _med(incl)
        L.append("Align-amortized `inclusion` cost `(align_cold + k·op)/k` — the "
                 "cold `align` is a shared entry price, paid once per held product "
                 "then spread over the k decisions run on it:")
        L.append("")
        L.append(f"| k | ms/decision |  (align_cold {ac:.4f} ms, op {iw:.4f} ms) |")
        L.append("|---|---|---|")
        for k in (1, 5, 10):
            L.append(f"| {k} | {(ac + k * iw) / k:.4f} | |")
        L.append("")
    L.append("")
    return "\n".join(L)


def _csv_text(rows: List[Dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=_FIELDS)
    w.writeheader()
    for r in sorted(rows, key=lambda r: (r["op"], r["case"])):
        w.writerow({k: r.get(k, "") for k in _FIELDS})
    return buf.getvalue()


# --- drivers ----------------------------------------------------------------

def run_campaign(argv: List[str]) -> int:
    corpus_path, limit, budget = _CORPUS, None, 10
    it = iter(argv)
    for a in it:
        if a == "--corpus":
            corpus_path = Path(next(it))
        elif a == "--limit":
            limit = int(next(it))
        elif a == "--budget":
            budget = int(next(it))
    det = corpus_path / "det"
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(_Budget()))
    print("loading corpus...")
    corpus = _Corpus(corpus_path / "sos")

    pairs = [(a, b) for _, a, b in _pairs_for(corpus, "uniform")][:_N_PAIRS]
    if limit is not None:
        pairs = pairs[:limit]
    langs = sorted({x for p in pairs for x in p})
    print(f"=== V1b: {len(pairs)} pairs, {len(langs)} distinct languages ===")

    _LOGS.mkdir(exist_ok=True)
    ckpt = _LOGS / "v1_ops.ckpt"
    done: Dict[str, Dict] = {}
    if ckpt.exists():
        with open(ckpt, newline="") as fh:
            for r in csv.DictReader(fh):
                done[f"{r['op']}|{r['case']}"] = r
    new = not ckpt.exists()

    with open(ckpt, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=_FIELDS)
        if new:
            w.writeheader()
        for i, (a, b) in enumerate(pairs, 1):
            if f"inclusion|{a}×{b}" in done:
                continue
            for r in _binary_rows(corpus, a, b, det, budget):
                w.writerow(r); done[f"{r['op']}|{r['case']}"] = r
            fh.flush()
            if i % 100 == 0:
                print(f"  binary {i}/{len(pairs)}")
        for j, name in enumerate(langs, 1):
            if f"complement|{name}" in done:
                continue
            for r in _unary_rows(corpus, name, det, budget):
                w.writerow(r); done[f"{r['op']}|{r['case']}"] = r
            fh.flush()
            if j % 100 == 0:
                print(f"  unary {j}/{len(langs)}")

    rows = list(done.values())
    f2 = sum(1 for r in rows if str(r["note"]).startswith("F2"))
    print(f"{len(rows)} rows, F2: {f2}")
    _REF.mkdir(parents=True, exist_ok=True)
    (_REF / "v1_ops.csv").write_text(_csv_text(rows))
    (_REF / "v1_ops.md").write_text(_summary(rows, corpus_path, len(pairs), len(langs)))
    print(f"wrote {_REF / 'v1_ops.md'} and .csv")
    return 0


def run_one(argv: List[str]) -> int:
    corpus_path = _CORPUS
    rest = list(argv)
    if "--corpus" in rest:
        i = rest.index("--corpus")
        corpus_path = Path(rest[i + 1]); del rest[i:i + 2]
    a, b = rest[0], rest[1]
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(_Budget()))
    corpus = _Corpus(corpus_path / "sos")
    det = corpus_path / "det"
    for r in _binary_rows(corpus, a, b, det, 10):
        print(r)
    for name in (a, b):
        for r in _unary_rows(corpus, name, det, 10):
            print(r)
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
