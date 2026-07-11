"""M2 law L1: measure vs the Route A oracle, one corpus case per invocation.

    python3 -m tests.quant.oracle_gate PATH.sos   one case; appends a CSV row
    python3 -m tests.quant.oracle_gate --list     corpus .sos paths, one per line
    python3 -m tests.quant.oracle_gate --aggregate  logs -> reference/quant/m2_oracle.{md,csv}

For one corpus invariant and its paired ``det/<name>.hoa``:
``measure(I).value == route_a(hoa).value`` exactly, under uniform p AND
the fixed skewed p ``p(a) = (1 + a) / sum(1 + m)`` (a = letter mask).
Failure attribution is explicit: a Spot-side failure (parse, missing
mate) is a SKIP (a datum); a mismatch or a crash in our code is a RED.
Row: ``name,n,n_states,mu_num,mu_den,ok,skip,ms`` to
``tests/quant/logs/oracle_gate.csv``. Exit: 0 green or skip, 1 red.
"""
from __future__ import annotations

import sys
import traceback
from fractions import Fraction
from pathlib import Path
from time import perf_counter
from typing import Dict, List

from sosl.sos import Alphabet, Letter, load_invariant
from sosl.quant import measure

REPO = Path(__file__).resolve().parents[3]
CORPUS = REPO / "genaut" / "corpus" / "flat_canon"
LOG = Path(__file__).resolve().parent / "logs" / "oracle_gate.csv"
REF_DIR = REPO / "reference" / "quant"
HEADER = "name,n,n_states,mu_num,mu_den,ok,skip,ms"


def corpus_files() -> List[Path]:
    """The corpus `.sos` files, sorted by name."""
    return sorted((CORPUS / "sos").glob("*.sos"))


def git_rev() -> str:
    """The current git revision (9 hex chars), read from ``.git`` directly."""
    head = (REPO / ".git" / "HEAD").read_text().strip()
    if head.startswith("ref: "):
        head = (REPO / ".git" / head[len("ref: "):]).read_text().strip()
    return head[:9]


def skewed(alphabet: Alphabet) -> Dict[Letter, Fraction]:
    """The fixed skewed Bernoulli of law L1: ``p(a)`` proportional to
    ``1 + a`` over the letter masks (full support, exact, sums to 1)."""
    total = sum(1 + a for a in alphabet.letters())
    return {a: Fraction(1 + a, total) for a in alphabet.letters()}


def append_row(row: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    new = not LOG.exists()
    with LOG.open("a") as f:
        if new:
            f.write(HEADER + "\n")
        f.write(row + "\n")


def run_case(path: Path) -> int:
    """Compare measure and oracle on ``path`` under both p's; append the
    CSV row; return 0 on green or skip, 1 on red."""
    name = path.name
    n = n_states = 0
    mu_num, mu_den, ok, skip = -1, -1, 0, 0
    t0 = perf_counter()
    try:
        inv = load_invariant(path.read_text())
        n = inv.n
        p2 = skewed(inv.alphabet)
        r_uni = measure(inv)
        r_skw = measure(inv, p2)
        mu_num, mu_den = r_uni.value.numerator, r_uni.value.denominator
        hoa = CORPUS / "det" / (path.stem + ".hoa")
        try:
            from sosl.quant.routea import route_a

            a_uni = route_a(str(hoa), inv.alphabet)
            a_skw = route_a(str(hoa), inv.alphabet, p2)
            n_states = a_uni.n_states
        except Exception:
            traceback.print_exc()
            skip = 1
        if not skip:
            ok = int(r_uni.value == a_uni.value and r_skw.value == a_skw.value)
    except Exception:
        traceback.print_exc()
    ms = int((perf_counter() - t0) * 1000 + 0.5)
    row = f"{name},{n},{n_states},{mu_num},{mu_den},{ok},{skip},{ms}"
    append_row(row)
    print(row)
    return 0 if ok or skip else 1


def aggregate() -> int:
    """Render ``reference/quant/m2_oracle.{md,csv}`` from the log; return
    0 iff every corpus file has a green or skip row (skips reported)."""
    rows: Dict[str, List[str]] = {}
    for line in LOG.read_text().splitlines():
        if line and line != HEADER:
            parts = line.split(",")
            rows[parts[0]] = parts  # last row per name wins
    files = corpus_files()
    missing = [f.name for f in files if f.name not in rows]
    skips = [r for r in rows.values() if r[6] == "1"]
    reds = [r for r in rows.values() if r[5] != "1" and r[6] != "1"]
    greens = len(rows) - len(reds) - len(skips)
    ms = sorted(int(r[7]) for r in rows.values())
    REF_DIR.mkdir(parents=True, exist_ok=True)
    csv = "\n".join([HEADER] + [",".join(rows[k]) for k in sorted(rows)])
    (REF_DIR / "m2_oracle.csv").write_text(csv + "\n")
    md: List[str] = [
        "# M2 — law L1: measure vs the Route A oracle",
        "",
        "- date: 2026-07-11",
        f"- git: {git_rev()}",
        f"- corpus: {CORPUS} ({len(files)} .sos files, det/ mates by basename)",
        "- regeneration (from `sosl/`): "
        "`python3 -m tests.quant.oracle_gate --list | while read f; do "
        "timeout 15 python3 -m tests.quant.oracle_gate \"$f\" >/dev/null; done; "
        "python3 -m tests.quant.oracle_gate --aggregate`",
        "",
        "**Law.** `measure(I(X)).value == route_a(det/X.hoa).value` exactly, "
        "under uniform p and the skewed `p(a) = (1+a)/sum(1+m)`; the oracle "
        "is the classical BSCC analysis on the paired deterministic complete "
        "EL automaton, Spot for parsing only, `Fraction` throughout.",
        "",
        "| cases | green | red | skip | missing | median ms | max ms |",
        "|---|---|---|---|---|---|---|",
        f"| {len(rows)} | {greens} | {len(reds)} | {len(skips)} | {len(missing)} "
        f"| {ms[len(ms) // 2] if ms else 0} | {ms[-1] if ms else 0} |",
        "",
    ]
    if reds:
        md += ["## Red rows", "", "```", HEADER]
        md += [",".join(r) for r in reds[:50]]
        md += ["```", ""]
    if skips:
        md += ["## Skips (Spot-side, a datum not a failure)", "", "```", HEADER]
        md += [",".join(r) for r in skips[:50]]
        md += ["```", ""]
    if missing:
        md += [f"## Missing ({len(missing)})", ""]
        md += [f"- {m}" for m in missing[:50]] + [""]
    (REF_DIR / "m2_oracle.md").write_text("\n".join(md))
    print(
        f"aggregate: {len(rows)} cases, {greens} green, {len(reds)} red, "
        f"{len(skips)} skip, {len(missing)} missing -> {REF_DIR / 'm2_oracle.md'}"
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
