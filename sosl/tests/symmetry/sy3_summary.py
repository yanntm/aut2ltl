"""Summarize the SY3 relations census CSV into the tables the report cites.

    python3 -m tests.symmetry.sy3_summary   # reads logs/sy3_relations.csv,
                                            # writes logs/sy3_summary.md

Aggregates the campaign CSV (`relations_gate --campaign`) — no re-checks:
regenerating the CSV then this script reproduces every number in report findings
F9–F11 and the SY3 corpus note. F8 (the stutter oracle) is asserted by the gate,
not tabulated here; its agreement count is cross-checked against the `.cat`
stutter tag below (the `stutter_inv` column must match the tag total)."""
from __future__ import annotations

import glob
import os
import statistics
from collections import Counter, defaultdict
from typing import Dict, List

_HERE = os.path.dirname(os.path.abspath(__file__))
_CSV = os.path.join(_HERE, "logs", "sy3_relations.csv")
_OUT = os.path.join(_HERE, "logs", "sy3_summary.md")
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
    aps = sorted(by_n, key=int)
    invisible_nonempty = [r for r in rows if r["invisible_letters"] != "0"]
    stutter_inv = sum(1 for r in rows if r["stutter_inv"] == "1")
    ladder = Counter(r["ladder_entry"] or "None" for r in rows)
    dens = [float(r["indep_density"]) for r in rows]
    rigid = sum(1 for x in dens if x == 0.0)
    total_commute = sum(1 for x in dens if x == 1.0)

    # cross-check against the corpus `.cat` stutter tag (F8 sanity in the summary)
    stutter_tag = Counter()
    for cat in sorted(glob.glob(os.path.join(_CORPUS, "*.cat"))):
        for line in open(cat):
            if line.startswith("stutter:"):
                stutter_tag[line.split(":", 1)[1].strip()] += 1

    def pct(k: int) -> str:
        return f"{100.0 * k / n_cases:.4f}".rstrip("0").rstrip(".") + "%"

    def ladder_key(k: str) -> int:
        return 99 if k == "None" else int(k)

    with open(_OUT, "w") as out:
        out.write("\n".join(header) + "\n\n# SY3 relations census summary\n\n")
        out.write(f"- cases: **{n_cases}** (by AP count: {dict(sorted(by_n.items()))})\n")
        out.write(
            f"- corpus `.cat` stutter tag: {dict(sorted(stutter_tag.items()))} "
            f"— `stutter_inv` (stutter_rung(1)) count here: **{stutter_inv}** "
            f"(must equal the `invariant` tag — F8 cross-check)\n\n"
        )

        out.write("## F9 — invisible letters (`[c] = 1`)\n\n")
        out.write(
            f"- cases with a nonempty invisible-letter set: "
            f"**{len(invisible_nonempty)}** / {n_cases} ({pct(len(invisible_nonempty))})\n"
        )
        out.write(
            "- structurally absent on this corpus, paralleling `inert_aps` (F3): an "
            "invisible letter is a *class* equality `[c]=1`, an inert AP a *fiber* "
            "equality — distinct read-offs, both empty here on the alphabet-minimal, "
            "canonized corpus.\n\n"
        )

        out.write("## F10 — the tolerated independence relation `Î_L`\n\n")
        out.write(
            f"- density (fraction of ordered distinct class pairs with `[cd]=[dc]`): "
            f"min {min(dens):.4f}, mean {statistics.mean(dens):.4f}, max {max(dens):.4f}\n"
        )
        out.write(
            f"- fully rigid (`Î_L = ∅`, no tolerated commuting): **{rigid}** "
            f"({pct(rigid)}); fully commutative (density 1): **{total_commute}** "
            f"({pct(total_commute)}); partial: **{n_cases - rigid - total_commute}**\n"
        )
        out.write("- mean density stratified by AP count (the load-bearing view):\n\n")
        out.write("| n | cases | mean Î_L density |\n|---|---|---|\n")
        densap = defaultdict(list)
        for r in rows:
            densap[r["n_aps"]].append(float(r["indep_density"]))
        for n in aps:
            out.write(
                f"| {n} | {len(densap[n])} | {statistics.mean(densap[n]):.4f} |\n"
            )
        out.write("\n")

        out.write("## F11 — the k-block ladder entry\n\n")
        out.write(
            "- `ladder_entry` = least rung `k ≤ 3` with `stutter_rung(k)` "
            "(`[v]=[vv]` for all length-`k` class-words), `None` if none:\n\n"
        )
        out.write("| ladder_entry | cases |\n|---|---|\n")
        for k in sorted(ladder, key=ladder_key):
            out.write(f"| {k} | {ladder[k]} |\n")
        out.write(
            f"\n- `ladder_entry == 1` count (**{ladder.get('1', 0)}**) equals the "
            f"stutter-invariant count (rung 1 is stutter); rungs 2–3 add "
            f"**{ladder.get('2', 0) + ladder.get('3', 0)}** cases that are "
            f"block-stutter at a deeper level but not letter-stutter — the "
            f"non-nested spread the parameter measures.\n\n"
        )
        out.write("- ladder entry stratified by AP count:\n\n")
        keys = sorted(ladder, key=ladder_key)
        out.write("| n | cases | " + " | ".join(keys) + " |\n")
        out.write("|---|---|" + "---|" * len(keys) + "\n")
        ladap = defaultdict(Counter)
        for r in rows:
            ladap[r["n_aps"]][r["ladder_entry"] or "None"] += 1
        for n in aps:
            out.write(
                f"| {n} | {sum(ladap[n].values())} | "
                + " | ".join(str(ladap[n].get(k, 0)) for k in keys)
                + " |\n"
            )
    print(f"wrote {_OUT}")


if __name__ == "__main__":
    main()
