"""Summarize the SY1 census CSV into the tables the report cites.

    python3 -m tests.symmetry.sy1_summary   # reads logs/sy1_generators.csv,
                                            # writes logs/sy1_summary.md

Aggregates the campaign CSV and counts the corpus `.cat` classification
tags (LTL bit, stutter tag) — no re-checks; regenerating the CSV
(`sigma_gate --campaign`) then this script reproduces every number in report
findings F2–F4 and the report's corpus note.
"""
from __future__ import annotations

import glob
import os
from collections import Counter
from typing import Dict, List

_HERE = os.path.dirname(os.path.abspath(__file__))
_CSV = os.path.join(_HERE, "logs", "sy1_generators.csv")
_OUT = os.path.join(_HERE, "logs", "sy1_summary.md")
_CORPUS = os.path.abspath(
    os.path.join(_HERE, "..", "..", "..", "genaut", "corpus", "flat_canon", "sos")
)


def main() -> None:
    header: List[str] = []
    rows: List[Dict[str, str]] = []
    cols: List[str] = []
    for line in open(_CSV):
        line = line.rstrip("\n")
        if line.startswith("#"):
            header.append(line)
            continue
        if not cols:
            cols = line.split(",")
            continue
        rows.append(dict(zip(cols, line.split(","))))

    n_cases = len(rows)
    by_n = Counter(r["n_aps"] for r in rows)
    status = Counter(r["status"] for r in rows)
    inert_nonempty = [r for r in rows if r["inert_set"]]
    sym_hit = [r for r in rows if r["sym_generator_hits"]]
    anti_hit = [r for r in rows if r["anti_generator_hits"]]
    anti_poss = [r for r in rows if r["anti_possible"] == "1"]
    gen_sym = Counter(
        g for r in rows for g in r["sym_generator_hits"].split(";") if g
    )
    gen_anti = Counter(
        g for r in rows for g in r["anti_generator_hits"].split(";") if g
    )
    # candidates actually checked (kernel/obstruction law asserted on each):
    # per ok row, the generators + the full sweep when it ran.
    def n_gens(n: int) -> int:
        return n * (n - 1) // 2 + n

    def group(n: int) -> int:
        out = 1
        for k in range(1, n + 1):
            out *= k
        return (1 << n) * out

    checks = sum(
        n_gens(int(r["n_aps"]))
        + (group(int(r["n_aps"])) if r["sym_full_count"] != "-1" else 0)
        for r in rows
        if r["status"] == "ok"
    )
    full_rows = [r for r in rows if r["sym_full_count"] != "-1"]
    sym_full_dist = Counter(r["sym_full_count"] for r in full_rows)
    wall = sorted(float(r["wall_ms"]) for r in rows)

    def pct(k: int) -> str:
        return f"{100.0 * k / n_cases:.4f}".rstrip("0").rstrip(".") + "%"

    with open(_OUT, "w") as out:
        out.write("\n".join(header) + "\n\n# SY1 census summary\n\n")
        out.write(f"- cases: **{n_cases}**")
        out.write(f" (by AP count: {dict(sorted(by_n.items()))})\n")
        out.write(f"- status: {dict(status)}\n")
        ltl = Counter(); stutter = Counter()
        for cat in sorted(glob.glob(os.path.join(_CORPUS, "*.cat"))):
            for line in open(cat):
                if line.startswith("ltl:"):
                    ltl[line.split(":", 1)[1].strip()] += 1
                elif line.startswith("stutter:"):
                    stutter[line.split(":", 1)[1].strip()] += 1
        out.write(
            f"- corpus `.cat` tags: LTL {dict(sorted(ltl.items()))}, "
            f"stutter {dict(sorted(stutter.items()))}\n"
        )
        out.write(
            f"- candidate checks with kernel+obstruction law asserted: "
            f"**{checks}** — zero violations (a violation aborts the run)\n"
        )
        out.write(
            f"- wall per case ms: median {wall[len(wall) // 2]:.1f}, "
            f"p95 {wall[int(0.95 * len(wall))]:.1f}, max {wall[-1]:.1f}\n\n"
        )
        out.write("## F3 — inert APs\n\n")
        out.write(
            f"- nonempty `inert_aps`: **{len(inert_nonempty)}** / {n_cases} "
            f"({pct(len(inert_nonempty))})\n\n"
        )
        out.write("## F4 — generator hits\n\n")
        out.write(
            f"- cases with ≥1 symmetric generator: **{len(sym_hit)}** "
            f"({pct(len(sym_hit))}); per generator: "
            f"{dict(sorted(gen_sym.items()))}\n"
        )
        out.write(
            f"- cases with ≥1 anti generator: **{len(anti_hit)}** "
            f"({pct(len(anti_hit))}); per generator: "
            f"{dict(sorted(gen_anti.items()))}\n"
        )
        out.write(
            f"- `anti_possible` true: **{len(anti_poss)}** ({pct(len(anti_poss))}) "
            f"— the pair-count fast path closes the anti question on the other "
            f"{n_cases - len(anti_poss)} cases ({pct(n_cases - len(anti_poss))})\n\n"
        )
        out.write("## Full B_n sweep (n ≤ 3 rows)\n\n")
        out.write(f"- rows swept: {len(full_rows)}\n")
        out.write(
            "- symmetric-element count distribution (identity included): "
            f"{dict(sorted(sym_full_dist.items(), key=lambda kv: int(kv[0])))}\n"
        )
    print(f"wrote {_OUT}")


if __name__ == "__main__":
    main()
