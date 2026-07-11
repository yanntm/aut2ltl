"""GT1 acceptance gate (spec §3.6): the interval object against its laws.

    cd sosl && python3 -m tests.giventhat.interval_gate --fixture
    python3 -m tests.giventhat.interval_gate --one <neg_phi> <k> [--corpus DIR]
    python3 -m tests.giventhat.interval_gate --campaign [--corpus DIR]
                                             [--budget S] [--limit N]

Per pair `(neg_phi, K)`, all four gates:

1. metamorphic endpoints — `member(p_min/p_max)` on the product table equals
   the AND / OR-NOT combination of memberships on the ORIGINAL two invariants
   (exhaustive lassos `|u|,|v| <= 3` on small alphabets, >= 500 sampled
   otherwise) — the check that crosses the align/materialize boundary;
2. endpoint cross-oracle — `k_settles_phi` vs `intersecting_word`,
   `k_refutes_phi` vs `included(K <= neg_phi)`, witnesses replayed against the
   paired det HOAs (bounded);
3. Prop 3.1 law (asserted inside `given_that`) + the conjugacy gate: classes
   partition `linked`, `saturate({p})` recovers each class, every saturated
   pair set met is a union of classes;
4. choice laws — `choose(empty) == p_min`, `choose(all) == p_max`,
   `decompose . choose == id`, monotonicity; 20 seeded subsets.

`--fixture` additionally asserts the spec §3.5 expected facts on the
`D_ab` / `D_K` pair and prints the recorded data. `--campaign` runs the
700-pair corpus sampling (spec §3.6.5, seed 20260711): 300 same-stratum pairs
+ the 300 reversed + 100 complement partners; checkpointed, 15 s per case;
the `|F|` distribution lands in `logs/gt1_bits.csv` (report slot F3).
"""
from __future__ import annotations

import csv
import itertools
import random
import signal
import sys
import time
import zlib
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from sosl.sos import load_invariant
from sosl.sos.calculus import Table, align
from sosl.sos.calculus.decide import included, intersecting_word, member
from sosl.sos.calculus.surgery import conjugacy_classes, saturate
from sosl.sos.calculus.witness import Witness
from sosl.sos.giventhat import Interval, choose, decompose, given_that, k_refutes_phi, k_settles_phi
from sosl.sos.invariant import Invariant
from sosl.sos.lasso import Lasso
from sosl.teacher.whitebox import HoaTeacher

from tests.calculus.v1_align import _Corpus
from tests.giventhat import fixtures

_HERE = Path(__file__).resolve().parent
_LOGS = _HERE / "logs"
_CORPUS = _HERE.parents[2] / "genaut" / "corpus" / "flat_canon"

_SEED = 20260711
_FIELDS = ["pop", "neg_phi", "k", "aps", "n_phi", "n_k", "prod_n", "linked",
           "bits", "settles", "refutes", "ms", "note"]


class _Budget(Exception):
    """The per-case watchdog fired."""


# --- gate 1: metamorphic endpoints ------------------------------------------


def _lassos(inv: Invariant, rng: random.Random) -> List[Lasso]:
    """Every lasso with `|u|, |v| <= 3` when that is small (the fixture
    alphabet), else >= 500 sampled ones — spec §3.6.1."""
    letters = inv.alphabet.letters()
    stems = [tuple(w) for n in range(4) for w in itertools.product(letters, repeat=n)]
    loops = [tuple(w) for n in range(1, 4) for w in itertools.product(letters, repeat=n)]
    if len(stems) * len(loops) <= 600:
        return [Lasso(u, v) for u in stems for v in loops]
    return [Lasso(rng.choice(stems), rng.choice(loops)) for _ in range(500)]


def _gate_metamorphic(iv: Interval, t_phi: Table, inv_phi: Invariant,
                      t_k: Table, inv_k: Invariant, rng: random.Random) -> int:
    """`member` on the interval endpoints vs the ORIGINAL two invariants —
    the check that would catch a carry bug across align/materialize."""
    count = 0
    for las in _lassos(inv_phi, rng):
        m_phi = member(t_phi, inv_phi.accept, las)
        m_k = member(t_k, inv_k.accept, las)
        assert member(iv.table, iv.p_min, las) == (m_phi and m_k), \
            f"p_min metamorphic law fails on {las}"
        assert member(iv.table, iv.p_max, las) == (m_phi or not m_k), \
            f"p_max metamorphic law fails on {las}"
        count += 1
    return count


# --- gate 2: endpoint cross-oracle -------------------------------------------


def _assert_replays(w: Witness, in_phi: bool, in_k: bool,
                    det_phi: Optional[HoaTeacher], det_k: Optional[HoaTeacher]) -> None:
    """Replay a witness lasso against the two det HOAs with the memberships
    its route promises (bounded — a det HOA replay is one product walk)."""
    if det_phi is not None:
        got = det_phi.member(w.lasso)
        assert got == in_phi, f"det(neg_phi) replay {got} != {in_phi}: {w.render()}"
    if det_k is not None:
        got = det_k.member(w.lasso)
        assert got == in_k, f"det(K) replay {got} != {in_k}: {w.render()}"


def _gate_cross_oracle(
    iv: Interval, t_phi: Table, inv_phi: Invariant, t_k: Table, inv_k: Invariant,
    det_phi: Optional[HoaTeacher], det_k: Optional[HoaTeacher],
) -> Tuple[bool, Optional[Witness], bool, Optional[Witness]]:
    """The endpoint decisions against the independent aligned-scan routes,
    every witness (both routes) replayed against both HOAs."""
    lang_phi = t_phi.language(inv_phi.accept)
    lang_k = t_k.language(inv_k.accept)

    settles, w_settle = k_settles_phi(iv)
    inter, w_inter = intersecting_word(align(lang_phi, lang_k))
    assert settles == (not inter), "k_settles_phi disagrees with intersecting_word"
    for w in (w_settle, w_inter):
        if w is not None:  # a word K leaves open: in L(neg_phi) and in L(K)
            _assert_replays(w, True, True, det_phi, det_k)

    refutes, w_refute = k_refutes_phi(iv)
    incl, w_incl = included(align(lang_k, lang_phi))
    assert refutes == incl, "k_refutes_phi disagrees with included(K <= neg_phi)"
    for w in (w_refute, w_incl):
        if w is not None:  # a run K allows that satisfies phi: in L(K) \ L(neg_phi)
            _assert_replays(w, False, True, det_phi, det_k)

    return settles, w_settle, refutes, w_refute


# --- gate 3: the conjugacy partition -----------------------------------------


def _gate_conjugacy(iv: Interval) -> None:
    """Spec §3.2's gate: the classes partition `linked`; `saturate` of one
    member recovers each class; every saturated pair set carried on the table
    is exactly the union of the classes it meets."""
    table = iv.table
    classes = conjugacy_classes(table)
    assert sum(len(c) for c in classes) == len(table.linked), "classes overlap"
    everything = frozenset().union(*classes) if classes else frozenset()
    assert everything == table.linked, "classes do not cover linked"
    for cls in classes:
        rep = min(cls)
        assert saturate(table, frozenset((rep,))) == cls, \
            f"saturate({rep}) != its class"
    for name, pairs in (("p_neg_phi", iv.p_neg_phi), ("p_k", iv.p_k),
                        ("p_min", iv.p_min), ("p_max", iv.p_max)):
        met = [c for c in classes if not c.isdisjoint(pairs)]
        tiled = frozenset().union(*met) if met else frozenset()
        assert tiled == pairs, f"{name} is not a union of conjugacy classes"


# --- gate 4: the choice laws --------------------------------------------------


def _gate_choice(iv: Interval, rng: random.Random) -> None:
    """Spec §3.4's laws, with 20 seeded random subsets."""
    assert choose(iv, ()) == iv.p_min, "choose(empty) != p_min"
    assert choose(iv, range(iv.bits)) == iv.p_max, "choose(all) != p_max"
    assert decompose(iv, iv.p_min) == frozenset(), "decompose(p_min) != empty"
    assert decompose(iv, iv.p_max) == frozenset(range(iv.bits)), \
        "decompose(p_max) != all"
    for _ in range(20):
        s = frozenset(i for i in range(iv.bits) if rng.random() < 0.5)
        q = choose(iv, s)
        assert decompose(iv, q) == s, f"decompose(choose({sorted(s)})) != it"
        wider = s | frozenset(i for i in range(iv.bits) if rng.random() < 0.5)
        assert q <= choose(iv, wider), "choose is not monotone"


# --- one pair, all gates ------------------------------------------------------


def check_pair(inv_phi: Invariant, inv_k: Invariant,
               det_phi_path: Optional[Path], det_k_path: Optional[Path],
               seed: int) -> Dict:
    """All four GT1 gates on one `(neg_phi, K)` pair; returns the census row."""
    rng = random.Random(seed)
    t0 = time.perf_counter()
    t_phi, t_k = Table.of(inv_phi), Table.of(inv_k)
    iv = given_that(inv_phi, inv_k)  # gate 3a: Prop 3.1 asserted inside

    _gate_conjugacy(iv)
    n_lassos = _gate_metamorphic(iv, t_phi, inv_phi, t_k, inv_k, rng)
    det_phi = HoaTeacher.of_hoa(str(det_phi_path)) if det_phi_path else None
    det_k = HoaTeacher.of_hoa(str(det_k_path)) if det_k_path else None
    settles, w_settle, refutes, w_refute = _gate_cross_oracle(
        iv, t_phi, inv_phi, t_k, inv_k, det_phi, det_k)
    _gate_choice(iv, rng)

    return {
        "aps": len(inv_phi.alphabet.aps), "n_phi": inv_phi.n, "n_k": inv_k.n,
        "prod_n": iv.table.n, "linked": len(iv.table.linked), "bits": iv.bits,
        "settles": int(settles), "refutes": int(refutes),
        "ms": round(1000 * (time.perf_counter() - t0), 1), "note": "",
        "_iv": iv, "_w_settle": w_settle, "_w_refute": w_refute,
        "_n_lassos": n_lassos,
    }


# --- the fixture pair (spec §3.5) ---------------------------------------------


def run_fixture(argv: List[str]) -> int:
    pair = fixtures.build(force="--force" in argv)
    inv_ab = load_invariant(pair.sos_ab.read_text())
    inv_k = load_invariant(pair.sos_k.read_text())
    assert inv_ab.n == 6, f"|C(D_ab)| = {inv_ab.n} != 6 — spec §8/E1, report"

    row = check_pair(inv_ab, inv_k, pair.det_ab, pair.det_k, _SEED)
    iv: Interval = row["_iv"]
    w1: Optional[Witness] = row["_w_settle"]
    w2: Optional[Witness] = row["_w_refute"]

    assert not row["settles"], "fixture: K must not settle phi"
    assert w1 is not None and len(w1.loop) == 2, \
        f"settle witness loop length != 2: {w1.render() if w1 else None}"
    assert not row["refutes"], "fixture: K must not refute phi"
    assert w2 is not None
    assert iv.bits >= 1, "fixture: the free band must be nonempty"

    print(f"|C(D_ab)| = {inv_ab.n} (asserted 6, paper §5.2)")
    print(f"|C(D_K)|  = {inv_k.n} (datum)")
    print(f"product: n = {row['prod_n']}, linked = {row['linked']}")
    print(f"iv.bits  = {iv.bits} (datum; paper predicts >= 1)")
    print(f"k_settles_phi = False, witness: {w1.render()}  [in D_ab, in D_K]")
    print(f"k_refutes_phi = False, witness: {w2.render()}  [not in D_ab, in D_K]")
    print(f"metamorphic lassos: {row['_n_lassos']} (exhaustive |u|,|v| <= 3)")
    print("SUCCESS")
    return 0


# --- one corpus pair ------------------------------------------------------------


def _corpus_row(corpus: _Corpus, det_dir: Path, pop: str, a: str, b: str,
                budget: int) -> Dict:
    """One campaign row: all gates on corpus pair `(neg_phi=a, K=b)` under the
    per-case watchdog; a blown budget is an F2 row, not a failure."""
    row: Dict = {"pop": pop, "neg_phi": a, "k": b}
    seed = zlib.crc32(f"{_SEED}|{a}|{b}".encode())
    signal.setitimer(signal.ITIMER_REAL, budget)
    try:
        got = check_pair(corpus.inv(a), corpus.inv(b),
                         det_dir / f"{a}.hoa", det_dir / f"{b}.hoa", seed)
        row.update({k: v for k, v in got.items() if not k.startswith("_")})
        if pop == "comp":
            assert got["settles"] == 1, \
                f"complement pair (p_min = empty) did not settle: {a} x {b}"
    except _Budget:
        row.update(aps="", n_phi="", n_k="", prod_n="", linked="", bits="",
                   settles="", refutes="", ms="", note="F2-budget")
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    return row


def run_one(argv: List[str]) -> int:
    corpus_dir = _CORPUS
    if "--corpus" in argv:
        corpus_dir = Path(argv[argv.index("--corpus") + 1])
        argv = [x for x in argv if x != "--corpus" and x != str(corpus_dir)]
    a, b = argv[0], argv[1]
    corpus = _Corpus(corpus_dir / "sos")
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(_Budget()))
    row = _corpus_row(corpus, corpus_dir / "det", "one", a, b, 15)
    print(row)
    print("SUCCESS" if row["note"] == "" else f"note: {row['note']}")
    return 0


# --- the 700-pair campaign (spec §3.6.5) ----------------------------------------


def _sample_pairs(corpus: _Corpus, rng: random.Random,
                  n_fwd: int, n_comp: int) -> List[Tuple[str, str, str]]:
    """The campaign populations: `n_fwd` same-stratum pairs sampled
    proportionally to stratum size, the same pairs reversed, and `n_comp`
    complement-partner pairs (content-hash partner map, never filenames)."""
    strata: Dict[Tuple[str, ...], List[str]] = {}
    for name in corpus.names:
        strata.setdefault(corpus.stratum(name), []).append(name)
    eligible = {k: v for k, v in sorted(strata.items()) if len(v) >= 2}
    total = sum(len(v) for v in eligible.values())

    fwd: List[Tuple[str, str]] = []
    seen: set = set()
    keys = list(eligible)
    quota = {k: max(1, round(n_fwd * len(eligible[k]) / total)) for k in keys}
    while sum(quota.values()) > n_fwd:
        quota[max(keys, key=lambda k: quota[k])] -= 1
    while sum(quota.values()) < n_fwd:
        quota[max(keys, key=lambda k: len(eligible[k]) / quota[k])] += 1
    for k in keys:
        names = eligible[k]
        while quota[k] > 0:
            a, b = rng.sample(names, 2)
            if (a, b) in seen:
                continue
            seen.add((a, b))
            fwd.append((a, b))
            quota[k] -= 1

    out = [("fwd", a, b) for a, b in fwd] + [("rev", b, a) for a, b in fwd]
    partnered = [n for n in corpus.names if corpus.partner_of(n)]
    for name in rng.sample(partnered, min(n_comp, len(partnered))):
        partner = corpus.partner_of(name)
        assert partner is not None
        out.append(("comp", name, partner))
    return out


def run_campaign(argv: List[str]) -> int:
    corpus_dir, limit, budget = _CORPUS, None, 15
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
    plan = _sample_pairs(corpus, rng, 300, 100)
    if limit is not None:
        plan = plan[:limit]

    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(_Budget()))
    _LOGS.mkdir(exist_ok=True)
    ckpt = _LOGS / "gt1_campaign.ckpt"
    done: Dict[Tuple[str, str, str], Dict] = {}
    if ckpt.exists():
        with open(ckpt, newline="") as fh:
            for r in csv.DictReader(fh):
                done[(r["pop"], r["neg_phi"], r["k"])] = r

    todo = [(pop, a, b) for pop, a, b in plan if (pop, a, b) not in done]
    print(f"=== GT1 campaign: {len(plan)} pairs, {len(done)} checkpointed, "
          f"{len(todo)} to run (seed {_SEED}) ===")

    fresh = not ckpt.exists()
    with open(ckpt, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=_FIELDS)
        if fresh:
            w.writeheader()
        for i, (pop, a, b) in enumerate(todo, 1):
            row = _corpus_row(corpus, corpus_dir / "det", pop, a, b, budget)
            w.writerow(row)
            fh.flush()
            done[(pop, a, b)] = row
            if i % 50 == 0:
                print(f"  {i}/{len(todo)}")

    rows = [done[key] for key in plan]
    with open(_LOGS / "gt1_bits.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in _FIELDS})

    scored = [r for r in rows if r["note"] == ""]
    f2 = len(rows) - len(scored)
    bits = sorted(int(r["bits"]) for r in scored)
    if bits:
        zero = sum(1 for x in bits if x == 0)
        print(f"|F| bits over {len(bits)} scored pairs (F2 skips: {f2}): "
              f"min {bits[0]} / median {bits[len(bits) // 2]} / "
              f"p95 {bits[int(0.95 * (len(bits) - 1))]} / max {bits[-1]}; "
              f"bits=0 share {zero}/{len(bits)}")
    for pop in ("fwd", "rev", "comp"):
        sub = [r for r in scored if r["pop"] == pop]
        if sub:
            s = sum(int(r["settles"]) for r in sub)
            u = sum(int(r["refutes"]) for r in sub)
            print(f"  {pop}: {len(sub)} scored, settles {s}, refutes {u}")
    print(f"wrote {_LOGS / 'gt1_bits.csv'}")
    print("SUCCESS" if all(r["note"] in ("", "F2-budget") for r in rows) else "FAILURE")
    return 0


def main(argv: List[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    if argv[0] == "--fixture":
        return run_fixture(argv[1:])
    if argv[0] == "--one":
        return run_one(argv[1:])
    if argv[0] == "--campaign":
        return run_campaign(argv[1:])
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
