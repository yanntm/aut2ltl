"""survey.report — CSV emission and run summaries.

The per-row CSV schema (kept identical to the legacy survey for now) plus a
compact summary. Comparing two result CSVs lives in survey.diff.results;
comparing two LANGUAGES lives in survey.diff (ltl_diff).
"""
from __future__ import annotations

import csv
from typing import Dict, List, Sequence, TextIO

# The legacy column set, reused verbatim (provenance/relative-path is deferred).
COLS: List[str] = ["formula", "class", "mp", "technique", "dag_nodes",
                   "temporals", "tree_nodes", "sharing", "build_s", "equiv",
                   "reconstructed"]

# An ANSWER is an input the tool reconstructed (a DAG), whether or not the oracle
# then confirmed it; "built" is the answered-but-unverified case (--no-verify).
_ANSWER_CATS = ("validated", "spot_timeout", "unverified", "spot_err", "false",
                "built")


def write_csv(rows: Sequence[Dict[str, object]], fileobj: TextIO,
              cols: Sequence[str] = COLS) -> None:
    """Write `rows` as CSV to an open text stream (a file, or stdout)."""
    writer = csv.DictWriter(fileobj, fieldnames=list(cols))
    writer.writeheader()
    for r in rows:
        writer.writerow(r)


def _num(v: object) -> float:
    try:
        return float(v)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


def _category(equiv: str) -> str:
    if equiv == "True":
        return "validated"
    if equiv == "FALSE":
        return "false"
    if equiv == "SPOT_TIMEOUT":
        return "spot_timeout"
    if equiv == "UNVERIFIED_SIZE":
        return "unverified"
    if equiv == "DECLINED":
        return "declined"
    if equiv in ("NOT_LTL", "PROBABLY_NOT_LTL"):
        return "not_ltl"
    if equiv.startswith("SPOT_ERR"):
        return "spot_err"
    if equiv.startswith("BUILD_TIMEOUT"):
        return "build_timeout"
    if equiv == "":
        return "built"           # answered, not verified (--no-verify, status OK)
    return "build_crash"         # the tool actually threw (a real defect)


def summarize(rows: Sequence[Dict[str, object]], label: str) -> List[str]:
    """The compact summary lines for one technique's rows (the CSV holds the
    per-input detail). Build time is construction only — not spot verification."""
    cat: Dict[str, int] = {}
    for r in rows:
        c = _category(str(r.get("equiv") or ""))
        cat[c] = cat.get(c, 0) + 1
    g = cat.get
    answers = [r for r in rows if _category(str(r.get("equiv") or "")) in _ANSWER_CATS]
    dag = sum(int(_num(r.get("dag_nodes"))) for r in answers)
    temp = sum(int(_num(r.get("temporals"))) for r in answers)
    build = sum(_num(r.get("build_s")) for r in answers)

    ltl_built = len(answers)
    not_ltl = g("not_ltl", 0)
    produced = ltl_built + not_ltl
    our_fail = g("build_timeout", 0) + g("build_crash", 0) + g("declined", 0)
    equivalent = g("validated", 0)
    not_checked = g("unverified", 0) + g("spot_timeout", 0) + g("spot_err", 0)
    wrong = g("false", 0)

    lines = [
        f"survey: {len(rows)} inputs  (--use {label})",
        f"aut2ltl answered: {produced}/{len(rows)}  "
        f"({ltl_built} LTL built + {not_ltl} not-LTL)   |   "
        f"Failures: {our_fail}  (timeout {g('build_timeout', 0)}, "
        f"crash {g('build_crash', 0)}, declined {g('declined', 0)})",
    ]
    if equivalent or wrong or not_checked:   # verification ran for some rows
        lines.append(f"Spot check of the {ltl_built} LTL built: {equivalent} "
                     f"EQUIVALENT, {not_checked} not checked (formula too large)")
        lines.append(f"NOT EQUIVALENT: {wrong}"
                     + ("   *** INVESTIGATE — see FALSE rows ***" if wrong
                        else "   (clean)"))
    lines.append(f"totals over LTL built: DAG={dag} temporals={temp} "
                 f"build={build:.3f}s")
    lines.append("FAIL" if wrong else "SUCCESS")
    return lines
