"""M3b: the Thm 4.4(2) biconditional, assertion-only (spec section 9.1).

    python3 -m tests.quant.m3b_gate A.sos B.sos   the biconditional on one pair
    python3 -m tests.quant.m3b_gate --aggregate   logs -> reference/quant/m3b_thm442.{md,csv}

On one aligned pair: byte-equal reduced essential forms ⟺ all-zero
aligned xor-profile (the null-disagreement read-off), asserted in BOTH
directions. Runs on M3's own 1000-pair sample
(``tests/quant/logs/m3_pair_sample.txt``, seed 1) — regenerate it with
``python3 -m tests.quant.m3_gate --pairs 1000 1`` if absent. A
violation in either direction convicts paper Thm 4.4(2): stop the
line, file against the paper.

Row ``a,b,null,es_eq,ok,ms`` to ``tests/quant/logs/m3b_pairs.csv``.
Exit: 0 green, 1 red. Budget kills (15s `timeout`) leave no row and
are counted by the aggregate as data.
"""
from __future__ import annotations

import sys
from pathlib import Path
from time import perf_counter
from typing import List

from sosl.sos import dump_invariant, load_invariant
from sosl.quant import distance, essential
from tests.quant.law_gate import append_row, git_rev
from tests.quant.m3_gate import CORPUS, _read_rows

LOGS = Path(__file__).resolve().parent / "logs"
REF_DIR = Path(__file__).resolve().parents[3] / "reference" / "quant"
PAIR_HEADER = "a,b,null,es_eq,ok,ms"


def run_pair(path_a: Path, path_b: Path) -> int:
    """The biconditional on one pair; append the CSV row; 0 green, 1 red."""
    t0 = perf_counter()
    inv_a = load_invariant(path_a.read_text())
    inv_b = load_invariant(path_b.read_text())
    null = distance(inv_a, inv_b).null_disagreement
    es_eq = dump_invariant(essential(inv_a)) == dump_invariant(essential(inv_b))
    ok = int(es_eq == null)
    ms = int((perf_counter() - t0) * 1000 + 0.5)
    row = f"{path_a.name},{path_b.name},{int(null)},{int(es_eq)},{ok},{ms}"
    append_row(LOGS / "m3b_pairs.csv", PAIR_HEADER, row)
    print(row)
    return 0 if ok else 1


def aggregate() -> int:
    """Render ``reference/quant/m3b_thm442.{md,csv}`` from the log;
    0 iff no red row."""
    pairs = _read_rows(LOGS / "m3b_pairs.csv", PAIR_HEADER)
    reds = [r for r in pairs if r[4] != "1"]
    null_pairs = sum(1 for r in pairs if r[2] == "1")
    es_eq_pairs = sum(1 for r in pairs if r[3] == "1")
    sample = LOGS / "m3_pair_sample.txt"
    attempted = len(sample.read_text().splitlines()) if sample.exists() else len(pairs)
    REF_DIR.mkdir(parents=True, exist_ok=True)
    (REF_DIR / "m3b_thm442.csv").write_text(
        "\n".join([PAIR_HEADER] + [",".join(r) for r in pairs]) + "\n"
    )
    md: List[str] = [
        "# M3b — Thm 4.4(2) as a biconditional: essentials ⟺ null xor-profile",
        "",
        "- date: 2026-07-11",
        f"- git: {git_rev()}",
        f"- corpus: {CORPUS} (M3's 1000-pair sample, seed 1)",
        "- regeneration (from `sosl/`): `python3 -m tests.quant.m3_gate "
        "--pairs 1000 1 | tee tests/quant/logs/m3_pair_sample.txt | while "
        "read a b; do timeout 15 python3 -m tests.quant.m3b_gate $a $b "
        ">/dev/null; done; python3 -m tests.quant.m3b_gate --aggregate`",
        "",
        "| law | sample | green | red | budget-blown |",
        "|---|---|---|---|---|",
        f"| byte-equal reduced essentials ⟺ all-zero aligned xor-profile "
        f"({null_pairs} null-disagreement, {es_eq_pairs} essential-equal) "
        f"| {attempted} | {len(pairs) - len(reds)} | {len(reds)} "
        f"| {attempted - len(pairs)} |",
        "",
        "Both directions asserted per pair; a red row in either direction "
        "convicts paper Thm 4.4(2) (stop-the-line). A budget-blown pair "
        "(15s `timeout`) is a recorded datum — no row means the kill.",
        "",
    ]
    if reds:
        md += ["## Red rows", "", "```", PAIR_HEADER]
        md += [",".join(r) for r in reds[:50]] + ["```", ""]
    (REF_DIR / "m3b_thm442.md").write_text("\n".join(md))
    print(
        f"aggregate: {len(pairs)}/{attempted} pairs ({len(reds)} red, "
        f"{null_pairs} null-disagreement, {es_eq_pairs} essential-equal) "
        f"-> {REF_DIR / 'm3b_thm442.md'}"
    )
    return 0 if not reds else 1


def main(argv: List[str]) -> int:
    if argv == ["--aggregate"]:
        return aggregate()
    assert len(argv) == 2, __doc__
    return run_pair(Path(argv[0]), Path(argv[1]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
