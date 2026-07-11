"""GT2 acceptance — the ladder gates (spec §4).

    python3 -m tests.giventhat.ladder_gate --rung-oracle [--corpus DIR] [--limit N]
    python3 -m tests.giventhat.ladder_gate --one <basename> [--corpus DIR]
    python3 -m tests.giventhat.ladder_gate --fixture [--force]
    python3 -m tests.giventhat.ladder_gate --pair <neg_phi> <k> [--corpus DIR]
    python3 -m tests.giventhat.ladder_gate --campaign [--corpus DIR]
                                           [--budget S] [--limit N]

Gate 1, the corpus rung oracle (run FIRST, before any interval work): over
every corpus invariant, the GT2 chain read-offs against the `.cat` sidecar's
Wagner coordinates —

    is_recurrence(P)  == (m+ <= 0)      is_persistence(P) == (m- <= 0)

The two sides share `classify.primitives`' H-order but decide by different
paths (direct violation scan here, the chain DP of `classify.chains` behind
the sidecars). The paper hand-checked the orientation on four examples; the
corpus decides it (spec T1). Green: proceed. Consistently flipped (agreement
~0 as stated, ~1 under the swap): implement the swap, file finding F5.
Mixed: STOP, report the smallest disagreeing case.

Per pair `(neg_phi, K)`, the remaining gates (spec §4 gates 2-5):

2. hull laws — `rec_hull` extensive / monotone / idempotent on seeded random
   saturated pair sets (unions of conjugacy classes), output saturated,
   `is_recurrence` on the output, fixpoint iff already a recurrence; plus the
   `r_classes` one-liner (they partition the linked stems);
3. the brute lattice oracle — on `iv.bits <= 12`, enumerate ALL `2^bits`
   choices; per rung, `exists_*` equals `any(is_*)` over the enumeration
   (CAL5/GT2 predicates on the raw chosen pair set), the returned member is
   the intersection (Moore rungs) resp. union (kernel rungs) of the
   enumerated members and is itself enumerated; `bits > 12` skipped, recorded;
4. witness discipline — on no, the refusal lasso replays via `member` on the
   table (in the constraining hull, outside `P_max` — dually inside `P_min`)
   and against the det HOAs (bounded);
5. `--fixture` — the paper §4.6 worked example (`ltl2tgba` + canonize, cached
   by `fixtures.build_gt2`): every hand-computed prediction is checked and a
   mismatch is an E1 escalation block, printed verbatim for the report.

Repo discipline: 15 s per-case watchdog, checkpoint file so a stall loses one
case, logs under `tests/giventhat/logs/` (never /tmp).
"""
from __future__ import annotations

import csv
import random
import signal
import subprocess
import sys
import time
import zlib
from datetime import date
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from sosl.sos import dump_invariant, load_invariant
from sosl.sos.alphabet import Alphabet, Letter
from sosl.sos.calculus import Table
from sosl.sos.calculus.decide import member
from sosl.sos.calculus.reduce import reduce
from sosl.sos.calculus.surgery import (
    complement,
    conjugacy_classes,
    interior,
    inverse_substitution,
    is_cosafety,
    is_obligation,
    is_safety,
    is_saturated,
    r_classes,
    safety_closure,
)
from sosl.sos.calculus.table import PairSet
from sosl.sos.calculus.witness import Witness
from sosl.sos.classify.io import parse_cat
from sosl.sos.giventhat import (
    Interval,
    choose,
    exists_cosafety,
    exists_obligation,
    exists_persistence,
    exists_recurrence,
    exists_safety,
    forced,
    given_that,
    k_refutes_phi,
    k_settles_phi,
)
from sosl.sos.giventhat.ladder import is_persistence, is_recurrence, rec_hull
from sosl.sos.invariant import Invariant
from sosl.sos.lasso import Lasso
from sosl.teacher.whitebox import HoaTeacher

from tests.calculus.v1_align import _Corpus
from tests.giventhat import fixtures
from tests.giventhat.interval_gate import _sample_pairs

_HERE = Path(__file__).resolve().parent
_LOGS = _HERE / "logs"
_CORPUS = _HERE.parents[2] / "genaut" / "corpus" / "flat_canon"
_SEED = 20260711

_FIELDS = ["case", "aps", "classes", "m_plus", "m_minus",
           "rec_ours", "rec_cat", "per_ours", "per_cat", "agree", "ms", "note"]

_BUDGET_S = 15


class _Budget(Exception):
    """The per-case watchdog fired."""


def _git_rev() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=_HERE, text=True).strip()
    except Exception:
        return "unknown"


def _one_rung(basename: str, sos_dir: Path) -> Dict:
    """One oracle row: the chain read-offs vs the `.cat` coordinates."""
    cat = parse_cat((sos_dir / f"{basename}.cat").read_text())
    m_plus, m_minus = cat["coords"][0], cat["coords"][1]
    inv = load_invariant((sos_dir / f"{basename}.sos").read_text())
    row: Dict = {"case": basename, "aps": len(inv.alphabet.aps), "classes": inv.n,
                 "m_plus": m_plus, "m_minus": m_minus, "note": ""}
    signal.setitimer(signal.ITIMER_REAL, _BUDGET_S)
    try:
        t0 = time.perf_counter()
        table = Table.of(inv)
        rec = is_recurrence(table, inv.accept)
        per = is_persistence(table, inv.accept)
        row["ms"] = round(1000 * (time.perf_counter() - t0), 2)
    except _Budget:
        row.update(rec_ours="BUDGET", rec_cat="", per_ours="", per_cat="",
                   agree="", ms="", note="F2-timeout")
        return row
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    rec_cat, per_cat = m_plus <= 0, m_minus <= 0
    row.update(rec_ours=int(rec), rec_cat=int(rec_cat),
               per_ours=int(per), per_cat=int(per_cat),
               agree="yes" if (rec == rec_cat and per == per_cat) else "no")
    if row["agree"] == "no":
        row["note"] = ("swap-consistent"
                       if (rec == per_cat and per == rec_cat) else "mixed")
    return row


def _summary_rung(rows: List[Dict], corpus: Path) -> str:
    """Verdict block: agreement as stated, agreement under the swapped
    orientation, and the smallest disagreeing cases."""
    scored = [r for r in rows if r["agree"] in ("yes", "no")]
    stated = sum(1 for r in scored if int(r["rec_ours"]) == int(r["rec_cat"])
                 and int(r["per_ours"]) == int(r["per_cat"]))
    swapped = sum(1 for r in scored if int(r["rec_ours"]) == int(r["per_cat"])
                  and int(r["per_ours"]) == int(r["rec_cat"]))
    budget = [r for r in rows if r["note"] == "F2-timeout"]
    disagree = sorted((r for r in scored if r["agree"] == "no"),
                      key=lambda r: (int(r["classes"]), r["case"]))
    L: List[str] = []
    L.append(f"date: {date.today().isoformat()}")
    L.append(f"git: {_git_rev()}")
    L.append("seed: full sweep (no sampling)")
    L.append(f"corpus: {corpus}")
    L.append("")
    L.append("# GT2 gate 1 — the corpus rung oracle")
    L.append("")
    L.append(f"{len(rows)} cases, {len(scored)} scored"
             + (f", {len(budget)} F2-timeout" if budget else "") + ".")
    L.append(f"- agreement as stated:  {stated}/{len(scored)}")
    L.append(f"- agreement under swap: {swapped}/{len(scored)}")
    if not disagree:
        L.append("- verdict: **GREEN** — the paper's orientation holds on the corpus.")
    elif stated == 0 and swapped == len(scored):
        L.append("- verdict: **CONSISTENT FLIP** — implement the swap, file F5.")
    else:
        L.append("- verdict: **MIXED** — STOP (spec T1); smallest cases below.")
        for r in disagree[:10]:
            L.append(f"  - {r['case']} (n={r['classes']}): "
                     f"rec {r['rec_ours']} vs m+={r['m_plus']}, "
                     f"per {r['per_ours']} vs m-={r['m_minus']}")
    L.append("")
    return "\n".join(L)


def run_rung_oracle(argv: List[str]) -> int:
    corpus, limit = _CORPUS, None
    it = iter(argv)
    for a in it:
        if a == "--corpus":
            corpus = Path(next(it))
        elif a == "--limit":
            limit = int(next(it))
    sos_dir = corpus / "sos"

    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(_Budget()))
    _LOGS.mkdir(exist_ok=True)
    ckpt = _LOGS / "rung_oracle.ckpt"
    done: Dict[str, Dict] = {}
    if ckpt.exists():
        with open(ckpt, newline="") as fh:
            for r in csv.DictReader(fh):
                done[r["case"]] = r

    cases = sorted(p.stem for p in sos_dir.glob("*.sos"))
    if limit is not None:
        cases = cases[:limit]
    todo = [c for c in cases if c not in done]
    print(f"=== GT2 rung oracle: {len(cases)} cases, {len(done)} checkpointed, "
          f"{len(todo)} to run ===")

    new = not ckpt.exists()
    with open(ckpt, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=_FIELDS)
        if new:
            w.writeheader()
        for i, basename in enumerate(todo, 1):
            row = _one_rung(basename, sos_dir)
            w.writerow(row)
            fh.flush()
            done[basename] = row
            if i % 500 == 0:
                print(f"  {i}/{len(todo)}")

    rows = [done[c] for c in cases]
    text = _summary_rung(rows, corpus)
    (_LOGS / "rung_oracle.md").write_text(text)
    print(text)
    disagree = sum(1 for r in rows if r.get("agree") == "no")
    return 0 if disagree == 0 else 1


def run_one(argv: List[str]) -> int:
    corpus = _CORPUS
    basename = argv[0]
    if "--corpus" in argv:
        corpus = Path(argv[argv.index("--corpus") + 1])
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(_Budget()))
    row = _one_rung(basename, corpus / "sos")
    print(row)
    return 0 if row.get("agree") == "yes" else 1


# --- the per-pair ladder gates (spec §4 gates 2-4) ----------------------------

# rung name, existence test, membership predicate, member kind
_RUNGS: List[Tuple[str, Callable[[Interval], Tuple], Callable, str]] = [
    ("safety", exists_safety, is_safety, "least"),
    ("cosafety", exists_cosafety, is_cosafety, "greatest"),
    ("obligation", exists_obligation, is_obligation, "least"),
    ("recurrence", exists_recurrence, is_recurrence, "least"),
    ("persistence", exists_persistence, is_persistence, "greatest"),
]


def _gate_r_partition(iv: Interval) -> None:
    """The `r_classes` one-liner: they partition the linked stems."""
    classes = r_classes(iv.table)
    stems = {s for (s, e) in iv.table.linked}
    assert sum(len(r) for r in classes) == len(stems), "R-classes overlap"
    covered = frozenset().union(*classes) if classes else frozenset()
    assert covered == stems, "R-classes do not cover the linked stems"


def _gate_hull_laws(iv: Interval, rng: random.Random, rounds: int = 6) -> None:
    """Spec §4 gate 2: `rec_hull` is a closure operator landing on
    recurrences, on seeded random saturated pair sets."""
    table = iv.table
    classes = conjugacy_classes(table)
    for _ in range(rounds):
        q: PairSet = frozenset().union(
            *(c for c in classes if rng.random() < 0.4)) if classes else frozenset()
        h = rec_hull(table, q)
        assert q <= h, "rec_hull not extensive"
        assert is_saturated(table, h), "rec_hull output not saturated"
        assert is_recurrence(table, h), "rec_hull output not a recurrence"
        assert rec_hull(table, h) == h, "rec_hull not idempotent"
        assert (h == q) == is_recurrence(table, q), \
            "rec_hull fixpoint iff is_recurrence fails"
        extra = [c for c in classes if not c <= q]
        if extra:
            q2 = q | extra[rng.randrange(len(extra))]
            assert h <= rec_hull(table, q2), "rec_hull not monotone"


def _gate_brute(iv: Interval) -> str:
    """Spec §4 gate 3: the exactness oracle. On `bits <= 12` enumerate ALL
    `2^bits` choices; per rung, existence and the member's extremality are
    checked literally against the enumeration. Returns 'ok' or 'skip-bits'
    (never raise the cap — spec trap #6)."""
    if iv.bits > 12:
        return "skip-bits"
    agg: Dict[str, Dict] = {
        name: {"any": False, "inter": None, "union": frozenset(), "seen": False}
        for name, _, _, _ in _RUNGS}
    answers = {name: fn(iv) for name, fn, _, _ in _RUNGS}
    for mask in range(1 << iv.bits):
        b = choose(iv, [i for i in range(iv.bits) if mask >> i & 1], check=False)
        for name, _, is_fn, _ in _RUNGS:
            if is_fn(iv.table, b):
                a = agg[name]
                a["any"] = True
                a["inter"] = b if a["inter"] is None else a["inter"] & b
                a["union"] = a["union"] | b
                if answers[name][1] is not None and b == answers[name][1]:
                    a["seen"] = True
    for name, _, _, kind in _RUNGS:
        ok, memb, _ = answers[name]
        a = agg[name]
        assert ok == a["any"], f"{name}: exists={ok} but enumeration says {a['any']}"
        if ok:
            assert a["seen"], f"{name}: returned member is not an enumerated member"
            want = a["inter"] if kind == "least" else a["union"]
            assert memb == want, f"{name}: member is not the {kind} enumerated one"
    return "ok"


def _gate_witnesses(iv: Interval, det_phi: Optional[HoaTeacher],
                    det_k: Optional[HoaTeacher]) -> None:
    """Spec §4 gate 4: every refusal replays — via `member` on the table
    (always) and against the paired det HOAs (bounded). Moore rungs: the
    lasso is in the constraining hull and outside `L(P_max)`; kernel rungs:
    inside `L(P_min)` and outside the kernel object."""
    table = iv.table
    hulls: Dict[str, PairSet] = {}
    f1, _ = forced(iv)
    stems1 = frozenset().union(*f1) if f1 else frozenset()
    hulls["safety"] = safety_closure(table, iv.p_min)
    hulls["obligation"] = frozenset(p for p in table.linked if p[0] in stems1)
    hulls["recurrence"] = rec_hull(table, iv.p_min)
    hulls["cosafety"] = interior(table, iv.p_max)
    hulls["persistence"] = rec_hull(table, complement(table, iv.p_max))

    for name, fn, _, kind in _RUNGS:
        ok, _, refusal = fn(iv)
        if ok:
            assert refusal is None, f"{name}: yes with a refusal"
            continue
        assert refusal is not None, f"{name}: no without a refusal"
        w: Witness = refusal
        las = w.lasso
        if kind == "least":  # Moore: in hull(P_min)-side, outside L(P_max)
            assert member(table, hulls[name], las), f"{name}: refusal not in hull"
            w.replay(lambda stem, loop: member(table, iv.p_max, Lasso(stem, loop)))
            if det_phi is not None and det_k is not None:
                # outside P_max = neg_phi | K^c: not in L(neg_phi), in L(K)
                assert not det_phi.member(las), f"{name}: det(neg_phi) accepts refusal"
                assert det_k.member(las), f"{name}: det(K) rejects refusal"
        else:  # kernel: in L(P_min), outside the kernel object
            w.replay(lambda stem, loop: member(table, iv.p_min, Lasso(stem, loop)))
            outside = (not member(table, hulls[name], las)) if name == "cosafety" \
                else member(table, hulls[name], las)  # persistence: IN the flip hull
            assert outside, f"{name}: refusal does not convict the kernel"
            if det_phi is not None and det_k is not None:
                # in P_min = neg_phi & K
                assert det_phi.member(las), f"{name}: det(neg_phi) rejects refusal"
                assert det_k.member(las), f"{name}: det(K) rejects refusal"


def check_ladder_pair(inv_phi: Invariant, inv_k: Invariant,
                      det_phi_path: Optional[Path], det_k_path: Optional[Path],
                      seed: int) -> Dict:
    """Gates 2-4 on one `(neg_phi, K)` pair; returns the census row."""
    rng = random.Random(seed)
    t0 = time.perf_counter()
    iv = given_that(inv_phi, inv_k)
    _gate_r_partition(iv)
    _gate_hull_laws(iv, rng)
    det_phi = HoaTeacher.of_hoa(str(det_phi_path)) if det_phi_path else None
    det_k = HoaTeacher.of_hoa(str(det_k_path)) if det_k_path else None
    _gate_witnesses(iv, det_phi, det_k)
    brute = _gate_brute(iv)
    row: Dict = {"bits": iv.bits, "brute": brute,
                 "ms": round(1000 * (time.perf_counter() - t0), 1), "note": ""}
    for name, fn, _, _ in _RUNGS:
        row[name] = int(fn(iv)[0])
    return row


# --- the worked-example fixture (spec §4 gate 5, paper §4.6) -------------------


def _extend(inv: Invariant, alphabet: Alphabet) -> Invariant:
    """`inv` reinterpreted over the larger `alphabet` (new letters map by
    dropping the APs `inv` does not know), canonically reduced — the sanctioned
    adapter for the fixture's per-formula AP sets."""
    if inv.alphabet.aps == alphabet.aps:
        return inv
    table = Table.of(inv)
    keep = set(inv.alphabet.aps)

    def pi(a: Letter) -> Letter:
        return inv.alphabet.letter_of(
            [ap for ap in alphabet.true_aps(a) if ap in keep])

    t2, moved = inverse_substitution(table, inv.accept, alphabet, pi)
    return reduce(t2, moved)


def run_fixture(argv: List[str]) -> int:
    """Every §4.6 hand computation, checked; mismatches are E1 escalation
    lines (encoding and canonize already vetted by construction), printed
    verbatim for the report — never patched here."""
    fx = fixtures.build_gt2(force="--force" in argv)
    alph = Alphabet.of(("a", "b", "c"))
    inv = {name: _extend(load_invariant(p.read_text()), alph)
           for name, p in fx.sos.items()}
    escal: List[str] = []

    def expect(label: str, got, want) -> None:
        line = f"{label}: got {got}, paper says {want}"
        if got == want:
            print(f"  ok: {label} = {want}")
        else:
            escal.append(line)
            print(f"  E1: {line}")

    def lasso_str(w: Optional[Witness]) -> str:
        if w is None:
            return "None"
        render = lambda word: "".join(
            "{" + ",".join(alph.true_aps(a)) + "}" for a in word)
        return f"{render(w.stem)}({render(w.loop)})^w"

    render_w = lambda word: "".join(
        "{" + ",".join(alph.true_aps(a)) + "}" for a in word) or "eps"
    np = inv["negphi"]
    t_np = Table.of(np)
    print("== machine census of I(neg_phi) over {a,b,c} "
          "(the count the paper's §4.6 arithmetic must reproduce) ==")
    for c in range(np.n):
        loops = sorted(e for (s, e) in t_np.linked if s == c)
        acc = sorted(e for e in loops if (c, e) in np.accept)
        idem = "  idem" if np.mult[c][c] == c else ""
        print(f"  class {c}: key {render_w(np.keys[c])}{idem}  "
              f"loops {loops}  accepting {acc}")
    print(f"  linked pairs: {len(t_np.linked)}; accept: {sorted(np.accept)}")

    print("== paper §4.6 predictions ==")
    expect("|C(neg_phi)|", inv["negphi"].n, 7)
    expect("|C(K)|", inv["k"].n, 4)
    iv = given_that(inv["negphi"], inv["k"])
    expect("product table classes", iv.table.n, 13)

    settles, w1 = k_settles_phi(iv)
    refutes, w2 = k_refutes_phi(iv)
    expect("k_settles_phi", settles, False)
    expect("settle witness", lasso_str(w1), "({a,b,c})^w")
    expect("k_refutes_phi", refutes, False)
    expect("refute witness", lasso_str(w2), "({b,c})^w")

    ok_s, _, ref_s = exists_safety(iv)
    expect("exists_safety", ok_s, False)
    expect("safety refusal", lasso_str(ref_s), "({b,c})^w")

    ok_c, kernel, _ = exists_cosafety(iv)
    expect("exists_cosafety", ok_c, True)
    if ok_c and kernel is not None:
        expect("kernel reduce == I(F(a | !c))",
               dump_invariant(reduce(iv.table, kernel)) == dump_invariant(inv["ref_open"]),
               True)
        # The least co-safety superset of P_min: open sets are exactly the
        # pair sets whose stems form a right ideal, so the least one is all
        # linked pairs whose stem is a right multiple of a P_min stem (one
        # row pass; the band is 25 bits here, the spec's 2^bits enumeration
        # is out of reach).
        ideal = set()
        for s in {p[0] for p in iv.p_min}:
            ideal.update(iv.table.mult[s])
        least: PairSet = frozenset(p for p in iv.table.linked if p[0] in ideal)
        assert is_cosafety(iv.table, least), "open hull is not co-safety"
        assert iv.p_min <= least <= iv.p_max, "open hull left the interval"
        expect("least co-safety member == I(F(a & c))",
               dump_invariant(reduce(iv.table, least)) == dump_invariant(inv["ref_least"]),
               True)

    t_phi = Table.of(inv["negphi"])
    p_phi = inv["negphi"].accept
    expect("is_recurrence(P_neg_phi)", is_recurrence(t_phi, p_phi), True)
    expect("is_persistence(P_neg_phi)", is_persistence(t_phi, p_phi), False)
    expect("is_obligation(P_neg_phi)", is_obligation(t_phi, p_phi), False)

    print("== gates 2-4 on the fixture pair ==")
    row = check_ladder_pair(inv["negphi"], inv["k"], None, None, _SEED)
    print(f"  {row}")

    if escal:
        print("\n== E1 ESCALATION (to the report, verbatim) ==")
        for line in escal:
            print(f"- {line}")
        return 1
    print("SUCCESS")
    return 0


# --- one corpus pair / the campaign -------------------------------------------


def _pair_row(corpus: _Corpus, det_dir: Path, pop: str, a: str, b: str,
              budget: int) -> Dict:
    row: Dict = {"pop": pop, "neg_phi": a, "k": b}
    seed = zlib.crc32(f"{_SEED}|ladder|{a}|{b}".encode())
    signal.setitimer(signal.ITIMER_REAL, budget)
    try:
        got = check_ladder_pair(corpus.inv(a), corpus.inv(b),
                                det_dir / f"{a}.hoa", det_dir / f"{b}.hoa", seed)
        row.update(got)
    except _Budget:
        row.update(bits="", brute="", ms="", note="F2-budget",
                   **{name: "" for name, _, _, _ in _RUNGS})
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    return row


def run_pair(argv: List[str]) -> int:
    corpus_dir = _CORPUS
    if "--corpus" in argv:
        i = argv.index("--corpus")
        corpus_dir = Path(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    a, b = argv[0], argv[1]
    corpus = _Corpus(corpus_dir / "sos")
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(_Budget()))
    row = _pair_row(corpus, corpus_dir / "det", "one", a, b, _BUDGET_S)
    print(row)
    print("SUCCESS" if row["note"] == "" else f"note: {row['note']}")
    return 0


_PAIR_FIELDS = ["pop", "neg_phi", "k", "bits",
                *(name for name, _, _, _ in _RUNGS), "brute", "ms", "note"]


def run_campaign(argv: List[str]) -> int:
    corpus_dir, limit, budget = _CORPUS, None, _BUDGET_S
    it = iter(argv)
    for a in it:
        if a == "--corpus":
            corpus_dir = Path(next(it))
        elif a == "--limit":
            limit = int(next(it))
        elif a == "--budget":
            budget = int(next(it))

    corpus = _Corpus(corpus_dir / "sos")
    rng = random.Random(_SEED)
    plan = _sample_pairs(corpus, rng, 300, 100)  # the GT1 populations, same seed
    if limit is not None:
        plan = plan[:limit]

    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(_Budget()))
    _LOGS.mkdir(exist_ok=True)
    ckpt = _LOGS / "ladder_campaign.ckpt"
    done: Dict[Tuple[str, str, str], Dict] = {}
    if ckpt.exists():
        with open(ckpt, newline="") as fh:
            for r in csv.DictReader(fh):
                done[(r["pop"], r["neg_phi"], r["k"])] = r

    todo = [(pop, a, b) for pop, a, b in plan if (pop, a, b) not in done]
    print(f"=== GT2 ladder campaign: {len(plan)} pairs, {len(done)} checkpointed, "
          f"{len(todo)} to run (seed {_SEED}) ===")

    fresh = not ckpt.exists()
    with open(ckpt, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=_PAIR_FIELDS)
        if fresh:
            w.writeheader()
        for i, (pop, a, b) in enumerate(todo, 1):
            row = _pair_row(corpus, corpus_dir / "det", pop, a, b, budget)
            w.writerow({k: row.get(k, "") for k in _PAIR_FIELDS})
            fh.flush()
            done[(pop, a, b)] = row
            if i % 50 == 0:
                print(f"  {i}/{len(todo)}")

    rows = [done[key] for key in plan]
    with open(_LOGS / "gt2_ladder.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=_PAIR_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in _PAIR_FIELDS})

    scored = [r for r in rows if r["note"] == ""]
    f2 = len(rows) - len(scored)
    bruted = sum(1 for r in scored if r["brute"] == "ok")
    print(f"scored {len(scored)}/{len(rows)} (F2 skips: {f2}); "
          f"brute oracle ran on {bruted} (bits <= 12), "
          f"skipped {sum(1 for r in scored if r['brute'] == 'skip-bits')}")
    for name, _, _, _ in _RUNGS:
        yes = sum(1 for r in scored if str(r[name]) == "1")
        print(f"  exists_{name}: {yes}/{len(scored)}")
    print(f"wrote {_LOGS / 'gt2_ladder.csv'}")
    print("SUCCESS" if all(r["note"] in ("", "F2-budget") for r in rows) else "FAILURE")
    return 0


def main(argv: List[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    if argv[0] == "--rung-oracle":
        return run_rung_oracle(argv[1:])
    if argv[0] == "--one":
        return run_one(argv[1:])
    if argv[0] == "--fixture":
        return run_fixture(argv[1:])
    if argv[0] == "--pair":
        return run_pair(argv[1:])
    if argv[0] == "--campaign":
        return run_campaign(argv[1:])
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
