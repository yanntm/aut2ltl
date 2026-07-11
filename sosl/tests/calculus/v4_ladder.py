"""V4 — the classification battery vs Spot over the flat_canon census (spec §9.2).

    python3 -m tests.calculus.v4_ladder --selftest
    python3 -m tests.calculus.v4_ladder --one <basename> [--corpus DIR]
    python3 -m tests.calculus.v4_ladder --campaign [--corpus DIR] [--limit N] [--budget S]

Our side is a scan of the held invariant (`sos.calculus.surgery`): `is_safety` /
`is_cosafety` (the closure/interior fixpoints), `is_obligation` (verdict constant
on each R-class), `obligation_degree` (the Wagner superchain coordinates).

Spot's side runs on the paired deterministic HOA. Spot's Manna-Pnueli
classifiers (`spot.is_obligation`, `is_persistence`, `mp_class`) are
**formula-level**: the formula is a mandatory argument and the automaton is only
an optional accelerator, so they cannot be applied to an automaton-only input.
The automaton-level route used here needs no formula, and is language-level (not
structural) on the corpus's deterministic complete automata:

- safety     `spot.is_safety_automaton(aut)` — "the acceptance condition can be
             set to true without changing the language" (`twaalgos/strength.hh`),
             i.e. the closure fixpoint, decided exactly.
- co-safety  the same test on the complement; `spot.dualize` is an exact
             complement on a deterministic complete automaton.
- obligation `spot.minimize_wdba(aut)` and check equivalence with the input:
             a language is an obligation iff it is WDBA-recognizable. This is
             what Spot's own `ocheck::via_WDBA` does inside `is_obligation`,
             minus the formula.
- degree     no counterpart in Spot; ours-only column.

`--selftest` pins those semantics on eight formulas of known Manna-Pnueli class
(the automaton route must reproduce `spot.mp_class` on the formula), so the
oracle's contract is a rerunnable claim rather than a one-off probe.

Repo discipline (§8.1): per-case watchdog, a checkpoint so a Spot stall loses one
case, deterministic byte-stable output (timing columns aside). Working rows go to
`tests/calculus/logs/`; the validated summary is copied to
`reference/calculus/v4_ladder.{md,csv}`.
"""
from __future__ import annotations

import csv
import io
import signal
import statistics
import subprocess
import sys
import time
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import spot

from sosl.sos import load_invariant
from sosl.sos.calculus import Table
from sosl.sos.calculus.surgery import (
    is_cosafety,
    is_obligation,
    is_safety,
    obligation_degree,
)
from sosl.sos.classify.io import parse_cat

_HERE = Path(__file__).resolve().parent
_LOGS = _HERE / "logs"
_REF = _HERE.parents[2] / "reference" / "calculus"
_CORPUS = _HERE.parents[2] / "genaut" / "corpus" / "flat_canon"

_FIELDS = ["case", "aps", "classes", "ltl",
           "ours_safety", "ours_cosafety", "ours_obligation", "ours_degree",
           "spot_safety", "spot_cosafety", "spot_obligation",
           "agree", "rung",
           "ours_safety_ms", "ours_cosafety_ms", "ours_obl_ms", "ours_deg_ms",
           "spot_safety_ms", "spot_cosafety_ms", "spot_obl_ms", "note"]

# The Manna-Pnueli rung a (safety, cosafety, obligation) triple reads off as.
# 'B' bottom (both), 'S' safety only, 'G' guarantee only, 'O' obligation but
# neither, '-' above the obligation rung.
def _rung(safety: bool, cosafety: bool, obligation: bool) -> str:
    if safety and cosafety:
        return "B"
    if safety:
        return "S"
    if cosafety:
        return "G"
    return "O" if obligation else "-"


class _Budget(Exception):
    """The per-case watchdog fired."""


def _git_rev() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=_HERE, text=True).strip()
    except Exception:
        return "unknown"


def _median_of_7(call: Callable[[], object]) -> Tuple[object, float]:
    """One warmup then the median of 7 timed calls (§8.4). Returns the value and
    the median wall time in ms."""
    return _median_of_7_of(lambda: None, lambda _: call())


def _median_of_7_of(setup: Callable[[], object],
                    call: Callable[[object], object]) -> Tuple[object, float]:
    """`_median_of_7`, with the operand rebuilt outside the timer before each
    repetition. Spot memoizes its verdicts on the automaton object, so a repeat
    on the same object would time a cached property rather than the algorithm;
    the rebuild (a parse) is entry price and is not part of the operation."""
    call(setup())
    times: List[float] = []
    value: object = None
    for _ in range(7):
        operand = setup()
        t0 = time.perf_counter()
        value = call(operand)
        times.append(1000 * (time.perf_counter() - t0))
    return value, statistics.median(times)


# --- the Spot oracle (automaton-level, formula-free) -------------------------


def _complement(aut: "spot.twa_graph") -> "spot.twa_graph":
    """The complement automaton. `dualize` is an exact complement exactly when
    the input is deterministic and complete; on anything else it falls back to
    an alternating automaton that the downstream tests reject. The precondition
    is the corpus's own guarantee, so a violation is a hard error, not a
    silently different measurement."""
    if not (spot.is_deterministic(aut) and spot.is_complete(aut)):
        raise ValueError("complement needs a deterministic complete automaton")
    return spot.dualize(aut)


def spot_safety(aut: "spot.twa_graph") -> bool:
    """Is the automaton's language a safety property? `is_safety_automaton`
    decides "acceptance can be set to true without changing the language",
    which is the closure fixpoint."""
    return spot.is_safety_automaton(aut)


def spot_cosafety(aut: "spot.twa_graph") -> bool:
    """Is the automaton's language co-safety? Safety of the complement."""
    return spot.is_safety_automaton(_complement(aut))


def spot_obligation(aut: "spot.twa_graph") -> bool:
    """Is the automaton's language an obligation property? A language is an
    obligation iff it is WDBA-recognizable, so minimize to a WDBA and check the
    language back (Spot's own `ocheck::via_WDBA`, without the formula)."""
    return spot.minimize_wdba(aut).equivalent_to(aut)


# --- selftest: pin Spot's automaton-level semantics against mp_class ---------

# formula -> Manna-Pnueli class per `spot.mp_class` (B bottom, S safety,
# G guarantee, O obligation, P persistence, R recurrence, T top).
_SELFTEST: Tuple[Tuple[str, str], ...] = (
    ("1", "B"),
    ("0", "B"),
    ("G p", "S"),
    ("F p", "G"),
    ("p U q", "G"),
    ("(G p) | (F q)", "O"),
    ("F G p", "P"),
    ("G F p", "R"),
)


def run_selftest(argv: List[str]) -> int:
    """The automaton route must reproduce, on a deterministic complete
    automaton, the class `spot.mp_class` reads off the formula."""
    print("=== V4 selftest — Spot's automaton-level oracle vs its formula-level "
          "mp_class ===")
    bad = 0
    for text, want in _SELFTEST:
        f = spot.formula(text)
        # "generic" acceptance, not the default Büchi: `deterministic` is only a
        # preference for Büchi output, and F G p is not DBA-realizable, so the
        # translator would hand back a nondeterministic automaton. The corpus's
        # own automata are deterministic complete DELAs, which is what this
        # reproduces.
        aut = spot.translate(f, "deterministic", "complete", "generic")
        got = _rung(spot_safety(aut), spot_cosafety(aut), spot_obligation(aut))
        mpc = spot.mp_class(f)
        # mp_class distinguishes P/R/T above the obligation rung; our triple
        # only sees "not an obligation" there.
        expect = want if want in "BSGO" else "-"
        ok = got == expect and mpc == want
        bad += not ok
        print(f"  {text:12s} mp_class={mpc}  automaton-route={got}  "
              f"expect={expect}  {'ok' if ok else 'MISMATCH'}")
    print("selftest:", "green" if not bad else f"{bad} MISMATCH")
    return 0 if not bad else 1


# --- one census row ---------------------------------------------------------


def _one(basename: str, sos_dir: Path, det_dir: Path, budget: int) -> Dict:
    """One census row: our scans on the held invariant vs Spot on the det HOA."""
    cat = parse_cat((sos_dir / f"{basename}.cat").read_text())
    inv = load_invariant((sos_dir / f"{basename}.sos").read_text())
    table = Table.of(inv)
    pairs = inv.accept
    row: Dict = {"case": basename, "aps": len(inv.alphabet.aps), "classes": inv.n,
                 "ltl": "yes" if cat["ltl"] else "no", "note": ""}

    o_saf, row["ours_safety_ms"] = _median_of_7(lambda: is_safety(table, pairs))
    o_cos, row["ours_cosafety_ms"] = _median_of_7(lambda: is_cosafety(table, pairs))
    o_obl, row["ours_obl_ms"] = _median_of_7(lambda: is_obligation(table, pairs))
    if o_obl:
        deg, row["ours_deg_ms"] = _median_of_7(
            lambda: obligation_degree(table, pairs))
        row["ours_degree"] = f"{deg[0]},{deg[1]}"
    else:
        row["ours_degree"], row["ours_deg_ms"] = "", ""
    row["ours_safety"] = int(o_saf)
    row["ours_cosafety"] = int(o_cos)
    row["ours_obligation"] = int(o_obl)
    row["rung"] = _rung(bool(o_saf), bool(o_cos), bool(o_obl))

    # Spot's props memoize on the automaton object, so every timed call gets a
    # freshly parsed one; the parse itself stays outside the timer (it is the
    # entry price, not the operation).
    hoa = str(det_dir / f"{basename}.hoa")
    fresh = lambda: spot.automaton(hoa)
    signal.setitimer(signal.ITIMER_REAL, budget)
    try:
        s_saf, row["spot_safety_ms"] = _median_of_7_of(fresh, spot_safety)
        s_cos, row["spot_cosafety_ms"] = _median_of_7_of(fresh, spot_cosafety)
        s_obl, row["spot_obl_ms"] = _median_of_7_of(fresh, spot_obligation)
    except _Budget:
        row.update(spot_safety="BUDGET", spot_cosafety="", spot_obligation="",
                   agree="", spot_safety_ms="", spot_cosafety_ms="",
                   spot_obl_ms="", note="F2-timeout")
        return row
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)

    row["spot_safety"] = int(bool(s_saf))
    row["spot_cosafety"] = int(bool(s_cos))
    row["spot_obligation"] = int(bool(s_obl))
    row["agree"] = "yes" if (row["ours_safety"], row["ours_cosafety"],
                             row["ours_obligation"]) == (
        row["spot_safety"], row["spot_cosafety"], row["spot_obligation"]) else "no"
    if row["agree"] == "no":
        disagreeing = [k for k in ("safety", "cosafety", "obligation")
                       if row[f"ours_{k}"] != row[f"spot_{k}"]]
        row["note"] = "F15-" + "+".join(disagreeing)
    return row


# --- the campaign -----------------------------------------------------------


def _cases(sos_dir: Path) -> List[str]:
    return sorted(p.stem for p in sos_dir.glob("*.sos"))


def _num(rows: List[Dict], key: str) -> List[float]:
    out = []
    for r in rows:
        try:
            out.append(float(r[key]))
        except (ValueError, TypeError, KeyError):
            pass
    return out


def _med(rows: List[Dict], key: str) -> float:
    xs = _num(rows, key)
    return statistics.median(xs) if xs else 0.0


def _summary(rows: List[Dict], corpus: Path) -> str:
    """The reference `.md`: the rung census, the agreement matrix per read-off,
    the degree histogram, and the head-to-head timings."""
    n = len(rows)
    f2 = [r for r in rows if r.get("spot_safety") == "BUDGET"]
    scored = [r for r in rows if r not in f2]
    ns = len(scored)
    disagree = [r for r in scored if r.get("agree") == "no"]
    rungs = Counter(r["rung"] for r in rows)
    degs = Counter(r["ours_degree"] for r in rows if r["ours_degree"])

    L: List[str] = []
    L.append(f"date: {date.today().isoformat()}")
    L.append(f"git: {_git_rev()}")
    L.append("seed: full sweep (no sampling)")
    L.append(f"corpus: {corpus.relative_to(_HERE.parents[2])}")
    L.append("")
    L.append("# V4 — the classification battery vs Spot")
    L.append("")
    L.append(f"{n} languages, {ns} scored"
             + (f", {len(f2)} skipped (F2 budget)" if f2 else "") + ". Ours: the "
             "`surgery` scans on the held invariant (warm, median of 7). Spot's: "
             "the automaton-level route on the paired deterministic HOA — "
             "`is_safety_automaton`, the same on `dualize`, and "
             "`minimize_wdba` + equivalence (Spot's Manna-Pnueli classifiers "
             "themselves are formula-level and do not apply to an "
             "automaton-only input).")
    L.append("")
    L.append("## Census — the Manna-Pnueli rungs of `flat_canon`")
    L.append("")
    L.append("| rung | languages | share |")
    L.append("|---|--:|--:|")
    for key, label in (("B", "B — safety ∧ co-safety (bottom)"),
                       ("S", "S — safety only"),
                       ("G", "G — co-safety only (guarantee)"),
                       ("O", "O — obligation, neither"),
                       ("-", "above the obligation rung")):
        L.append(f"| {label} | {rungs[key]} | {100*rungs[key]/n:.1f}% |")
    L.append(f"| **total** | **{n}** | |")
    L.append("")
    obl = sum(rungs[k] for k in "BSGO")
    L.append(f"Obligation languages: **{obl}/{n} = {100*obl/n:.1f}%**.")
    L.append("")
    L.append("A consistency check the census must pass: co-safety is safety of "
             "the complement and the corpus is complement-closed, so the S and "
             f"G counts have to match — S = {rungs['S']}, G = {rungs['G']} "
             + ("(they do; a strict subset of the corpus need not be "
                "complement-closed, so this only binds a full sweep)."
                if rungs["S"] == rungs["G"] else
                "(**they do not** — either the sweep is partial, or the "
                "corpus is not complement-closed; investigate before citing)."))
    L.append("")
    L.append("## Agreement with Spot, per read-off")
    L.append("")
    L.append("| read-off | agree | disagree | ours true | Spot true |")
    L.append("|---|--:|--:|--:|--:|")
    for key, label in (("safety", "`is_safety`"),
                       ("cosafety", "`is_cosafety`"),
                       ("obligation", "`is_obligation`")):
        ag = sum(1 for r in scored if r[f"ours_{key}"] == r[f"spot_{key}"])
        ot = sum(1 for r in scored if int(r[f"ours_{key}"]))
        st = sum(1 for r in scored if int(r[f"spot_{key}"]))
        L.append(f"| {label} | {ag} | {ns - ag} | {ot} | {st} |")
    L.append("")
    rate = 100 * (ns - len(disagree)) / ns if ns else 0.0
    L.append(f"Full-triple agreement: **{ns - len(disagree)}/{ns} = {rate:.2f}%**"
             f"{' (perfect)' if not disagree else ''}.")
    L.append("")
    L.append("`obligation_degree` has no Spot counterpart — Spot decides the "
             "obligation rung but does not measure the Wagner superchain "
             "coordinates. The column is ours-only.")
    L.append("")
    L.append("## Obligation degree — the histogram (ours-only)")
    L.append("")
    L.append("| degree (n⁺, n⁻) | languages | rungs |")
    L.append("|---|--:|---|")
    for d, c in sorted(degs.items(),
                       key=lambda kv: tuple(int(x) for x in kv[0].split(","))):
        at = sorted({r["rung"] for r in rows if r["ours_degree"] == d})
        L.append(f"| ({d.replace(',', ', ')}) | {c} | {' '.join(at)} |")
    L.append("")
    flip = lambda d: ",".join(reversed(d.split(",")))
    sym = all(degs[d] == degs.get(flip(d), 0) for d in degs)
    L.append("A second consistency check, free from the same sweep: complement "
             "swaps the two polarities of the superchain, so on a "
             "complement-closed corpus the histogram must be symmetric under "
             "`(n⁺, n⁻) ↦ (n⁻, n⁺)` — "
             + ("it is, on every entry."
                if sym else
                "**it is not**; investigate before citing."))
    L.append("")
    L.append("## Head-to-head timings (ms, median of 7 per case, then the "
             "median over cases)")
    L.append("")
    L.append("| read-off | ours | Spot | Spot / ours |")
    L.append("|---|--:|--:|--:|")
    for key, label, skey in (("safety", "safety", "spot_safety_ms"),
                             ("cosafety", "co-safety", "spot_cosafety_ms"),
                             ("obligation", "obligation", "spot_obl_ms")):
        okey = {"safety": "ours_safety_ms", "cosafety": "ours_cosafety_ms",
                "obligation": "ours_obl_ms"}[key]
        om, sm = _med(scored, okey), _med(scored, skey)
        ratio = f"{sm/om:.2f}×" if om else "—"
        L.append(f"| {label} | {om:.4f} | {sm:.4f} | {ratio} |")
    dm = _med([r for r in scored if r["ours_degree"]], "ours_deg_ms")
    L.append(f"| degree | {dm:.4f} | — | — |")
    L.append("")
    L.append("Ours are warm scans of a held object; Spot's are calls on a "
             "deterministic automaton it has already parsed (the parse is "
             "outside the timer on both sides). Python against C++ — the ratio "
             "is corroboration of the asymptotics, not a benchmark claim: the "
             "scans are linear in the table, while `dualize` and "
             "`minimize_wdba` + equivalence build and compare automata.")
    L.append("")
    L.append("## Disagreement dossier")
    L.append("")
    if not disagree:
        L.append("None — the algebraic read-offs and Spot's automaton-level "
                 "oracle agree on every scored language, on all three verdicts.")
    else:
        for r in sorted(disagree, key=lambda r: r["case"]):
            L.append(f"- **{r['case']}** ({r['note']}) — ours "
                     f"S/G/O = {r['ours_safety']}/{r['ours_cosafety']}/"
                     f"{r['ours_obligation']}, Spot "
                     f"{r['spot_safety']}/{r['spot_cosafety']}/"
                     f"{r['spot_obligation']}.")
    if f2:
        L.append("")
        L.append("## F2 — blown budgets")
        L.append("")
        for r in sorted(f2, key=lambda r: r["case"]):
            L.append(f"- `{r['case']}` — Spot exceeded the per-case budget.")
    L.append("")
    return "\n".join(L)


def _csv_text(rows: List[Dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=_FIELDS)
    w.writeheader()
    for r in sorted(rows, key=lambda r: r["case"]):
        w.writerow({k: r.get(k, "") for k in _FIELDS})
    return buf.getvalue()


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
    ckpt = _LOGS / "v4_ladder.ckpt"
    done: Dict[str, Dict] = {}
    if ckpt.exists():
        with open(ckpt, newline="") as fh:
            for r in csv.DictReader(fh):
                done[r["case"]] = r

    cases = _cases(sos_dir)
    if limit is not None:
        cases = cases[:limit]
    todo = [c for c in cases if c not in done]
    print(f"=== V4 ladder: {len(cases)} cases, {len(done)} checkpointed, "
          f"{len(todo)} to run ===")

    new = not ckpt.exists()
    with open(ckpt, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=_FIELDS)
        if new:
            w.writeheader()
        for i, basename in enumerate(todo, 1):
            row = _one(basename, sos_dir, det_dir, budget)
            w.writerow({k: row.get(k, "") for k in _FIELDS})
            fh.flush()
            done[basename] = row
            if i % 500 == 0:
                print(f"  {i}/{len(todo)}")

    rows = [done[c] for c in cases]
    disagree = sum(1 for r in rows if r.get("agree") == "no")
    f2 = sum(1 for r in rows if r.get("spot_safety") == "BUDGET")
    print(f"agreement: {sum(1 for r in rows if r.get('agree') == 'yes')}/"
          f"{len(rows) - f2}  disagreements: {disagree}  F2: {f2}")

    _REF.mkdir(parents=True, exist_ok=True)
    (_REF / "v4_ladder.csv").write_text(_csv_text(rows))
    (_REF / "v4_ladder.md").write_text(_summary(rows, corpus))
    print(f"wrote {_REF / 'v4_ladder.md'} and .csv")
    return 0 if disagree == 0 else 1


def run_one(argv: List[str]) -> int:
    corpus = _CORPUS
    basename = argv[0]
    if "--corpus" in argv:
        corpus = Path(argv[argv.index("--corpus") + 1])
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(_Budget()))
    row = _one(basename, corpus / "sos", corpus / "det", 10)
    for k in _FIELDS:
        print(f"  {k:18s} {row.get(k, '')}")
    return 0 if row.get("agree") != "no" else 1


def main(argv: List[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    if argv[0] == "--selftest":
        return run_selftest(argv[1:])
    if argv[0] == "--campaign":
        return run_campaign(argv[1:])
    if argv[0] == "--one":
        return run_one(argv[1:])
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
