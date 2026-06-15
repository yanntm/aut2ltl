#!/usr/bin/env python3
"""
tests/survey.py — the single survey, driven through the FRONT END.

Unlike the retired probes (which wired straight into the engine API), this
survey reconstructs each formula by spawning the actual command-line tool
(`python3 -m aut2ltl <formula> --ltl`) and reading its stdout (the gated
formula) + stderr report (technique, DAG/tree sizes, build time). So it tests
exactly what a user runs.

For each formula, in two subprocesses with separate budgets (both 15s by
default — a blown budget IS a finding, reported, not waited on):

  1. BUILD   — the front-end tool. Subprocess isolation per formula is automatic
               (each is a fresh `-m aut2ltl` process).
  2. VERIFY  — a test-only spot oracle: classify (spot.mp_class) and, when the
               reconstructed formula is small enough to have been flattened,
               check spot.are_equivalent(original, reconstructed).

The equivalence check is deliberately NOT a CLI flag: it is a heavyweight
diagnosis the tool's clients should never pay for, so it lives here.

equiv verdicts:
  True            — verified equivalent (round-trip sound)
  FALSE           — verified NON-equivalent  ***A TRUE FAILURE***
  SPOT_TIMEOUT    — verification ran out of budget (NOT a failure; construction OK)
  UNVERIFIED_SIZE — formula too big to flatten (gated off), so not checkable here
  SPOT_ERR:...    — Spot could not translate (e.g. >32 acceptance sets)
build-phase outcomes (no equiv): DECLINED / BUILD_TIMEOUT / ERROR:...

Outputs a dense CSV (default tests/logs/survey_<timestamp>.csv) and prints the
overall report as the LAST lines of stdout.

Run from the project root:
    python3 tests/survey.py                      # the curated corpus
    python3 tests/survey.py "GFa & GFb" "FGa"     # specific formulas
    python3 tests/survey.py formulas.txt          # one formula per line (# comments)
    python3 tests/survey.py --use bls,sl          # pass --use through to the tool
    KR_SURVEY_TIMEOUT=30 python3 tests/survey.py  # widen the per-phase budget

HOA-file inputs are planned (the tool already accepts them); this survey
currently feeds LTL strings only.
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from tests.survey_formulas import SURVEY_FORMULAS, KLASS_OF  # noqa: E402

# Per-phase budgets (separate, so a slow case tells us WHICH phase blocked).
BUILD_TIMEOUT = int(os.environ.get("KR_SURVEY_TIMEOUT", "15"))
EQUIV_TIMEOUT = int(os.environ.get("KR_SURVEY_EQUIV_TIMEOUT", "15"))

# Max chars of the reconstructed formula to keep in the CSV (the flat form can
# be huge even when it flattened under the tool's gate).
FORMULA_SHOWN = 80

MP_NAME = {"B": "bottom", "S": "safety", "G": "guarantee", "O": "obligation",
           "R": "recurrence", "P": "persistence", "T": "reactivity"}
MP_ORDER = {"B": 0, "S": 1, "G": 2, "O": 3, "R": 4, "P": 5, "T": 6}

# Test-only spot oracle: classify the original and (when a flattened
# reconstruction is supplied) check equivalence. Inputs travel via stdin — a
# multi-MB flat formula on argv dies with E2BIG.
_VERIFY_CHILD = '''
import sys, json
import spot
p = json.load(sys.stdin)
out = {}
orig = p["orig"]
try:
    fo = spot.formula(orig)
    out["mp"] = spot.mp_class(fo)            # B/S/G/O/R/P/T
except Exception as e:
    out["mp"] = "?"
    out["mp_err"] = str(e)[:90]
rec = p.get("rec")
if rec is None:
    out["equiv"] = None                      # nothing to verify (gated off / build failed)
else:
    try:
        orig_aut = spot.formula(orig).translate("Buchi")
        other = spot.formula(rec)
        if rec not in ("true", "false"):
            other = other.translate("Buchi")
        out["equiv"] = bool(spot.are_equivalent(orig_aut, other))
    except Exception as e:
        out["equiv"] = "SPOT_ERR:" + str(e)[:80]
print("VERIFY_JSON:" + json.dumps(out))
'''


def _parse_report(stderr: str) -> Dict[str, object]:
    """Pull technique / DAG nodes / tree nodes / sharing / build time out of the
    front end's stderr report (`key : value` lines)."""
    out: Dict[str, object] = {}
    for line in stderr.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if key == "technique":
            out["technique"] = val
        elif key == "DAG nodes":
            out["dag_nodes"] = int(val)
        elif key == "tree nodes":
            out["tree_nodes"] = int(val)
        elif key == "sharing":
            out["sharing"] = val.rstrip("x")
        elif key == "build time":
            out["build_s"] = val.rstrip("s")
    return out


def run_build(formula: str, use: Optional[str] = None,
              timeout: int = BUILD_TIMEOUT) -> Dict[str, object]:
    """Reconstruct `formula` via the front-end tool (passing `--use <use>`
    through when given). Returns the parsed report plus `status` (OK / DECLINED
    / BUILD_TIMEOUT / ERROR:...) and `rec` (the formula on stdout, or the
    `<unflattened ...>` placeholder)."""
    cmd = [sys.executable, "-m", "aut2ltl", formula, "--ltl"]
    if use:
        cmd += ["--use", use]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=timeout, cwd=PROJECT_ROOT,
        )
    except subprocess.TimeoutExpired:
        return {"status": f"BUILD_TIMEOUT>{timeout}s"}
    stdout = (proc.stdout or "").strip()
    info = _parse_report(proc.stderr or "")
    if proc.returncode == 1:
        info["status"] = "DECLINED"
        return info
    if proc.returncode != 0 or not stdout:
        msg = (proc.stderr or proc.stdout or "no output").strip().splitlines()
        info["status"] = "ERROR:" + (msg[-1][:90] if msg else "no output")
        return info
    info["status"] = "OK"
    info["rec"] = stdout
    return info


def run_verify(orig: str, rec: Optional[str],
               timeout: int = EQUIV_TIMEOUT) -> Dict[str, object]:
    """Classify `orig` and (when `rec` is a real flattened formula) check
    equivalence, in the test-only spot oracle subprocess."""
    try:
        proc = subprocess.run(
            [sys.executable, "-c", _VERIFY_CHILD],
            input=json.dumps({"orig": orig, "rec": rec}),
            capture_output=True, text=True, timeout=timeout, cwd=PROJECT_ROOT,
        )
    except subprocess.TimeoutExpired:
        return {"mp": "?", "equiv": "SPOT_TIMEOUT"}
    for line in (proc.stdout or "").splitlines():
        if line.startswith("VERIFY_JSON:"):
            return json.loads(line[len("VERIFY_JSON:"):])
    return {"mp": "?", "equiv": "SPOT_ERR:no marker"}


def survey_one(formula: str, use: Optional[str] = None) -> Dict[str, object]:
    """Full per-formula record: BUILD (front end) then VERIFY (spot oracle)."""
    rec_row: Dict[str, object] = {
        "formula": formula,
        "class": KLASS_OF.get(formula, "?"),
        "mp": "?",
        "technique": "-",
        "dag_nodes": "",
        "tree_nodes": "",
        "sharing": "",
        "build_s": "",
        "equiv": "",
        "reconstructed": "",
    }
    build = run_build(formula, use)
    rec_row["technique"] = build.get("technique", "-")
    for k in ("dag_nodes", "tree_nodes", "sharing", "build_s"):
        if k in build:
            rec_row[k] = build[k]

    status = build["status"]
    if status != "OK":
        # build failure/decline: still classify (rec=None), surface the reason as equiv
        rec_row["mp"] = run_verify(formula, None).get("mp", "?")
        rec_row["equiv"] = status
        return rec_row

    rec = str(build.get("rec", ""))
    checkable = None if rec.startswith("<unflattened") else rec
    verify = run_verify(formula, checkable)
    rec_row["mp"] = verify.get("mp", "?")
    if checkable is None:
        rec_row["equiv"] = "UNVERIFIED_SIZE"
    else:
        eq = verify.get("equiv")
        rec_row["equiv"] = {True: "True", False: "FALSE"}.get(eq, str(eq))
    rec_row["reconstructed"] = rec[:FORMULA_SHOWN] + ("…" if len(rec) > FORMULA_SHOWN else "")
    return rec_row


def _load_inputs(args: List[str]) -> List[str]:
    """Positional args are formulas, except an existing file is read one formula
    per line (# comments and blanks skipped). No args ⇒ the curated corpus."""
    if not args:
        return list(SURVEY_FORMULAS)
    formulas: List[str] = []
    for a in args:
        p = Path(a)
        if p.is_file():
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.split("#", 1)[0].strip()
                if line:
                    formulas.append(line)
        else:
            formulas.append(a)
    return formulas


def _report(rows: List[Dict[str, object]]) -> List[str]:
    """The overall report, returned as lines (printed last)."""
    by_verdict: Dict[str, int] = {}
    for r in rows:
        by_verdict[str(r["equiv"])] = by_verdict.get(str(r["equiv"]), 0) + 1
    fails = [r for r in rows if r["equiv"] == "FALSE"]
    errs = [r for r in rows if str(r["equiv"]).startswith(("ERROR", "BUILD_TIMEOUT", "DECLINED"))]

    lines = ["", "=== survey report ===", f"cases: {len(rows)}"]
    for verdict in sorted(by_verdict, key=lambda v: (v != "True", v != "FALSE", v)):
        tag = "  <-- TRUE FAILURES" if verdict == "FALSE" else ""
        lines.append(f"  {verdict:18s}: {by_verdict[verdict]}{tag}")
    if fails:
        lines.append("")
        lines.append("TRUE FAILURES (verified non-equivalent):")
        for r in fails:
            lines.append(f"  {r['formula']}  (class={r['class']}, mp={r['mp']})")
    if errs:
        lines.append("")
        lines.append("build problems:")
        for r in errs:
            lines.append(f"  {r['formula']}  -> {r['equiv']}")
    verdict_ok = by_verdict.get("True", 0)
    lines.append("")
    lines.append(f"BOTTOM LINE: {verdict_ok}/{len(rows)} verified equivalent; "
                 f"{len(fails)} true failure(s).")
    return lines


def main() -> int:
    import argparse
    p = argparse.ArgumentParser(
        description="Survey the aut2ltl front end over a corpus of LTL formulas.")
    p.add_argument("inputs", nargs="*",
                   help="formulas, or a file (one formula per line); empty = curated corpus")
    p.add_argument("--use", metavar="T1,T2,...",
                   help="techniques to cite, passed through to the tool's --use")
    args = p.parse_args()

    formulas = _load_inputs(args.inputs)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    logs = PROJECT_ROOT / "tests" / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    csv_path = Path(os.environ.get("KR_SURVEY_CSV", str(logs / f"survey_{ts}.csv")))

    print("=== aut2ltl front-end survey ===")
    print(f"{len(formulas)} formulas  (build budget {BUILD_TIMEOUT}s, "
          f"equiv budget {EQUIV_TIMEOUT}s, isolated per formula"
          f"{', --use ' + args.use if args.use else ''})\n")
    hdr = (f"  {'formula':26s} {'mp':2s} {'tech':16s} "
           f"{'DAG':>6s} {'tree':>12s} {'build':>7s}  equiv")
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))

    rows: List[Dict[str, object]] = []
    cols = ["formula", "class", "mp", "technique", "dag_nodes", "tree_nodes",
            "sharing", "build_s", "equiv", "reconstructed"]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        for formula in formulas:
            row = survey_one(formula, args.use)
            rows.append(row)
            writer.writerow(row)
            fh.flush()
            bs = f"{row['build_s']}s" if row["build_s"] != "" else "-"
            print(f"  {formula:26.26s} {str(row['mp']):2s} "
                  f"{str(row['technique']):16.16s} "
                  f"{str(row['dag_nodes']):>6s} {str(row['tree_nodes']):>12s} "
                  f"{bs:>7s}  {row['equiv']}")

    for line in _report(rows):
        print(line)
    print(f"\nCSV: {csv_path}")
    # exit non-zero iff a TRUE failure (verified non-equivalent) occurred
    return 1 if any(r["equiv"] == "FALSE" for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
