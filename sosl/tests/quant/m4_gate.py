"""M4 entropy laws on the corpus (spec section 10).

    python3 -m tests.quant.m4_gate PATH.sos         case laws on one invariant
    python3 -m tests.quant.m4_gate A.sos B.sos      monotonicity on one pair
    python3 -m tests.quant.m4_gate --pairs N SEED   emit N same-alphabet corpus pairs
    python3 -m tests.quant.m4_gate --list           corpus .sos paths, one per line
    python3 -m tests.quant.m4_gate --aggregate      logs -> reference/quant/m4_entropy.{md,csv...}

Case mode: ``L = 0 => h = 0`` with width 0; ``L != 0 => rho_lo >= 1``
(the live subgraph must carry a cycle — a violation convicts the
liveness scan); ``rho_hi <= |Sigma|`` exactly; the closure law
``h(cl(L)) = h(L)`` checked structurally (``cl`` via the calculus
safety_closure on the same table: equal live sets, identical live
letter-count matrices — never on floats). Row
``name,n,nlive,nblocks,conv,rng_ok,cl_ok,h_lo,h_hi,ms`` to
``tests/quant/logs/m4_cases.csv``; a non-converged bracket (conv=0) is
a datum, not a red.

Pair mode: M2's L3 inclusion detection on the aligned pair; if
``L1 <= L2`` then the enclosure-safe reading ``rho_lo(L1) <= rho_hi(L2)``
(both directions). Row ``a,b,inc_ab,inc_ba,mono_ok,ms`` to
``tests/quant/logs/m4_pairs.csv``.

Exit: 0 green, 1 red. Budget kills (15s `timeout` per case) leave no
row and are counted by the aggregate as data, not violations.
"""
from __future__ import annotations

import sys
from pathlib import Path
from time import perf_counter
from typing import List

from sosl.sos import load_invariant
from sosl.sos.calculus import Table, align, included, safety_closure
from sosl.quant import entropy, letter_counts, live_classes
from tests.quant.law_gate import append_row, corpus_files, emit_pairs, git_rev

REPO = Path(__file__).resolve().parents[3]
CORPUS = REPO / "genaut" / "corpus" / "flat_canon"
LOGS = Path(__file__).resolve().parent / "logs"
REF_DIR = REPO / "reference" / "quant"
CASE_HEADER = "name,n,nlive,nblocks,conv,rng_ok,cl_ok,h_lo,h_hi,ms"
PAIR_HEADER = "a,b,inc_ab,inc_ba,mono_ok,ms"


def run_case(path: Path) -> int:
    """The per-language entropy laws; append the CSV row; 0 green, 1 red."""
    name = path.name
    t0 = perf_counter()
    inv = load_invariant(path.read_text())
    r = entropy(inv)
    rng_ok = 1
    if not inv.accept:
        if r.rho_lo != 0 or r.rho_hi != 0 or r.h_lo != 0.0 or r.h_hi != 0.0:
            rng_ok = 0
    else:
        if r.rho_lo < 1:  # the live subgraph must carry a cycle
            rng_ok = 0
        if r.rho_hi > len(inv.letter_class):
            rng_ok = 0
    table = Table.of(inv)
    cl_inv = table.invariant(safety_closure(table, inv.accept))
    cl_alive = live_classes(cl_inv)
    cl_ok = int(
        cl_alive == r.live
        and letter_counts(cl_inv, cl_alive) == letter_counts(inv, r.live)
    )
    ms = int((perf_counter() - t0) * 1000 + 0.5)
    row = (
        f"{name},{inv.n},{len(r.live)},{len(r.blocks)},{int(r.converged)},"
        f"{rng_ok},{cl_ok},{r.h_lo!r},{r.h_hi!r},{ms}"
    )
    append_row(LOGS / "m4_cases.csv", CASE_HEADER, row)
    print(row)
    return 0 if rng_ok and cl_ok else 1


def run_pair(path_a: Path, path_b: Path) -> int:
    """Monotonicity under detected inclusion on one aligned pair."""
    t0 = perf_counter()
    inv_a = load_invariant(path_a.read_text())
    inv_b = load_invariant(path_b.read_text())
    assert inv_a.alphabet == inv_b.alphabet, "pair must share the alphabet"
    la = Table.of(inv_a).language(inv_a.accept)
    lb = Table.of(inv_b).language(inv_b.accept)
    inc_ab = included(align(la, lb))[0]
    inc_ba = included(align(lb, la))[0]
    ra, rb = entropy(inv_a), entropy(inv_b)
    mono_ok = int(
        (not inc_ab or ra.rho_lo <= rb.rho_hi)
        and (not inc_ba or rb.rho_lo <= ra.rho_hi)
    )
    ms = int((perf_counter() - t0) * 1000 + 0.5)
    row = (
        f"{path_a.name},{path_b.name},{int(inc_ab)},{int(inc_ba)},{mono_ok},{ms}"
    )
    append_row(LOGS / "m4_pairs.csv", PAIR_HEADER, row)
    print(row)
    return 0 if mono_ok else 1


def _read_rows(log: Path, header: str) -> List[List[str]]:
    if not log.exists():
        return []
    return [
        line.split(",")
        for line in log.read_text().splitlines()
        if line and line != header
    ]


def aggregate() -> int:
    """Render ``reference/quant/m4_entropy.md`` (+ the two CSVs) from
    the logs; 0 iff no red anywhere and no case is missing."""
    cases = {r[0]: r for r in _read_rows(LOGS / "m4_cases.csv", CASE_HEADER)}
    pairs = _read_rows(LOGS / "m4_pairs.csv", PAIR_HEADER)
    case_rows = list(cases.values())
    case_reds = [r for r in case_rows if not (r[5] == "1" and r[6] == "1")]
    unconverged = [r for r in case_rows if r[4] != "1"]
    pair_reds = [r for r in pairs if r[4] != "1"]
    inclusions = sum(1 for r in pairs if r[2] == "1" or r[3] == "1")
    files = corpus_files()
    missing = [f.name for f in files if f.name not in cases]
    sample = LOGS / "m4_pair_sample.txt"
    att_pairs = len(sample.read_text().splitlines()) if sample.exists() else len(pairs)
    REF_DIR.mkdir(parents=True, exist_ok=True)
    (REF_DIR / "m4_entropy_cases.csv").write_text(
        "\n".join([CASE_HEADER] + [",".join(cases[k]) for k in sorted(cases)]) + "\n"
    )
    (REF_DIR / "m4_entropy_pairs.csv").write_text(
        "\n".join([PAIR_HEADER] + [",".join(r) for r in pairs]) + "\n"
    )
    md: List[str] = [
        "# M4 — entropy: certified enclosures and the laws",
        "",
        "- date: 2026-07-11",
        f"- git: {git_rev()}",
        f"- corpus: {CORPUS} ({len(files)} .sos files)",
        "- seeds: pair sample seed on the driver command line; case mode "
        "is deterministic",
        "- regeneration (from `sosl/`): cases "
        "`python3 -m tests.quant.m4_gate --list | while read f; do "
        "timeout 15 python3 -m tests.quant.m4_gate \"$f\" >/dev/null; done`; "
        "pairs `python3 -m tests.quant.m4_gate --pairs 1000 1 | tee "
        "tests/quant/logs/m4_pair_sample.txt | while read a b; do timeout 15 "
        "python3 -m tests.quant.m4_gate $a $b >/dev/null; done`; then "
        "`python3 -m tests.quant.m4_gate --aggregate`",
        "",
        "| law | sample | green | red | budget-blown |",
        "|---|---|---|---|---|",
        f"| case laws: emptiness, 1 <= rho_lo, rho_hi <= |Sigma|, "
        f"structural h(cl(L)) = h(L) ({len(unconverged)} non-converged "
        f"brackets, data) | {len(files)} | {len(case_rows) - len(case_reds)} "
        f"| {len(case_reds)} | {len(missing)} |",
        f"| monotonicity under inclusion ({inclusions} pairs with an "
        f"inclusion) | {att_pairs} | {len(pairs) - len(pair_reds)} "
        f"| {len(pair_reds)} | {att_pairs - len(pairs)} |",
        "",
        "A budget-blown row (15s per-case `timeout`) and a non-converged "
        "bracket (still a valid enclosure by Collatz-Wielandt) are recorded "
        "data, not law violations. `h` is reported as the ulp-widened float "
        "bracket; every law above is decided on the exact rational side.",
        "",
    ]
    for title, reds, header in (
        ("Red case rows", case_reds, CASE_HEADER),
        ("Red pair rows", pair_reds, PAIR_HEADER),
    ):
        if reds:
            md += [f"## {title}", "", "```", header]
            md += [",".join(r) for r in reds[:50]] + ["```", ""]
    (REF_DIR / "m4_entropy.md").write_text("\n".join(md))
    print(
        f"aggregate: {len(case_rows)}/{len(files)} cases ({len(case_reds)} red, "
        f"{len(unconverged)} non-converged), {len(pairs)}/{att_pairs} pairs "
        f"({len(pair_reds)} red) -> {REF_DIR / 'm4_entropy.md'}"
    )
    return 0 if not case_reds and not pair_reds and not missing else 1


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
    paths = [Path(a) for a in argv]
    if len(paths) == 2:
        return run_pair(*paths)
    assert len(paths) == 1, __doc__
    return run_case(paths[0])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
