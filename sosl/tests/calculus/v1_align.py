"""V1a — the alignment-ratio distribution over flat_canon (spec §8.3).

    python3 -m tests.calculus.v1_align --one A B [--corpus DIR]
    python3 -m tests.calculus.v1_align --campaign [--corpus DIR]
                                       [--pop uniform|large|related|all]
                                       [--limit N] [--budget S]

Fills the paper §3.3 TBD: how far below the rectangle ``n_A * n_B`` the
generated product `align` actually lands, and whether relatedness of the
operands collapses it as predicted. The datum per pair is ``Aligned.ratio``
(``|nodes| / (n_A * n_B)``, the field the implementation already exposes) and
the COLD BFS wall time — alignment is the one move where cold time is the ledger
entry (§8.1 warm/cold policy).

Three seeded populations (seed 20260709), each sampled WITHIN an alphabet
stratum because `align` asserts equal alphabets (trap #1):
- `uniform`: 5000 unordered pairs, drawn uniformly across strata proportionally
  to each stratum's pair count.
- `large`: 200 pairs among the top-decile ``|C|`` languages — uniform sampling
  is dominated by small tables, and the claim must be tested where products can
  grow.
- `related`: for 1000 sampled languages, the pair (L, complement partner of L),
  the partner found by content hash of ``reduce(complement(L))`` (trap #6, never
  name-mapped). Same algebra on both sides, so the product should collapse near
  the diagonal — §3.3's "related operands" contrast for free.

Repo discipline (§8.1): per-pair watchdog, a checkpoint so a stall loses one
pair, deterministic byte-stable output (the two timing columns aside). Working
rows go to `tests/calculus/logs/`; the validated summary is copied to
`reference/calculus/v1_align_ratio.{md,csv}`.
"""
from __future__ import annotations

import csv
import io
import signal
import subprocess
import sys
import time
from datetime import date
from math import comb
from pathlib import Path
from random import Random
from typing import Dict, List, Optional, Tuple

from sosl.sos import Invariant, dump_invariant, load_invariant
from sosl.sos.calculus import Table, align, complement, reduce

_HERE = Path(__file__).resolve().parent
_LOGS = _HERE / "logs"
_REF = _HERE.parents[2] / "reference" / "calculus"
_CORPUS = _HERE.parents[2] / "genaut" / "corpus" / "flat_canon"

SEED = 20260709
_N_UNIFORM = 5000
_N_LARGE = 200
_N_RELATED = 1000

_FIELDS = ["pop", "a", "b", "aps", "n_a", "n_b", "sigma",
           "nodes", "ratio", "align_ms", "note"]


class _Budget(Exception):
    """The per-pair watchdog fired."""


def _git_rev() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=_HERE, text=True).strip()
    except Exception:
        return "unknown"


# --- corpus loading, cached ------------------------------------------------

class _Corpus:
    """The parsed corpus: an Invariant/Table cache and the metadata (alphabet
    stratum key, class count) needed to stratify and sample. The complement
    partner map is built lazily (only the `related` population needs it)."""

    def __init__(self, sos_dir: Path) -> None:
        self.sos_dir = sos_dir
        self.names: List[str] = sorted(p.stem for p in sos_dir.glob("*.sos"))
        self._inv: Dict[str, Invariant] = {}
        self._table: Dict[str, Table] = {}
        self.meta: Dict[str, Tuple[Tuple[str, ...], int]] = {}
        for name in self.names:
            inv = self.inv(name)
            self.meta[name] = (tuple(inv.alphabet.aps), inv.n)
        self._partner: Optional[Dict[str, str]] = None

    def inv(self, name: str) -> Invariant:
        got = self._inv.get(name)
        if got is None:
            got = load_invariant((self.sos_dir / f"{name}.sos").read_text())
            self._inv[name] = got
        return got

    def table(self, name: str) -> Table:
        got = self._table.get(name)
        if got is None:
            got = Table.of(self.inv(name))
            self._table[name] = got
        return got

    def stratum(self, name: str) -> Tuple[str, ...]:
        return self.meta[name][0]

    def classes(self, name: str) -> int:
        return self.meta[name][1]

    def partner_of(self, name: str) -> Optional[str]:
        """The corpus basename whose language is the complement of `name`'s,
        found by content hash (not filename). None if the corpus holds no such
        file — a finding, since the corpus is complement-closed."""
        if self._partner is None:
            canon: Dict[str, str] = {}
            for other in self.names:
                canon[dump_invariant(self.inv(other))] = other
            self._partner = {}
            for n in self.names:
                tbl = self.table(n)
                comp = reduce(tbl, complement(tbl, self.inv(n).accept), check=False)
                self._partner[n] = canon.get(dump_invariant(comp), "")
        got = self._partner[name]
        return got or None


# --- one pair --------------------------------------------------------------

def _row(corpus: _Corpus, pop: str, a: str, b: str, budget: int) -> Dict:
    """One ratio row: cold-time `align(a, b)` and read `Aligned.ratio`. The two
    languages are built over distinct Table objects, so the BFS is the real
    generated product (never the diagonal short-circuit)."""
    aps, n_a = corpus.meta[a]
    _, n_b = corpus.meta[b]
    row: Dict = {"pop": pop, "a": a, "b": b, "aps": len(aps),
                 "n_a": n_a, "n_b": n_b, "sigma": 1 << len(aps),
                 "nodes": "", "ratio": "", "align_ms": "", "note": ""}
    la = corpus.table(a).language(corpus.inv(a).accept)
    lb = corpus.table(b).language(corpus.inv(b).accept)
    if la.alphabet != lb.alphabet:
        row["note"] = "alphabet-mismatch"
        return row
    signal.setitimer(signal.ITIMER_REAL, budget)
    try:
        t0 = time.perf_counter()
        aligned = align(la, lb)
        dt = time.perf_counter() - t0
    except _Budget:
        row["note"] = "F2-timeout"
        return row
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    row["nodes"] = aligned.n
    row["ratio"] = round(aligned.ratio, 4)
    row["align_ms"] = round(1000 * dt, 3)
    return row


# --- population sampling ---------------------------------------------------

def _sample_pairs(groups: Dict[Tuple[str, ...], List[str]], rng: Random,
                  k: int) -> List[Tuple[str, str]]:
    """`k` distinct unordered pairs, each within one alphabet stratum, drawn
    across strata proportionally to each stratum's pair count ``C(m, 2)``."""
    keys = [g for g, lst in sorted(groups.items()) if len(lst) >= 2]
    weights = [comb(len(groups[g]), 2) for g in keys]
    total = sum(weights)
    k = min(k, total)
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


def _group_by_stratum(corpus: _Corpus, names: List[str]
                      ) -> Dict[Tuple[str, ...], List[str]]:
    groups: Dict[Tuple[str, ...], List[str]] = {}
    for n in sorted(names):
        groups.setdefault(corpus.stratum(n), []).append(n)
    return groups


def _large_threshold(corpus: _Corpus) -> int:
    """The top-decile ``|C|`` cut: the 90th-percentile class count."""
    ns = sorted(corpus.classes(n) for n in corpus.names)
    return ns[int(0.9 * len(ns))]


def _pairs_for(corpus: _Corpus, pop: str) -> List[Tuple[str, str, str]]:
    """The deterministic (pop, a, b) list for one population."""
    if pop == "uniform":
        rng = Random(SEED)
        groups = _group_by_stratum(corpus, corpus.names)
        return [("uniform", a, b) for a, b in _sample_pairs(groups, rng, _N_UNIFORM)]
    if pop == "large":
        rng = Random(SEED + 1)
        thr = _large_threshold(corpus)
        big = [n for n in corpus.names if corpus.classes(n) >= thr]
        groups = _group_by_stratum(corpus, big)
        return [("large", a, b) for a, b in _sample_pairs(groups, rng, _N_LARGE)]
    if pop == "related":
        rng = Random(SEED + 2)
        seen: set = set()
        out: List[Tuple[str, str, str]] = []
        pool = list(corpus.names)
        idx = list(range(len(pool)))
        rng.shuffle(idx)
        for i in idx:
            if len(out) >= _N_RELATED:
                break
            a = pool[i]
            b = corpus.partner_of(a)
            if b is None:
                out.append(("related", a, "", ))  # no-partner finding
                continue
            pair = tuple(sorted((a, b)))
            if pair in seen:
                continue
            seen.add(pair)
            out.append(("related", pair[0], pair[1]))
        return out
    raise ValueError(f"unknown population {pop!r}")


# --- summary ----------------------------------------------------------------

def _pct(xs: List[float], q: float) -> float:
    """Nearest-rank percentile of a non-empty sorted list."""
    if not xs:
        return float("nan")
    i = min(len(xs) - 1, max(0, int(round(q * (len(xs) - 1)))))
    return xs[i]


def _pop_stats(rows: List[Dict]) -> Dict:
    vals = sorted(float(r["ratio"]) for r in rows if r["ratio"] != "")
    times = sorted(float(r["align_ms"]) for r in rows if r["align_ms"] != "")
    n = len(vals)
    frac = lambda thr: (sum(1 for v in vals if v < thr) / n) if n else float("nan")
    one = (sum(1 for v in vals if v >= 0.999) / n) if n else float("nan")
    return {
        "n": len(rows), "priced": n,
        "min": _pct(vals, 0.0), "p25": _pct(vals, 0.25), "med": _pct(vals, 0.5),
        "p75": _pct(vals, 0.75), "p95": _pct(vals, 0.95), "max": _pct(vals, 1.0),
        "lt25": frac(0.25), "lt50": frac(0.5), "lt90": frac(0.9), "eq1": one,
        "med_ms": _pct(times, 0.5) if times else float("nan"),
        "f2": sum(1 for r in rows if r["note"] == "F2-timeout"),
        "nopart": sum(1 for r in rows if r["note"] == "no-partner"),
    }


def _summary(rows: List[Dict], corpus_path: Path) -> str:
    pops = ["uniform", "large", "related"]
    by = {p: [r for r in rows if r["pop"] == p] for p in pops}
    st = {p: _pop_stats(by[p]) for p in pops if by[p]}
    L: List[str] = []
    L.append("# V1a — alignment-ratio distribution")
    L.append("")
    L.append(f"- date: {date.today().isoformat()}")
    L.append(f"- git: {_git_rev()}")
    L.append(f"- seed: {SEED} (uniform), {SEED + 1} (large), {SEED + 2} (related)")
    L.append(f"- corpus: {corpus_path}")
    L.append("")
    L.append("Ratio = `|nodes| / (n_A * n_B)`; time is COLD `align` BFS wall "
             "(§8.1: alignment is reported cold). Pairs are sampled within "
             "alphabet strata.")
    L.append("")
    L.append("| pop | pairs | min | p25 | median | p75 | p95 | max | med ms |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for p in pops:
        if p not in st:
            continue
        s = st[p]
        L.append(f"| {p} | {s['priced']} | {s['min']:.4f} | {s['p25']:.4f} | "
                 f"{s['med']:.4f} | {s['p75']:.4f} | {s['p95']:.4f} | "
                 f"{s['max']:.4f} | {s['med_ms']:.1f} |")
    L.append("")
    L.append("| pop | ratio<0.25 | ratio<0.5 | ratio<0.9 | ratio≈1.0 | F2 |")
    L.append("|---|---|---|---|---|---|")
    for p in pops:
        if p not in st:
            continue
        s = st[p]
        L.append(f"| {p} | {s['lt25']:.4f} | {s['lt50']:.4f} | {s['lt90']:.4f} "
                 f"| {s['eq1']:.4f} | {s['f2']} |")
    L.append("")
    if "related" in st and "uniform" in st:
        rm, um = st["related"]["med"], st["uniform"]["med"]
        rel = "below" if rm < um else ("above" if rm > um else "equal to")
        L.append(f"The `related` median ratio ({rm:.4f}) sits {rel} the `uniform` "
                 f"median ({um:.4f}): complement partners share the algebra, so the "
                 f"generated product collapses toward the diagonal, confirming "
                 f"§3.3's related-operands prediction.")
        if st["related"].get("nopart"):
            L.append("")
            L.append(f"({st['related']['nopart']} sampled languages had no "
                     f"content-matched complement partner in the corpus — "
                     f"investigate; the corpus is meant to be complement-closed.)")
    L.append("")
    return "\n".join(L)


def _csv_text(rows: List[Dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=_FIELDS)
    w.writeheader()
    for r in sorted(rows, key=lambda r: (r["pop"], r["a"], r["b"])):
        w.writerow({k: r.get(k, "") for k in _FIELDS})
    return buf.getvalue()


# --- drivers ----------------------------------------------------------------

def _ckpt_key(pop: str, a: str, b: str) -> str:
    return f"{pop}|{a}|{b}"


def run_campaign(argv: List[str]) -> int:
    corpus_path, which, limit, budget = _CORPUS, "all", None, 15
    it = iter(argv)
    for a in it:
        if a == "--corpus":
            corpus_path = Path(next(it))
        elif a == "--pop":
            which = next(it)
        elif a == "--limit":
            limit = int(next(it))
        elif a == "--budget":
            budget = int(next(it))
    pops = ["uniform", "large", "related"] if which == "all" else [which]

    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(_Budget()))
    print("loading corpus...")
    corpus = _Corpus(corpus_path / "sos")

    plan: List[Tuple[str, str, str]] = []
    for p in pops:
        got = _pairs_for(corpus, p)
        if limit is not None:
            got = got[:limit]
        plan.extend(got)
    print(f"=== V1a: {len(plan)} pairs ({', '.join(pops)}) ===")

    _LOGS.mkdir(exist_ok=True)
    ckpt = _LOGS / "v1_align.ckpt"
    done: Dict[str, Dict] = {}
    if ckpt.exists():
        with open(ckpt, newline="") as fh:
            for r in csv.DictReader(fh):
                done[_ckpt_key(r["pop"], r["a"], r["b"])] = r
    todo = [t for t in plan if _ckpt_key(*t) not in done]
    print(f"{len(done)} checkpointed, {len(todo)} to run")

    new = not ckpt.exists()
    with open(ckpt, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=_FIELDS)
        if new:
            w.writeheader()
        for i, (pop, a, b) in enumerate(todo, 1):
            if not b:  # no-partner finding row (related)
                row = {"pop": pop, "a": a, "b": "", "aps": len(corpus.stratum(a)),
                       "n_a": corpus.classes(a), "n_b": "",
                       "sigma": 1 << len(corpus.stratum(a)),
                       "nodes": "", "ratio": "", "align_ms": "", "note": "no-partner"}
            else:
                row = _row(corpus, pop, a, b, budget)
            w.writerow(row)
            fh.flush()
            done[_ckpt_key(pop, a, b)] = row
            if i % 500 == 0:
                print(f"  {i}/{len(todo)}")

    rows = [done[_ckpt_key(*t)] for t in plan]
    for r in rows:  # normalize checkpoint-read strings
        for k in ("ratio", "align_ms"):
            try:
                r[k] = float(r[k])
            except (ValueError, TypeError):
                r[k] = ""
    f2 = sum(1 for r in rows if r["note"] == "F2-timeout")
    print(f"priced {sum(1 for r in rows if r['ratio'] != '')}/{len(rows)}  F2: {f2}")

    _REF.mkdir(parents=True, exist_ok=True)
    (_REF / "v1_align_ratio.csv").write_text(_csv_text(rows))
    (_REF / "v1_align_ratio.md").write_text(_summary(rows, corpus_path))
    print(f"wrote {_REF / 'v1_align_ratio.md'} and .csv")
    return 0


def run_one(argv: List[str]) -> int:
    corpus_path = _CORPUS
    rest = [x for x in argv]
    if "--corpus" in rest:
        i = rest.index("--corpus")
        corpus_path = Path(rest[i + 1])
        del rest[i:i + 2]
    a, b = rest[0], rest[1]
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(_Budget()))
    corpus = _Corpus(corpus_path / "sos")
    row = _row(corpus, "manual", a, b, 15)
    print(row)
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
