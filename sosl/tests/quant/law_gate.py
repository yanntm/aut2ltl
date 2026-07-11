"""M2 laws L2-L5: measure laws on aligned pairs and single invariants.

    python3 -m tests.quant.law_gate A.sos B.sos   L2+L3 on one aligned pair
    python3 -m tests.quant.law_gate PATH.sos      L4+L5 on one invariant
    python3 -m tests.quant.law_gate --pairs N SEED  emit N same-alphabet corpus pairs
    python3 -m tests.quant.law_gate --list          corpus .sos paths, one per line
    python3 -m tests.quant.law_gate --aggregate     logs -> reference/quant/m2_laws.{md,csv...}

Pair mode (L2 modularity, L3 monotonicity): align the two invariants,
materialize the product, move both pair sets onto the one table, then
``mu(P1|P2) + mu(P1&P2) == mu(P1) + mu(P2)`` exactly; if `included`
says L1 <= L2 then ``mu(L1) <= mu(L2)`` (both directions; the decision
is also cross-checked against pair-set order on the shared table).
Row ``a,b,n_prod,mod_ok,inc_ab,inc_ba,mono_ok,cons_ok,ms`` to
``tests/quant/logs/law_pairs.csv``.

Single mode (L4 trichotomy p-freeness, L5 obligation cross-check):
3 seeded random full-support rational p's — the 0 / interior / 1 class
of ``mu_p`` must match the theta-profile read-off (all-0 / mixed /
all-1) for each; if the `.cat` sidecar puts the language in the
obligation band (``max(m+, m-) <= 0``), every linked stem in every
bottom SCC must carry that SCC's theta bit (calculus Thm 3.10 made
numerical). Row ``name,n,trich_ok,oblig,ms`` (oblig in {1, 0, na}) to
``tests/quant/logs/law_cases.csv``. Exit: 0 green, 1 red.
"""
from __future__ import annotations

import random
import sys
import traceback
from fractions import Fraction
from pathlib import Path
from time import perf_counter
from typing import Dict, List, Tuple

from sosl.sos import Alphabet, Letter, load_invariant
from sosl.sos.calculus import Table, align, included, materialize
from sosl.sos.calculus.surgery import _stem_verdicts
from sosl.sos.calculus.table import PairSet
from sosl.sos.classify.io.reader import parse_cat
from sosl.quant import bottom_sccs, measure, theta_profile

REPO = Path(__file__).resolve().parents[3]
CORPUS = REPO / "genaut" / "corpus" / "flat_canon"
LOGS = Path(__file__).resolve().parent / "logs"
REF_DIR = REPO / "reference" / "quant"
PAIR_HEADER = "a,b,n_prod,mod_ok,inc_ab,inc_ba,mono_ok,cons_ok,ms"
CASE_HEADER = "name,n,trich_ok,oblig,ms"
P_SEED = 20260711


def corpus_files() -> List[Path]:
    """The corpus `.sos` files, sorted by name."""
    return sorted((CORPUS / "sos").glob("*.sos"))


def git_rev() -> str:
    """The current git revision (9 hex chars), read from ``.git`` directly."""
    head = (REPO / ".git" / "HEAD").read_text().strip()
    if head.startswith("ref: "):
        head = (REPO / ".git" / head[len("ref: "):]).read_text().strip()
    return head[:9]


def append_row(log: Path, header: str, row: str) -> None:
    log.parent.mkdir(parents=True, exist_ok=True)
    new = not log.exists()
    with log.open("a") as f:
        if new:
            f.write(header + "\n")
        f.write(row + "\n")


def random_p(alphabet: Alphabet, rng: random.Random) -> Dict[Letter, Fraction]:
    """One random full-support rational Bernoulli: integer weights in
    ``1..99`` per letter, normalized exactly."""
    w = {a: rng.randint(1, 99) for a in alphabet.letters()}
    total = sum(w.values())
    return {a: Fraction(v, total) for a, v in w.items()}


def run_pair(path_a: Path, path_b: Path) -> int:
    """Laws L2 + L3 on one pair; append the CSV row; 0 green, 1 red."""
    name_a, name_b = path_a.name, path_b.name
    n_prod, mod_ok, mono_ok, cons_ok = 0, 0, 0, 0
    inc_ab = inc_ba = False
    t0 = perf_counter()
    inv_a = load_invariant(path_a.read_text())
    inv_b = load_invariant(path_b.read_text())
    assert inv_a.alphabet == inv_b.alphabet, "pair must share the alphabet"
    la = Table.of(inv_a).language(inv_a.accept)
    lb = Table.of(inv_b).language(inv_b.accept)
    aligned = align(la, lb)
    prod = materialize(aligned, la, lb)
    table = prod.table
    n_prod = table.n

    def mu(pairs: PairSet) -> Fraction:
        return measure(table.invariant(pairs)).value

    m_a, m_b = mu(prod.pairs_a), mu(prod.pairs_b)
    m_u = mu(prod.pairs_a | prod.pairs_b)
    m_i = mu(prod.pairs_a & prod.pairs_b)
    mod_ok = int(m_u + m_i == m_a + m_b)
    inc_ab = included(aligned)[0]
    inc_ba = prod.pairs_b <= prod.pairs_a
    cons_ok = int(inc_ab == (prod.pairs_a <= prod.pairs_b))
    mono_ok = int(
        (not inc_ab or m_a <= m_b) and (not inc_ba or m_b <= m_a)
    )
    ms = int((perf_counter() - t0) * 1000 + 0.5)
    ok = mod_ok and mono_ok and cons_ok
    row = (
        f"{name_a},{name_b},{n_prod},{mod_ok},{int(inc_ab)},{int(inc_ba)},"
        f"{mono_ok},{cons_ok},{ms}"
    )
    append_row(LOGS / "law_pairs.csv", PAIR_HEADER, row)
    print(row)
    return 0 if ok else 1


def run_case(path: Path) -> int:
    """Laws L4 + L5 on one invariant; append the CSV row; 0 green, 1 red."""
    name = path.name
    t0 = perf_counter()
    inv = load_invariant(path.read_text())
    profile = theta_profile(inv)
    bits = [bit for (_, bit) in profile.entries]
    expected = 0 if not any(bits) else (2 if all(bits) else 1)
    rng = random.Random(f"{P_SEED}:{name}")
    trich_ok = 1
    for _ in range(3):
        v = measure(inv, random_p(inv.alphabet, rng)).value
        got = 0 if v == 0 else (2 if v == 1 else 1)
        if got != expected:
            trich_ok = 0
    oblig = "na"
    coords = parse_cat((path.parent / (path.stem + ".cat")).read_text())["coords"]
    if max(coords[0], coords[1]) <= 0:
        table = Table.of(inv)
        theta = _stem_verdicts(table, inv.accept)
        oblig = "1"
        if theta is None:
            oblig = "0"
        else:
            for scc, (_, bit) in zip(bottom_sccs(inv), profile.entries):
                stems = [s for s in scc if s in theta]
                assert stems, "a bottom SCC with no linked stem"
                if any(theta[s] != bit for s in stems):
                    oblig = "0"
    ms = int((perf_counter() - t0) * 1000 + 0.5)
    ok = trich_ok == 1 and oblig != "0"
    row = f"{name},{inv.n},{trich_ok},{oblig},{ms}"
    append_row(LOGS / "law_cases.csv", CASE_HEADER, row)
    print(row)
    return 0 if ok else 1


def emit_pairs(count: int, seed: int) -> None:
    """``count`` uniform unordered same-alphabet corpus pairs, seeded —
    two paths per line, group chosen proportional to its pair count."""
    groups: Dict[str, List[Path]] = {}
    for f in corpus_files():
        ap_line = f.read_text().splitlines()[1]
        groups.setdefault(ap_line, []).append(f)
    weighted = [(g, len(g) * (len(g) - 1) // 2) for g in groups.values() if len(g) > 1]
    total = sum(w for _, w in weighted)
    rng = random.Random(seed)
    for _ in range(count):
        pick = rng.randrange(total)
        for g, w in weighted:
            if pick < w:
                a, b = rng.sample(g, 2)
                print(f"{a} {b}")
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
    """Render ``reference/quant/m2_laws.md`` (+ the two CSVs) from the
    logs; 0 iff no red anywhere."""
    pairs = _read_rows(LOGS / "law_pairs.csv", PAIR_HEADER)
    cases = {r[0]: r for r in _read_rows(LOGS / "law_cases.csv", CASE_HEADER)}
    pair_reds = [r for r in pairs if not (r[3] == "1" and r[6] == "1" and r[7] == "1")]
    inclusions = sum(1 for r in pairs if r[4] == "1" or r[5] == "1")
    case_rows = list(cases.values())
    case_reds = [r for r in case_rows if not (r[2] == "1" and r[3] != "0")]
    oblig_band = sum(1 for r in case_rows if r[3] != "na")
    files = corpus_files()
    missing = [f.name for f in files if f.name not in cases]
    REF_DIR.mkdir(parents=True, exist_ok=True)
    (REF_DIR / "m2_laws_pairs.csv").write_text(
        "\n".join([PAIR_HEADER] + [",".join(r) for r in pairs]) + "\n"
    )
    (REF_DIR / "m2_laws_cases.csv").write_text(
        "\n".join([CASE_HEADER] + [",".join(cases[k]) for k in sorted(cases)]) + "\n"
    )
    md: List[str] = [
        "# M2 — laws L2-L5: modularity, monotonicity, trichotomy, obligation",
        "",
        "- date: 2026-07-11",
        f"- git: {git_rev()}",
        f"- corpus: {CORPUS} ({len(files)} .sos files)",
        f"- seeds: pair sample seed on the driver command line; per-file p seed `{P_SEED}:<name>`",
        "- regeneration (from `sosl/`): pairs "
        "`python3 -m tests.quant.law_gate --pairs 1000 1 | while read a b; do "
        "timeout 15 python3 -m tests.quant.law_gate \"$a\" \"$b\" >/dev/null; done`; "
        "cases `python3 -m tests.quant.law_gate --list | while read f; do "
        "timeout 15 python3 -m tests.quant.law_gate \"$f\" >/dev/null; done`; then "
        "`python3 -m tests.quant.law_gate --aggregate`",
        "",
        "| law | sample | green | red |",
        "|---|---|---|---|",
        f"| L2 modularity + L3 monotonicity (pairs; {inclusions} with an inclusion) "
        f"| {len(pairs)} | {len(pairs) - len(pair_reds)} | {len(pair_reds)} |",
        f"| L4 trichotomy + L5 obligation (cases; {oblig_band} in the obligation band) "
        f"| {len(case_rows)} | {len(case_rows) - len(case_reds)} | {len(case_reds)} |",
        "",
        f"missing single-case rows: {len(missing)}",
        "",
    ]
    for title, reds, header in (
        ("Red pair rows", pair_reds, PAIR_HEADER),
        ("Red case rows", case_reds, CASE_HEADER),
    ):
        if reds:
            md += [f"## {title}", "", "```", header]
            md += [",".join(r) for r in reds[:50]] + ["```", ""]
    (REF_DIR / "m2_laws.md").write_text("\n".join(md))
    print(
        f"aggregate: {len(pairs)} pairs ({len(pair_reds)} red), "
        f"{len(case_rows)} cases ({len(case_reds)} red, {oblig_band} obligation), "
        f"{len(missing)} missing -> {REF_DIR / 'm2_laws.md'}"
    )
    return 0 if not pair_reds and not case_reds and not missing else 1


def main(argv: List[str]) -> int:
    if argv and argv[0] == "--pairs":
        emit_pairs(int(argv[1]), int(argv[2]))
        return 0
    if argv == ["--list"]:
        for f in corpus_files():
            print(f)
        return 0
    if argv == ["--aggregate"]:
        return aggregate()
    if len(argv) == 2:
        return run_pair(Path(argv[0]), Path(argv[1]))
    assert len(argv) == 1, __doc__
    return run_case(Path(argv[0]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
