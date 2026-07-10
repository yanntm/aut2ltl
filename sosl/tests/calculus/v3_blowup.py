"""V3 — Prop 3.4 blow-up, empirically: |𝒞(W·L_n)| ≥ 2^n − 1 (spec §8.7).

    python3 -m tests.calculus.v3_blowup --one N [--budget S]
    python3 -m tests.calculus.v3_blowup --campaign [--budget S] [--max N]

Confirms the syntactic-semigroup blow-up of `W·L_n` for n = 2..5 on directly
built deterministic Emerson–Lei automata (the KNOWN result of `W · L_n`, not a
concatenation implementation), and exhibits the operand size |𝒞(L_n)| beside it.

`L_n` = {ω-words whose a-count before the first `b` is ≡ 0 (mod n)}; `W = Σ*·#·Σ`
opens threads; `W·L_n` accepts iff some `#`-thread has a-count ≡ 0 (mod n) at its
first following `b`. The DELA for `W·L_n`: state = a set `S ⊆ Z_n` of live phase
counters plus an accepting sink `ACC`; from `S`, `a` shifts every phase (+1 mod
n), `#` injects a fresh 0, `b` goes to `ACC` iff `0 ∈ S` else drops all threads.
A run reaches `ACC` iff some thread's a-count hits 0 (mod n) at its first `b` —
membership in `W·L_n`. `Inf(0)` on `ACC`'s self-loops.

Alphabet encoding (trap #9): 2 APs give FOUR valuations, and the fourth is NOT
aliased away — the increment CLASS carries two letters:
`a := (¬p∧¬q) | (p∧q)`, `b := p∧¬q`, `# := ¬p∧q`. Prop 3.4's proof survives
verbatim with a two-letter increment class.

Trap #10: the monoid construction itself may blow the per-case budget at n = 4
or 5 — that enriched monoid IS the entry price this section of the paper is
about. A TIMEOUT (or an algebra-cap None) is a PUBLISHABLE DATUM, recorded on
the states it was exhibited at; the campaign stops at the last n that finished.

Deliverable copied to `reference/calculus/v3_blowup.{md,csv}`.
"""
from __future__ import annotations

import csv
import io
import signal
import subprocess
import sys
import time
from collections import deque
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import buddy
import spot

from sosl.sos.build.importer import canonical
from sosl.sos.core.quotient import invariant_of

_HERE = Path(__file__).resolve().parent
_LOGS = _HERE / "logs"
_REF = _HERE.parents[2] / "reference" / "calculus"
_FIELDS = ["n", "cardinality_Ln", "cardinality_WLn", "bound_2n_minus_1",
           "wl_states", "construct_ms", "note"]


class _Budget(Exception):
    """The per-case watchdog fired (the monoid construction is the entry price)."""


def _git_rev() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=_HERE, text=True).strip()
    except Exception:
        return "unknown"


def _wl_automaton(n: int) -> Tuple[object, int]:
    """The deterministic `W·L_n` automaton; returns it and its reachable-state
    count. States are the reachable subsets `S ⊆ Z_n` (BFS from `∅`) plus `ACC`."""
    aut = spot.make_twa_graph()
    p, q = aut.register_ap("p"), aut.register_ap("q")
    aut.set_acceptance(1, "Inf(0)")
    P, Q = buddy.bdd_ithvar(p), buddy.bdd_ithvar(q)
    a_cls, b_cls, sharp = (-P & -Q) | (P & Q), P & -Q, -P & Q

    idx: Dict[frozenset, int] = {}

    def sid(s: frozenset) -> int:
        got = idx.get(s)
        if got is None:
            got = aut.new_state()
            idx[s] = got
        return got

    start = frozenset()
    aut.set_init_state(sid(start))
    acc = aut.new_state()
    aut.new_edge(acc, acc, buddy.bddtrue, [0])

    seen = {start}
    work = deque([start])
    while work:
        s = work.popleft()
        shift = frozenset((x + 1) % n for x in s)
        injected = s | {0}
        drop = frozenset()
        for t in (shift, injected, drop):
            if t not in seen:
                seen.add(t)
                work.append(t)
        src = sid(s)
        aut.new_edge(src, sid(shift), a_cls)
        aut.new_edge(src, sid(injected), sharp)
        aut.new_edge(src, acc if 0 in s else sid(drop), b_cls)
    return aut, aut.num_states()


def _ln_automaton(n: int) -> object:
    """The deterministic `L_n` operand: a phase counter `c ∈ Z_n`, `a` increments
    it, `#` leaves it, `b` accepts iff `c = 0`. Two sinks; `Inf(0)` on `ACC`."""
    aut = spot.make_twa_graph()
    p, q = aut.register_ap("p"), aut.register_ap("q")
    aut.set_acceptance(1, "Inf(0)")
    P, Q = buddy.bdd_ithvar(p), buddy.bdd_ithvar(q)
    a_cls, b_cls, sharp = (-P & -Q) | (P & Q), P & -Q, -P & Q

    counters = [aut.new_state() for _ in range(n)]
    acc, rej = aut.new_state(), aut.new_state()
    aut.set_init_state(counters[0])
    aut.new_edge(acc, acc, buddy.bddtrue, [0])
    aut.new_edge(rej, rej, buddy.bddtrue)
    for c in range(n):
        aut.new_edge(counters[c], counters[(c + 1) % n], a_cls)
        aut.new_edge(counters[c], counters[c], sharp)
        aut.new_edge(counters[c], acc if c == 0 else rej, b_cls)
    return aut


def _cardinality(aut: object, budget: int) -> Tuple[Optional[int], Optional[float], str]:
    """`|𝒞|` of the automaton's language via `invariant_of ∘ canonical`, under the
    watchdog. Returns (cardinality, ms, note); a fired budget or an algebra-cap
    (None invariant) is the entry-price datum, not a failure."""
    signal.setitimer(signal.ITIMER_REAL, budget)
    try:
        t0 = time.perf_counter()
        inv = invariant_of(canonical(aut))
        ms = round(1000 * (time.perf_counter() - t0), 2)
        if inv is None:
            return None, ms, "CAPPED"
        return inv.n, ms, ""
    except _Budget:
        return None, None, "TIMEOUT"
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def _one(n: int, budget: int) -> Dict:
    ln = _cardinality(_ln_automaton(n), budget)
    wl_aut, wl_states = _wl_automaton(n)
    wl = _cardinality(wl_aut, budget)
    bound = (1 << n) - 1
    note = wl[2] or ln[2]
    row = {"n": n, "cardinality_Ln": ln[0] if ln[0] is not None else "",
           "cardinality_WLn": wl[0] if wl[0] is not None else "",
           "bound_2n_minus_1": bound, "wl_states": wl_states,
           "construct_ms": wl[1] if wl[1] is not None else "", "note": note}
    if wl[0] is not None:
        assert wl[0] >= bound, (
            f"n={n}: |C(W.L_n)|={wl[0]} < 2^n-1={bound} — suspect the encoding "
            f"(trap #9) before Prop 3.4")
    return row


# --- summary ----------------------------------------------------------------

def _summary(rows: List[Dict], budget: int) -> str:
    L: List[str] = []
    L.append("# V3 — Prop 3.4 blow-up: |𝒞(W·L_n)| ≥ 2^n − 1")
    L.append("")
    L.append(f"- date: {date.today().isoformat()}")
    L.append(f"- git: {_git_rev()}")
    L.append(f"- per-case budget: {budget} s (the construction, not Spot)")
    L.append("")
    L.append("Directly built deterministic Emerson–Lei automata; `|𝒞|` via "
             "`invariant_of ∘ canonical`. Encoding (trap #9): the increment class "
             "carries two letters `a := (¬p∧¬q)|(p∧q)`, with `b := p∧¬q`, "
             "`# := ¬p∧q` — Prop 3.4 survives verbatim.")
    L.append("")
    L.append("| n | classes(L_n) | classes(W·L_n) | bound 2^n−1 | W·L_n states | "
             "construct ms |")
    L.append("|---|---|---|---|---|---|")
    for r in rows:
        wl = r["cardinality_WLn"] if r["cardinality_WLn"] != "" else f"**{r['note']}**"
        ms = r["construct_ms"] if r["construct_ms"] != "" else "—"
        L.append(f"| {r['n']} | {r['cardinality_Ln']} | {wl} | "
                 f"{r['bound_2n_minus_1']} | {r['wl_states']} | {ms} |")
    L.append("")
    ok = [r for r in rows if r["cardinality_WLn"] != ""]
    if ok:
        L.append("Every finished row satisfies the bound "
                 "`|𝒞(W·L_n)| ≥ 2^n − 1`, so the syntactic semigroup blows up "
                 "exponentially even though the automaton stays at "
                 f"≤ 2^n + 1 states.")
    stopped = [r for r in rows if r["note"] in ("TIMEOUT", "CAPPED")]
    if stopped:
        s = stopped[0]
        L.append("")
        L.append(f"The construction hit its {'budget' if s['note']=='TIMEOUT' else 'algebra cap'} "
                 f"at n = {s['n']} on a {s['wl_states']}-state automaton: the "
                 f"enriched monoid IS the entry price Prop 3.4 warns of, exhibited "
                 f"— a publishable datum, not a failure. The sweep stops there.")
    L.append("")
    return "\n".join(L)


def _csv_text(rows: List[Dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=_FIELDS)
    w.writeheader()
    for r in sorted(rows, key=lambda r: r["n"]):
        w.writerow({k: r.get(k, "") for k in _FIELDS})
    return buf.getvalue()


# --- drivers ----------------------------------------------------------------

def run_campaign(argv: List[str]) -> int:
    budget, nmax = 15, 5
    it = iter(argv)
    for a in it:
        if a == "--budget":
            budget = int(next(it))
        elif a == "--max":
            nmax = int(next(it))
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(_Budget()))
    rows: List[Dict] = []
    for n in range(2, nmax + 1):
        row = _one(n, budget)
        rows.append(row)
        print(f"n={n}: |C(L_n)|={row['cardinality_Ln']} "
              f"|C(W.L_n)|={row['cardinality_WLn'] or row['note']} "
              f"bound={row['bound_2n_minus_1']} ({row['construct_ms'] or '—'} ms)")
        if row["note"] in ("TIMEOUT", "CAPPED"):
            print(f"  stop: entry price exhibited at n={n}")
            break
    _LOGS.mkdir(exist_ok=True)
    _REF.mkdir(parents=True, exist_ok=True)
    (_REF / "v3_blowup.csv").write_text(_csv_text(rows))
    (_REF / "v3_blowup.md").write_text(_summary(rows, budget))
    print(f"wrote {_REF / 'v3_blowup.md'} and .csv")
    return 0


def run_one(argv: List[str]) -> int:
    budget = 15
    if "--budget" in argv:
        budget = int(argv[argv.index("--budget") + 1])
    n = int(argv[0])
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(_Budget()))
    print(_one(n, budget))
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
