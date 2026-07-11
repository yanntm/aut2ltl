"""M3 laws: distance / shadow / essential on the corpus.

    python3 -m tests.quant.m3_gate PATH.sos           case laws on one invariant
    python3 -m tests.quant.m3_gate A.sos B.sos        pair laws on one pair
    python3 -m tests.quant.m3_gate A.sos B.sos C.sos  triangle on one triple
    python3 -m tests.quant.m3_gate --pairs N SEED     emit N same-alphabet corpus pairs
    python3 -m tests.quant.m3_gate --triples N SEED   emit N same-alphabet corpus triples
    python3 -m tests.quant.m3_gate --list             corpus .sos paths, one per line
    python3 -m tests.quant.m3_gate --aggregate        logs -> reference/quant/m3_laws.{md,csv...}

Case mode: ``d(L, shadow(L)) = 0`` and ``d(L, essential(L)) = 0`` with
all-zero xor profiles; both operations idempotent (byte-equality of
dumps); essential byte-identical under uniform and the skewed ``p``
(Prop 4.5 — a difference is stop-the-line); ``essential(shadow(L))``
byte-equal ``essential(L)`` (the shadow⟹essential consistency law on the
pair ``(L, shadow(L))``, whose shadows agree by idempotence); if the
input algebra is aperiodic then ``ltl_up_to_null`` must say True. Row
``name,n,n_sh,n_es,laws_ok,pfree_ok,apr,ltl,ms`` to
``tests/quant/logs/m3_cases.csv``.

Pair mode: exact symmetry ``d(A, B) == d(B, A)`` (uniform and skewed);
shadow⟹essential consistency across the pair when the shadows happen to
agree. Row ``a,b,sym_ok,cons,d_num,d_den,null,ms`` (cons in {1, 0, na})
to ``tests/quant/logs/m3_pairs.csv``.

Triple mode: ``d(A, C) <= d(A, B) + d(B, C)`` exactly, uniform ``p``.
Row ``a,b,c,tri_ok,ms`` to ``tests/quant/logs/m3_triples.csv``.

Exit: 0 green, 1 red. Budget kills (15s per case, big aligned products)
leave no row and are counted by the aggregate as data, not violations.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path
from time import perf_counter
from typing import Dict, List

from sosl.sos import dump_invariant, load_invariant
from sosl.sos.classify.aperiodic import is_aperiodic
from sosl.quant import distance, essential, ltl_up_to_null, shadow
from tests.quant.law_gate import append_row, corpus_files, git_rev
from tests.quant.oracle_gate import skewed

REPO = Path(__file__).resolve().parents[3]
CORPUS = REPO / "genaut" / "corpus" / "flat_canon"
LOGS = Path(__file__).resolve().parent / "logs"
REF_DIR = REPO / "reference" / "quant"
CASE_HEADER = "name,n,n_sh,n_es,laws_ok,pfree_ok,apr,ltl,ms"
PAIR_HEADER = "a,b,sym_ok,cons,d_num,d_den,null,ms"
TRIPLE_HEADER = "a,b,c,tri_ok,ms"


def run_case(path: Path) -> int:
    """The per-language M3 laws; append the CSV row; 0 green, 1 red."""
    name = path.name
    t0 = perf_counter()
    inv = load_invariant(path.read_text())
    sh = shadow(inv)
    es = essential(inv)
    laws_ok = 1
    for other in (sh, es):
        d = distance(inv, other)
        if d.value != 0 or not d.null_disagreement:
            laws_ok = 0
    if dump_invariant(shadow(sh)) != dump_invariant(sh):
        laws_ok = 0
    if dump_invariant(essential(es)) != dump_invariant(es):
        laws_ok = 0
    if dump_invariant(essential(sh)) != dump_invariant(es):
        laws_ok = 0
    pfree_ok = int(
        dump_invariant(essential(inv, skewed(inv.alphabet))) == dump_invariant(es)
    )
    apr = int(is_aperiodic(inv))
    ltl = int(ltl_up_to_null(inv))
    if apr and not ltl:
        laws_ok = 0  # LTL outright but not LTL up to null sets: impossible
    ms = int((perf_counter() - t0) * 1000 + 0.5)
    row = f"{name},{inv.n},{sh.n},{es.n},{laws_ok},{pfree_ok},{apr},{ltl},{ms}"
    append_row(LOGS / "m3_cases.csv", CASE_HEADER, row)
    print(row)
    return 0 if laws_ok and pfree_ok else 1


def run_pair(path_a: Path, path_b: Path) -> int:
    """Distance symmetry + shadow⟹essential consistency on one pair."""
    name_a, name_b = path_a.name, path_b.name
    t0 = perf_counter()
    inv_a = load_invariant(path_a.read_text())
    inv_b = load_invariant(path_b.read_text())
    d_ab = distance(inv_a, inv_b)
    d_ba = distance(inv_b, inv_a)
    sym_ok = int(d_ab.value == d_ba.value)
    p = skewed(inv_a.alphabet)
    if distance(inv_a, inv_b, p).value != distance(inv_b, inv_a, p).value:
        sym_ok = 0
    cons = "na"
    if dump_invariant(shadow(inv_a)) == dump_invariant(shadow(inv_b)):
        cons = str(int(
            dump_invariant(essential(inv_a)) == dump_invariant(essential(inv_b))
        ))
    ms = int((perf_counter() - t0) * 1000 + 0.5)
    row = (
        f"{name_a},{name_b},{sym_ok},{cons},"
        f"{d_ab.value.numerator},{d_ab.value.denominator},"
        f"{int(d_ab.null_disagreement)},{ms}"
    )
    append_row(LOGS / "m3_pairs.csv", PAIR_HEADER, row)
    print(row)
    return 0 if sym_ok and cons != "0" else 1


def run_triple(path_a: Path, path_b: Path, path_c: Path) -> int:
    """The triangle inequality on one triple, uniform ``p``, exact."""
    t0 = perf_counter()
    inv_a = load_invariant(path_a.read_text())
    inv_b = load_invariant(path_b.read_text())
    inv_c = load_invariant(path_c.read_text())
    d_ac = distance(inv_a, inv_c).value
    d_ab = distance(inv_a, inv_b).value
    d_bc = distance(inv_b, inv_c).value
    tri_ok = int(d_ac <= d_ab + d_bc)
    ms = int((perf_counter() - t0) * 1000 + 0.5)
    row = f"{path_a.name},{path_b.name},{path_c.name},{tri_ok},{ms}"
    append_row(LOGS / "m3_triples.csv", TRIPLE_HEADER, row)
    print(row)
    return 0 if tri_ok else 1


def emit_tuples(count: int, seed: int, arity: int) -> None:
    """``count`` uniform same-alphabet corpus tuples, seeded — ``arity``
    paths per line, group chosen proportional to its tuple count."""
    groups: Dict[str, List[Path]] = {}
    for f in corpus_files():
        ap_line = f.read_text().splitlines()[1]
        groups.setdefault(ap_line, []).append(f)
    eligible = [g for g in groups.values() if len(g) >= arity]

    def tuples_in(g: List[Path]) -> int:
        w = 1
        for i in range(arity):
            w = w * (len(g) - i) // (i + 1)
        return w

    weighted = [(g, tuples_in(g)) for g in eligible]
    total = sum(w for _, w in weighted)
    rng = random.Random(seed)
    for _ in range(count):
        pick = rng.randrange(total)
        for g, w in weighted:
            if pick < w:
                print(" ".join(str(p) for p in rng.sample(g, arity)))
                break
            pick -= w


def _read_rows(log: Path, header: str) -> List[List[str]]:
    if not log.exists():
        return []
    return [
        line.split(",")
        for line in log.read_text().splitlines()
        if line and line != header
    ]


def aggregate() -> int:
    """Render ``reference/quant/m3_laws.md`` (+ three CSVs) from the
    logs; 0 iff no red anywhere."""
    cases = {r[0]: r for r in _read_rows(LOGS / "m3_cases.csv", CASE_HEADER)}
    pairs = _read_rows(LOGS / "m3_pairs.csv", PAIR_HEADER)
    triples = _read_rows(LOGS / "m3_triples.csv", TRIPLE_HEADER)
    case_rows = list(cases.values())
    case_reds = [r for r in case_rows if not (r[4] == "1" and r[5] == "1")]
    pair_reds = [r for r in pairs if not (r[2] == "1" and r[3] != "0")]
    triple_reds = [r for r in triples if r[3] != "1"]
    files = corpus_files()
    missing = [f.name for f in files if f.name not in cases]
    pair_sample = LOGS / "m3_pair_sample.txt"
    triple_sample = LOGS / "m3_triple_sample.txt"
    att_pairs = (
        len(pair_sample.read_text().splitlines()) if pair_sample.exists() else len(pairs)
    )
    att_triples = (
        len(triple_sample.read_text().splitlines())
        if triple_sample.exists() else len(triples)
    )
    cons_pairs = sum(1 for r in pairs if r[3] != "na")
    null_pairs = sum(1 for r in pairs if r[6] == "1")
    ltl_count = sum(1 for r in case_rows if r[7] == "1")
    apr_count = sum(1 for r in case_rows if r[6] == "1")
    REF_DIR.mkdir(parents=True, exist_ok=True)
    (REF_DIR / "m3_laws_cases.csv").write_text(
        "\n".join([CASE_HEADER] + [",".join(cases[k]) for k in sorted(cases)]) + "\n"
    )
    (REF_DIR / "m3_laws_pairs.csv").write_text(
        "\n".join([PAIR_HEADER] + [",".join(r) for r in pairs]) + "\n"
    )
    (REF_DIR / "m3_laws_triples.csv").write_text(
        "\n".join([TRIPLE_HEADER] + [",".join(r) for r in triples]) + "\n"
    )
    md: List[str] = [
        "# M3 — distance, shadow, essential: the laws",
        "",
        "- date: 2026-07-11",
        f"- git: {git_rev()}",
        f"- corpus: {CORPUS} ({len(files)} .sos files)",
        "- seeds: pair/triple sample seeds on the driver command line; "
        "case mode is deterministic (uniform + the M2 skewed p)",
        "- regeneration (from `sosl/`): cases "
        "`python3 -m tests.quant.m3_gate --list | while read f; do "
        "timeout 15 python3 -m tests.quant.m3_gate \"$f\" >/dev/null; done`; "
        "pairs `python3 -m tests.quant.m3_gate --pairs 1000 1 | tee "
        "tests/quant/logs/m3_pair_sample.txt | while read a b; do timeout 15 "
        "python3 -m tests.quant.m3_gate $a $b >/dev/null; done`; triples "
        "`python3 -m tests.quant.m3_gate --triples 500 1 | tee "
        "tests/quant/logs/m3_triple_sample.txt | while read a b c; do timeout 15 "
        "python3 -m tests.quant.m3_gate $a $b $c >/dev/null; done`; then "
        "`python3 -m tests.quant.m3_gate --aggregate`",
        "",
        "| law | sample | green | red | budget-blown |",
        "|---|---|---|---|---|",
        f"| case laws: d(L,sh)=d(L,es)=0, idempotence, sh⟹es consistency, "
        f"Prop 4.5 p-freeness, apr⟹ltl ({apr_count} aperiodic, {ltl_count} "
        f"ltl-up-to-null) | {len(files)} | {len(case_rows) - len(case_reds)} "
        f"| {len(case_reds)} | {len(missing)} |",
        f"| pair laws: symmetry both p's, sh⟹es across the pair "
        f"({cons_pairs} with equal shadows; {null_pairs} null-disagreement) "
        f"| {att_pairs} | {len(pairs) - len(pair_reds)} | {len(pair_reds)} "
        f"| {att_pairs - len(pairs)} |",
        f"| triangle inequality | {att_triples} "
        f"| {len(triples) - len(triple_reds)} | {len(triple_reds)} "
        f"| {att_triples - len(triples)} |",
        "",
        "A budget-blown row (15s per-case `timeout`, big aligned products or "
        "large essential quotients) is a recorded datum, not a law violation "
        "— no row means the kill. `pfree` red would convict paper Prop 4.5 "
        "(stop-the-line); none is expected.",
        "",
    ]
    for title, reds, header in (
        ("Red case rows", case_reds, CASE_HEADER),
        ("Red pair rows", pair_reds, PAIR_HEADER),
        ("Red triple rows", triple_reds, TRIPLE_HEADER),
    ):
        if reds:
            md += [f"## {title}", "", "```", header]
            md += [",".join(r) for r in reds[:50]] + ["```", ""]
    (REF_DIR / "m3_laws.md").write_text("\n".join(md))
    print(
        f"aggregate: {len(case_rows)}/{len(files)} cases ({len(case_reds)} red), "
        f"{len(pairs)}/{att_pairs} pairs ({len(pair_reds)} red), "
        f"{len(triples)}/{att_triples} triples ({len(triple_reds)} red) "
        f"-> {REF_DIR / 'm3_laws.md'}"
    )
    return 0 if not case_reds and not pair_reds and not triple_reds and not missing else 1


def main(argv: List[str]) -> int:
    if argv and argv[0] == "--pairs":
        emit_tuples(int(argv[1]), int(argv[2]), 2)
        return 0
    if argv and argv[0] == "--triples":
        emit_tuples(int(argv[1]), int(argv[2]), 3)
        return 0
    if argv == ["--list"]:
        for f in corpus_files():
            print(f)
        return 0
    if argv == ["--aggregate"]:
        return aggregate()
    paths = [Path(a) for a in argv]
    if len(paths) == 3:
        return run_triple(*paths)
    if len(paths) == 2:
        return run_pair(*paths)
    assert len(paths) == 1, __doc__
    return run_case(paths[0])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
