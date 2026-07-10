"""V1c — the pipeline demo, normal-form economy + entry price (spec §8.5).

    python3 -m tests.calculus.v1_pipeline --one A B [--corpus DIR]
    python3 -m tests.calculus.v1_pipeline --campaign [--corpus DIR] [--budget S]

Fills the paper §3.4 entry-price TBD. Honest scope (trap #14): on this corpus
everything is deterministic and small, so the demo CANNOT show "Spot pays Safra
k times" — that stays theoretical. What it measures is the NORMAL-FORM economy:
the intermediate `|𝒞|` / state sizes along a four-stage pipeline, and the cost of
the re-check every pipeline actually runs ("did my rewrite change the
language"). For the calculus that re-check is a byte comparison of canonical
`.sos` dumps (free); for Spot it is `equivalent_to`.

Pipeline, for 20 seeded same-alphabet pairs (A, B) both in the middle `|𝒞|`
decile:

    E1 = ¬A;  E2 = E1 ∩ B;  E3 = ¬E2;  E4 = E3 ∪ A

Calculus: surgery + `reduce(check=False)` (the ∩/∪ across two tables go through
`calculus.product`); re-checks are byte compares; witnesses come free from the
decision scans. Spot: `dualize` / `product` / `product_or` then `postprocess`
(the standard simplification, timed); re-checks are `equivalent_to`. The
entry-price row is the one-time cost the CALCULUS pays that Spot does not: build
`𝓘(L)` from the deterministic automaton D (`invariant_of ∘ canonical`, the
sos-building core of `genaut/gen/canonize.py`), measured in-process.

Deliverable copied to `reference/calculus/v1_pipeline.{md,csv}`.
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
from random import Random
from typing import Callable, Dict, List, Optional, Tuple

import spot

from sosl.sos import Invariant, dump_invariant
from sosl.sos.build.importer import canonical
from sosl.sos.calculus import (
    Table,
    align,
    complement,
    intersection,
    is_empty,
    materialize,
    reduce,
    union,
)
from sosl.sos.core.quotient import invariant_of

from tests.calculus.v1_align import _Corpus, _group_by_stratum

_HERE = Path(__file__).resolve().parent
_LOGS = _HERE / "logs"
_REF = _HERE.parents[2] / "reference" / "calculus"
_CORPUS = _HERE.parents[2] / "genaut" / "corpus" / "flat_canon"

SEED = 20260712
_N_PAIRS = 20
_STAGES = ["E1=¬A", "E2=E1∩B", "E3=¬E2", "E4=E3∪A"]
_FIELDS = ["pair", "stage", "calc_n", "calc_ms", "calc_recheck_ms", "calc_empty",
           "spot_states", "spot_ms", "spot_recheck_ms", "spot_empty", "note"]


class _Budget(Exception):
    """The per-op watchdog fired (Spot side)."""


def _git_rev() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=_HERE, text=True).strip()
    except Exception:
        return "unknown"


def _median_ms(fn: Callable[[], object], reps: int = 5) -> float:
    fn()
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t0)
    return round(1000 * statistics.median(ts), 4)


# --- the two pipelines ------------------------------------------------------

Stage = Tuple[str, object, Callable[[], object]]
"""A stage name, its held result, and a thunk that recomputes it from held
inputs (for median timing and the re-check)."""


def _calc_stages(inv_a: Invariant, inv_b: Invariant) -> List[Stage]:
    ta, tb = Table.of(inv_a), Table.of(inv_b)

    def e1() -> Invariant:
        return reduce(ta, complement(ta, inv_a.accept), check=False)
    r1 = e1(); t1 = Table.of(r1)

    def cross(left: Invariant, lt: Table, right: Invariant, rt: Table,
              op) -> Invariant:
        la, lb = lt.language(left.accept), rt.language(right.accept)
        prod = materialize(align(la, lb), la, lb)
        return reduce(prod.table, op(prod.table, prod.pairs_a, prod.pairs_b),
                      check=False)

    def e2() -> Invariant:
        return cross(r1, t1, inv_b, tb, intersection)
    r2 = e2(); t2 = Table.of(r2)

    def e3() -> Invariant:
        return reduce(t2, complement(t2, r2.accept), check=False)
    r3 = e3(); t3 = Table.of(r3)

    def e4() -> Invariant:
        return cross(r3, t3, inv_a, ta, union)
    r4 = e4()
    return [(_STAGES[0], r1, e1), (_STAGES[1], r2, e2),
            (_STAGES[2], r3, e3), (_STAGES[3], r4, e4)]


def _spot_stages(aut_a, aut_b):
    def simp(a):
        return a.postprocess("Small")

    def e1():
        return simp(spot.dualize(aut_a))
    s1 = e1()

    def e2():
        return simp(spot.product(s1, aut_b))
    s2 = e2()

    def e3():
        return simp(spot.dualize(s2))
    s3 = e3()

    def e4():
        return simp(spot.product_or(s3, aut_a))
    s4 = e4()
    return [(_STAGES[0], s1, e1), (_STAGES[1], s2, e2),
            (_STAGES[2], s3, e3), (_STAGES[3], s4, e4)]


# --- one pair ---------------------------------------------------------------

def _one(corpus: _Corpus, a: str, b: str, det: Path, budget: int) -> List[Dict]:
    inv_a, inv_b = corpus.inv(a), corpus.inv(b)
    pair = f"{a}×{b}"
    calc = _calc_stages(inv_a, inv_b)
    calc_dumps = [dump_invariant(inv) for _, inv, _ in calc]

    aut_a = spot.automaton(str(det / f"{a}.hoa"))
    aut_b = spot.automaton(str(det / f"{b}.hoa"))
    signal.setitimer(signal.ITIMER_REAL, budget)
    spot_note = ""
    try:
        spot_st = _spot_stages(aut_a, aut_b)
    except _Budget:
        spot_st, spot_note = None, "F2-timeout"
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)

    rows: List[Dict] = []
    for i, (name, inv, build) in enumerate(calc):
        row: Dict = {"pair": pair, "stage": name, "calc_n": inv.n,
                     "calc_ms": _median_ms(build), "note": spot_note}
        # re-check = the COMPARISON only: the freshly recomputed form is built
        # once outside the timer (the recompute is the stage build, already
        # priced); the re-check times how much "is it the same language" costs.
        d_fresh = dump_invariant(build())
        d_stage = calc_dumps[i]
        row["calc_recheck_ms"] = _median_ms(lambda: d_stage == d_fresh)
        empty, _ = is_empty(Table.of(inv), inv.accept)
        row["calc_empty"] = int(empty)
        if spot_st is not None:
            _, au, sbuild = spot_st[i]
            signal.setitimer(signal.ITIMER_REAL, budget)
            try:
                row["spot_states"] = au.num_states()
                row["spot_ms"] = _median_ms(sbuild)
                fresh_au = sbuild()
                row["spot_recheck_ms"] = _median_ms(
                    lambda: fresh_au.equivalent_to(au))
                row["spot_empty"] = int(au.is_empty())
            except _Budget:
                row.update(spot_states="", spot_ms="", spot_recheck_ms="",
                           spot_empty="", note="F2-timeout")
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
        else:
            row.update(spot_states="", spot_ms="", spot_recheck_ms="",
                       spot_empty="")
        rows.append(row)
    return rows


def _entry_ms(det: Path, name: str, budget: int) -> float:
    """The one-time entry price: build 𝓘(L) from the deterministic automaton D
    (`invariant_of ∘ canonical`), the sos-building core of `canonize.py`."""
    path = str(det / f"{name}.hoa")

    def build() -> object:
        return dump_invariant(invariant_of(canonical(spot.automaton(path))))
    return _median_ms(build)


# --- sampling ---------------------------------------------------------------

def _middle_decile_pairs(corpus: _Corpus, rng: Random, k: int
                         ) -> List[Tuple[str, str]]:
    ns = sorted(corpus.classes(n) for n in corpus.names)
    lo, hi = ns[int(0.45 * len(ns))], ns[int(0.55 * len(ns))]
    band = [n for n in corpus.names if lo <= corpus.classes(n) <= hi]
    groups = _group_by_stratum(corpus, band)
    keys = [g for g, lst in sorted(groups.items()) if len(lst) >= 2]
    weights = [len(groups[g]) for g in keys]
    seen: set = set()
    out: List[Tuple[str, str]] = []
    while len(out) < k:
        g = rng.choices(keys, weights=weights, k=1)[0]
        lst = groups[g]
        i, j = rng.sample(range(len(lst)), 2)
        pair = tuple(sorted((lst[i], lst[j])))
        if pair in seen:
            continue
        seen.add(pair)
        out.append(pair)  # type: ignore[arg-type]
    return out


# --- summary ----------------------------------------------------------------

def _med(xs: List[float]) -> float:
    return statistics.median(xs) if xs else float("nan")


def _col(rows: List[Dict], stage: str, key: str) -> List[float]:
    return [float(r[key]) for r in rows
            if r["stage"] == stage and r[key] not in ("", None)]


def _summary(rows: List[Dict], entry: List[float], corpus_path: Path,
             n_pairs: int) -> str:
    L: List[str] = []
    L.append("# V1c — pipeline demo: normal-form economy + entry price")
    L.append("")
    L.append(f"- date: {date.today().isoformat()}")
    L.append(f"- git: {_git_rev()}")
    L.append(f"- seed: {SEED}  |  {n_pairs} same-alphabet pairs, middle |𝒞| decile")
    L.append(f"- corpus: {corpus_path}")
    L.append("")
    L.append("Pipeline `E1=¬A · E2=E1∩B · E3=¬E2 · E4=E3∪A`. Calculus times are "
             "surgery + `reduce(check=False)` (∩/∪ via `calculus.product`); Spot "
             "times are the op + `postprocess(Small)`. Medians over the pairs. "
             "Trap #14: deterministic corpus — this is the normal-form economy, "
             "not a Safra story.")
    L.append("")
    L.append("| stage | median classes (calc) | calc ms | median states (Spot) "
             "| Spot ms |")
    L.append("|---|---|---|---|---|")
    L.append(f"| entry: build 𝓘(L) from D | — | {_med(entry):.4f} | — | native |")
    calc_tot, spot_tot = _med(entry), 0.0
    for st in _STAGES:
        cn, cm = _col(rows, st, "calc_n"), _col(rows, st, "calc_ms")
        ss, sm = _col(rows, st, "spot_states"), _col(rows, st, "spot_ms")
        calc_tot += _med(cm)
        spot_tot += (_med(sm) if sm else 0.0)
        L.append(f"| {st} | {_med(cn):.0f} | {_med(cm):.4f} | "
                 f"{(_med(ss) if ss else float('nan')):.0f} | "
                 f"{(_med(sm) if sm else float('nan')):.4f} |")
    L.append(f"| **cumulative** (entry + 4 stages) | — | **{calc_tot:.4f}** | — "
             f"| **{spot_tot:.4f}** |")
    L.append("")

    # the re-check economy: byte compare vs equivalent_to
    cr = [x for st in _STAGES for x in _col(rows, st, "calc_recheck_ms")]
    sr = [x for st in _STAGES for x in _col(rows, st, "spot_recheck_ms")]
    L.append(f"**Re-check economy.** Median per-stage \"did my rewrite change the "
             f"language\" re-check: calculus {_med(cr):.4f} ms (a byte compare of "
             f"canonical `.sos` dumps) vs Spot {_med(sr):.4f} ms (`equivalent_to`). "
             f"The canonical normal form turns the query every pipeline runs into "
             f"a string comparison.")
    L.append("")
    L.append(f"**Entry price.** The calculus pays a one-time "
             f"{_med(entry):.4f} ms to build `𝓘(L)` from the deterministic D that "
             f"Spot consumes natively; thereafter each surgery is a set operation "
             f"on a held object and each re-check is free. Amortized over a "
             f"four-stage pipeline the entry is a "
             f"{100 * _med(entry) / calc_tot:.0f}% share of the calculus total.")
    L.append("")
    L.append("**Trap #14.** Every automaton here is deterministic and small, so "
             "no Safra determinization is forced and intermediate sizes stay "
             "modest on both sides; the demo isolates the normal-form / free-"
             "recheck economy, not the exponential entry the theory row reserves.")
    L.append("")
    return "\n".join(L)


def _csv_text(rows: List[Dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=_FIELDS)
    w.writeheader()
    for r in sorted(rows, key=lambda r: (r["pair"], r["stage"])):
        w.writerow({k: r.get(k, "") for k in _FIELDS})
    return buf.getvalue()


# --- drivers ----------------------------------------------------------------

def run_campaign(argv: List[str]) -> int:
    corpus_path, budget = _CORPUS, 10
    it = iter(argv)
    for a in it:
        if a == "--corpus":
            corpus_path = Path(next(it))
        elif a == "--budget":
            budget = int(next(it))
    det = corpus_path / "det"
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(_Budget()))
    print("loading corpus...")
    corpus = _Corpus(corpus_path / "sos")
    pairs = _middle_decile_pairs(corpus, Random(SEED), _N_PAIRS)
    print(f"=== V1c: {len(pairs)} pipeline pairs ===")

    _LOGS.mkdir(exist_ok=True)
    ckpt = _LOGS / "v1_pipeline.ckpt"
    done: Dict[str, Dict] = {}
    if ckpt.exists():
        with open(ckpt, newline="") as fh:
            for r in csv.DictReader(fh):
                done[f"{r['pair']}|{r['stage']}"] = r
    new = not ckpt.exists()
    entry: List[float] = []
    with open(ckpt, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=_FIELDS)
        if new:
            w.writeheader()
        for i, (a, b) in enumerate(pairs, 1):
            entry.append(_entry_ms(det, a, budget))
            if f"{a}×{b}|{_STAGES[0]}" in done:
                continue
            for r in _one(corpus, a, b, det, budget):
                w.writerow(r); done[f"{r['pair']}|{r['stage']}"] = r
            fh.flush()
            print(f"  pair {i}/{len(pairs)}: {a}×{b}")

    rows = list(done.values())
    f2 = sum(1 for r in rows if str(r["note"]).startswith("F2"))
    print(f"{len(rows)} rows, F2: {f2}")
    _REF.mkdir(parents=True, exist_ok=True)
    (_REF / "v1_pipeline.csv").write_text(_csv_text(rows))
    (_REF / "v1_pipeline.md").write_text(
        _summary(rows, entry, corpus_path, len(pairs)))
    print(f"wrote {_REF / 'v1_pipeline.md'} and .csv")
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
    print(f"entry(A) = {_entry_ms(det, a, 10):.4f} ms")
    for r in _one(corpus, a, b, det, 10):
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
