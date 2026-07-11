"""M1 gate: the flip law, one corpus case per invocation.

    python3 -m tests.quant.flip_gate PATH.sos     one case; appends a CSV row
    python3 -m tests.quant.flip_gate --list       corpus .sos paths, one per line
    python3 -m tests.quant.flip_gate --aggregate  logs -> reference/quant/m1_measure.{md,csv}

For one invariant: load, measure under uniform p, complement by the
calculus flip (no reduce), measure again; the case is green iff
``mu(L) + mu(~L) == 1`` exactly AND the two theta-profiles are pointwise
negations over the same SCC keys. The row
``name,n,n_bottom_sccs,mu_num,mu_den,ok,ms`` goes to
``tests/quant/logs/flip_gate.csv`` (a crash still writes its red row,
with mu -1/-1). ``--aggregate`` keeps the last row per name, checks
coverage against the corpus, and renders the machine report with the
date / git-rev / corpus header of the ``reference/calculus`` reports.
Exit status: 0 green, 1 red, 2 crash.
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path
from time import perf_counter
from typing import Dict, List

from sosl.sos import load_invariant
from sosl.quant import MeasureResult, measure

REPO = Path(__file__).resolve().parents[3]
CORPUS = REPO / "genaut" / "corpus" / "flat_canon" / "sos"
LOG = Path(__file__).resolve().parent / "logs" / "flip_gate.csv"
REF_DIR = REPO / "reference" / "quant"
HEADER = "name,n,n_bottom_sccs,mu_num,mu_den,ok,ms"


def corpus_files() -> List[Path]:
    """The corpus `.sos` files, sorted by name."""
    return sorted(CORPUS.glob("*.sos"))


def git_rev() -> str:
    """The current git revision (9 hex chars), read from ``.git`` directly."""
    head = (REPO / ".git" / "HEAD").read_text().strip()
    if head.startswith("ref: "):
        head = (REPO / ".git" / head[len("ref: "):]).read_text().strip()
    return head[:9]


def profiles_negated(a: MeasureResult, b: MeasureResult) -> bool:
    """Same SCC keys in the same order, every theta bit flipped."""
    ea, eb = a.profile.entries, b.profile.entries
    return len(ea) == len(eb) and all(
        ka == kb and va != vb for (ka, va), (kb, vb) in zip(ea, eb)
    )


def append_row(row: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    new = not LOG.exists()
    with LOG.open("a") as f:
        if new:
            f.write(HEADER + "\n")
        f.write(row + "\n")


def run_case(path: Path) -> int:
    """Measure ``path`` and its flip, append the CSV row, return the exit
    status (0 green, 1 red, 2 crash)."""
    name = path.name
    n = 0
    status = 2
    mu_num, mu_den, n_bottom, ok = -1, -1, -1, 0
    t0 = perf_counter()
    try:
        inv = load_invariant(path.read_text())
        n = inv.n
        r = measure(inv)
        rc = measure(inv.complement())
        mu_num, mu_den = r.value.numerator, r.value.denominator
        n_bottom = len(r.profile.entries)
        ok = int(r.value + rc.value == 1 and profiles_negated(r, rc))
        status = 0 if ok else 1
    except Exception:
        traceback.print_exc()
    ms = int((perf_counter() - t0) * 1000 + 0.5)
    row = f"{name},{n},{n_bottom},{mu_num},{mu_den},{ok},{ms}"
    append_row(row)
    print(row)
    return status


def aggregate() -> int:
    """Render ``reference/quant/m1_measure.{md,csv}`` from the log; return
    0 iff every corpus file has a green row."""
    rows: Dict[str, List[str]] = {}
    for line in LOG.read_text().splitlines():
        if line and line != HEADER:
            parts = line.split(",")
            rows[parts[0]] = parts  # last row per name wins
    files = corpus_files()
    missing = [f.name for f in files if f.name not in rows]
    reds = [r for r in rows.values() if r[5] != "1"]
    greens = len(rows) - len(reds)
    mu_zero = sum(1 for r in rows.values() if r[3] == "0")
    mu_one = sum(1 for r in rows.values() if r[3] == r[4])
    interior = len(rows) - mu_zero - mu_one
    ns = sorted(int(r[1]) for r in rows.values())
    sccs = sorted(int(r[2]) for r in rows.values())
    REF_DIR.mkdir(parents=True, exist_ok=True)
    csv = "\n".join([HEADER] + [",".join(rows[k]) for k in sorted(rows)])
    (REF_DIR / "m1_measure.csv").write_text(csv + "\n")
    md: List[str] = [
        "# M1 — theta-profile + exact measure: the flip gate",
        "",
        f"- date: 2026-07-11",
        f"- git: {git_rev()}",
        f"- corpus: {CORPUS.parent} ({len(files)} .sos files)",
        "- regeneration (from `sosl/`): "
        "`python3 -m tests.quant.flip_gate --list | while read f; do "
        "timeout 15 python3 -m tests.quant.flip_gate \"$f\" >/dev/null; done; "
        "python3 -m tests.quant.flip_gate --aggregate`",
        "",
        f"**Law.** `mu(L) + mu(~L) == 1` exactly (uniform p) and pointwise-"
        "negated theta-profiles, complement by the calculus flip, no reduce, "
        "all numbers `Fraction`.",
        "",
        "| cases | green | red | missing |",
        "|---|---|---|---|",
        f"| {len(rows)} | {greens} | {len(reds)} | {len(missing)} |",
        "",
        "| mu = 0 | 0 < mu < 1 | mu = 1 | median n | max n | median bottom SCCs | max |",
        "|---|---|---|---|---|---|---|",
        f"| {mu_zero} | {interior} | {mu_one} | {ns[len(ns) // 2] if ns else 0} "
        f"| {ns[-1] if ns else 0} | {sccs[len(sccs) // 2] if sccs else 0} "
        f"| {sccs[-1] if sccs else 0} |",
        "",
    ]
    if reds:
        md += ["## Red rows", "", "```", HEADER]
        md += [",".join(r) for r in reds[:50]]
        md += ["```", ""]
    if missing:
        md += [f"## Missing ({len(missing)})", ""]
        md += [f"- {m}" for m in missing[:50]]
        md += [""]
    (REF_DIR / "m1_measure.md").write_text("\n".join(md))
    print(
        f"aggregate: {len(rows)} cases, {greens} green, {len(reds)} red, "
        f"{len(missing)} missing -> {REF_DIR / 'm1_measure.md'}"
    )
    return 0 if not reds and not missing else 1


def main(argv: List[str]) -> int:
    assert len(argv) == 1, __doc__
    if argv[0] == "--list":
        for f in corpus_files():
            print(f)
        return 0
    if argv[0] == "--aggregate":
        return aggregate()
    return run_case(Path(argv[0]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
