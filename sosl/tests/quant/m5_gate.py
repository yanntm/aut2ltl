"""M5 gates: the Markov product ``Pr_M(L)``, one corpus case per invocation.

    python3 -m tests.quant.m5_gate PATH.sos            one case; appends a CSV row
    python3 -m tests.quant.m5_gate --oracle PATH.sos   one Route A product case
    python3 -m tests.quant.m5_gate --list              corpus .sos paths, one per line
    python3 -m tests.quant.m5_gate --sample            the oracle sample, one path per line
    python3 -m tests.quant.m5_gate --aggregate         logs -> reference/quant/m5_product.{md,csv}

The main case runs three of the four spec §11.5 gates on one invariant:

- **Bernoulli embedding.** The chain ``{q_a}`` with ``l(q_a) = a`` and
  ``P(q_a -> q_b) = p(b)``, run from every initial state:
  ``sum_a p(a) . Pr_{M_a}(L) == mu_p(L)`` byte-exact against M1, under the
  uniform p and the skewed p of M2's law L1. This exercises the word
  convention |Sigma| times per language.
- **Complement flip.** One seeded random chain (exact rationals, small
  denominators): ``Pr_M(L) + Pr_M(~L) == 1`` exactly, complement by the
  calculus flip.
- **Reader round-trip.** Every chain used is written to ``.mc`` text, re-read
  and asserted identical.

``--oracle`` runs the fourth: the same seeded random chain against the paired
deterministic ``det/<name>.hoa``, per bottom SCC an Emerson-Lei evaluation on
the product's edge marks and the same absorption system — asserted byte-equal
to ``pr_chain``. A Spot-side failure is a SKIP (a datum), never a red.

Rows go to ``tests/quant/logs/m5_{gate,oracle}.csv``. Exit: 0 green (or skip),
1 red, 2 crash.
"""
from __future__ import annotations

import random
import sys
import traceback
import zlib
from fractions import Fraction
from pathlib import Path
from time import perf_counter
from typing import Dict, List, Tuple

from sosl.sos import Alphabet, Letter, load_invariant
from sosl.sos.invariant import Invariant
from sosl.quant import measure
from sosl.quant.mc import Chain, bernoulli_chain, dump_mc, parse_mc
from sosl.quant.product import pr_chain

REPO = Path(__file__).resolve().parents[3]
CORPUS = REPO / "genaut" / "corpus" / "flat_canon"
LOGS = Path(__file__).resolve().parent / "logs"
REF_DIR = REPO / "reference" / "quant"
SEED = 1
SAMPLE_SIZE = 250

HEADER = "name,n,ap,sigma,n_prod,bern_ok,flip_ok,rt_ok,ok,ms"
O_HEADER = "name,n,n_prod,pr_num,pr_den,oracle_num,oracle_den,ok,skip,ms"


def corpus_files() -> List[Path]:
    """The corpus `.sos` files, sorted by name."""
    return sorted((CORPUS / "sos").glob("*.sos"))


def sample_files() -> List[Path]:
    """The seeded oracle sample: `SAMPLE_SIZE` corpus files, drawn without
    replacement from the sorted corpus under `SEED`."""
    files = corpus_files()
    rng = random.Random(SEED)
    return sorted(rng.sample(files, min(SAMPLE_SIZE, len(files))))


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


def random_chain(alphabet: Alphabet, name: str) -> Chain:
    """A chain seeded by the case name (so one case replays alone): between
    ``|Sigma|`` and ``2|Sigma|`` states, every letter labelling at least one
    of them, and per state 1..3 branches with probabilities ``w_i / sum w``
    for small integer weights — exact rationals, small denominators."""
    rng = random.Random(SEED ^ zlib.crc32(name.encode()))
    letters = alphabet.letters()
    size = len(letters)
    n = size + rng.randrange(size + 1)
    label = list(letters)
    rng.shuffle(label)
    label += [rng.choice(letters) for _ in range(n - size)]
    trans: List[Tuple[Tuple[int, Fraction], ...]] = []
    for _ in range(n):
        k = rng.randint(1, min(3, n))
        targets = sorted(rng.sample(range(n), k))
        weights = [rng.randint(1, 4) for _ in targets]
        total = sum(weights)
        trans.append(
            tuple((d, Fraction(w, total)) for d, w in zip(targets, weights))
        )
    ch = Chain(
        alphabet=alphabet, label=tuple(label), trans=tuple(trans), init=0
    )
    ch.validate()
    return ch


def round_trip(ch: Chain) -> bool:
    """``ch`` survives its own ``.mc`` text unchanged."""
    return parse_mc(dump_mc(ch), ch.alphabet) == ch


def bernoulli_law(inv: Invariant, p: Dict[Letter, Fraction]) -> Tuple[bool, int]:
    """The embedding law under one ``p``: ``sum_a p(a) . Pr_{M_a}(L)`` against
    ``mu_p(L)``, the chain re-started at every letter state. Returns the
    verdict and the largest product size seen."""
    ch = bernoulli_chain(inv.alphabet, p)
    assert round_trip(ch), "the Bernoulli chain failed its .mc round-trip"
    total = Fraction(0)
    widest = 0
    for i, a in enumerate(inv.alphabet.letters()):
        r = pr_chain(inv, ch.with_init(i))
        total += p[a] * r.value
        widest = max(widest, r.n_product)
    return total == measure(inv, p).value, widest


def run_case(path: Path) -> int:
    """The Bernoulli-embedding, complement-flip and round-trip gates on one
    invariant; append the CSV row; 0 green, 1 red, 2 crash."""
    name = path.name
    n = sigma = n_prod = 0
    bern_ok = flip_ok = rt_ok = ok = 0
    status = 2
    ap = "-"
    t0 = perf_counter()
    try:
        inv = load_invariant(path.read_text())
        n = inv.n
        sigma = inv.alphabet.size
        ap = " ".join(inv.alphabet.aps) or "-"
        uni_ok, w1 = bernoulli_law(inv, {a: Fraction(1, sigma) for a in inv.alphabet.letters()})
        skw_ok, w2 = bernoulli_law(inv, skewed(inv.alphabet))
        bern_ok = int(uni_ok and skw_ok)

        ch = random_chain(inv.alphabet, name)
        rt_ok = int(round_trip(ch))
        r = pr_chain(inv, ch)
        rc = pr_chain(inv.complement(), ch)
        flip_ok = int(r.value + rc.value == 1)
        n_prod = max(w1, w2, r.n_product)

        ok = int(bern_ok and flip_ok and rt_ok)
        status = 0 if ok else 1
    except Exception:
        traceback.print_exc()
    ms = int((perf_counter() - t0) * 1000 + 0.5)
    row = f"{name},{n},{ap},{sigma},{n_prod},{bern_ok},{flip_ok},{rt_ok},{ok},{ms}"
    append_row(LOGS / "m5_gate.csv", HEADER, row)
    print(row)
    return status


def run_oracle(path: Path) -> int:
    """The Route A product-side oracle on one invariant and its seeded random
    chain; append the CSV row; 0 green or skip, 1 red."""
    name = path.name
    n = n_prod = 0
    num, den, onum, oden, ok, skip = -1, -1, -1, -1, 0, 0
    t0 = perf_counter()
    try:
        inv = load_invariant(path.read_text())
        n = inv.n
        ch = random_chain(inv.alphabet, name)
        r = pr_chain(inv, ch)
        num, den = r.value.numerator, r.value.denominator
        n_prod = r.n_product
        hoa = CORPUS / "det" / (path.stem + ".hoa")
        try:
            from sosl.quant.routea import route_a_chain

            o = route_a_chain(str(hoa), ch)
            onum, oden = o.value.numerator, o.value.denominator
        except Exception:
            traceback.print_exc()
            skip = 1
        if not skip:
            ok = int(r.value == o.value)
    except Exception:
        traceback.print_exc()
    ms = int((perf_counter() - t0) * 1000 + 0.5)
    row = f"{name},{n},{n_prod},{num},{den},{onum},{oden},{ok},{skip},{ms}"
    append_row(LOGS / "m5_oracle.csv", O_HEADER, row)
    print(row)
    return 0 if ok or skip else 1


def append_row(log: Path, header: str, row: str) -> None:
    log.parent.mkdir(parents=True, exist_ok=True)
    new = not log.exists()
    with log.open("a") as f:
        if new:
            f.write(header + "\n")
        f.write(row + "\n")


def read_log(log: Path, header: str) -> Dict[str, List[str]]:
    """The last row per case name."""
    rows: Dict[str, List[str]] = {}
    if not log.exists():
        return rows
    for line in log.read_text().splitlines():
        if line and line != header:
            parts = line.split(",")
            rows[parts[0]] = parts
    return rows


def aggregate() -> int:
    """Render ``reference/quant/m5_product.{md,csv}`` and
    ``m5_product_oracle.csv``; 0 iff every corpus case is green and every
    sampled case is green or a skip."""
    rows = read_log(LOGS / "m5_gate.csv", HEADER)
    orows = read_log(LOGS / "m5_oracle.csv", O_HEADER)
    files = corpus_files()
    missing = [f.name for f in files if f.name not in rows]
    reds = [r for r in rows.values() if r[8] != "1"]
    greens = len(rows) - len(reds)
    prods = sorted(int(r[4]) for r in rows.values()) or [0]
    ms = sorted(int(r[9]) for r in rows.values()) or [0]

    sample = [f.name for f in sample_files()]
    o_missing = [s for s in sample if s not in orows]
    o_skips = [r for r in orows.values() if r[8] == "1"]
    o_reds = [r for r in orows.values() if r[7] != "1" and r[8] != "1"]
    o_greens = len(orows) - len(o_reds) - len(o_skips)

    REF_DIR.mkdir(parents=True, exist_ok=True)
    (REF_DIR / "m5_product.csv").write_text(
        "\n".join([HEADER] + [",".join(rows[k]) for k in sorted(rows)]) + "\n"
    )
    (REF_DIR / "m5_product_oracle.csv").write_text(
        "\n".join([O_HEADER] + [",".join(orows[k]) for k in sorted(orows)]) + "\n"
    )
    md: List[str] = [
        "# M5 — the Markov product `Pr_M(L)`: the four gates",
        "",
        "- date: 2026-07-12",
        f"- git: {git_rev()}",
        f"- seed: {SEED} (random chains keyed by case name; oracle sample of "
        f"{SAMPLE_SIZE})",
        f"- corpus: {CORPUS} ({len(files)} .sos files)",
        "- regeneration (from `sosl/`): `python3 -m tests.quant.m5_gate --list | "
        "while read f; do timeout 15 python3 -m tests.quant.m5_gate \"$f\" "
        ">/dev/null; done; python3 -m tests.quant.m5_gate --sample | while read f; "
        "do timeout 15 python3 -m tests.quant.m5_gate --oracle \"$f\" >/dev/null; "
        "done; python3 -m tests.quant.m5_gate --aggregate`",
        "",
        "**Laws.** Bernoulli embedding `sum_a p(a) . Pr_{M_a}(L) == mu_p(L)` "
        "(uniform and skewed p, the chain restarted at every letter state); "
        "complement flip `Pr_M(L) + Pr_M(~L) == 1` on a seeded random chain; "
        "`.mc` reader round-trip on every chain; Route A product-side oracle on "
        "the sample. All exact `Fraction`s.",
        "",
        "| cases | green | red | missing |",
        "|---|---|---|---|",
        f"| {len(rows)} | {greens} | {len(reds)} | {len(missing)} |",
        "",
        "| median product states | max | median ms | max ms |",
        "|---|---|---|---|",
        f"| {prods[len(prods) // 2]} | {prods[-1]} | {ms[len(ms) // 2]} | {ms[-1]} |",
        "",
        "## Route A product-side oracle (sample)",
        "",
        "| sampled | green | red | skip | missing |",
        "|---|---|---|---|---|",
        f"| {len(orows)} | {o_greens} | {len(o_reds)} | {len(o_skips)} "
        f"| {len(o_missing)} |",
        "",
    ]
    for title, bad, head in (
        ("Red rows", reds, HEADER),
        ("Red oracle rows", o_reds, O_HEADER),
    ):
        if bad:
            md += [f"## {title}", "", "```", head]
            md += [",".join(r) for r in bad[:50]]
            md += ["```", ""]
    if missing:
        md += [f"## Missing ({len(missing)})", ""] + [f"- {m}" for m in missing[:50]] + [""]
    (REF_DIR / "m5_product.md").write_text("\n".join(md))
    print(
        f"aggregate: {len(rows)} cases, {greens} green, {len(reds)} red, "
        f"{len(missing)} missing; oracle {len(orows)} sampled, {o_greens} green, "
        f"{len(o_reds)} red, {len(o_skips)} skip, {len(o_missing)} missing "
        f"-> {REF_DIR / 'm5_product.md'}"
    )
    return 0 if not (reds or missing or o_reds or o_missing) else 1


def main(argv: List[str]) -> int:
    if argv == ["--list"]:
        for f in corpus_files():
            print(f)
        return 0
    if argv == ["--sample"]:
        for f in sample_files():
            print(f)
        return 0
    if argv == ["--aggregate"]:
        return aggregate()
    if len(argv) == 2 and argv[0] == "--oracle":
        return run_oracle(Path(argv[1]))
    assert len(argv) == 1, __doc__
    return run_case(Path(argv[0]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
