"""survey.run — orchestrate a survey: examples × techniques → rows → CSV/report.

For each requested technique, reconstruct every example (and, unless disabled,
verify it), into the legacy row schema. All rows go to one flat CSV (a file
under --logs, or stdout); a compact summary per technique goes to stdout; the
per-input live trace goes to stderr under --verbose.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from survey import build as _build
from survey import report
from survey import verify as _verify
from survey.example import Example
from survey.techniques import resolve

FORMULA_SHOWN = 80


def _record(ex: Example, technique: Optional[str], *, verify: bool,
            build_timeout: int, equiv_timeout: int) -> Dict[str, object]:
    """One CSV row: BUILD the example (front end), then VERIFY (spot oracle)
    unless disabled. Mirrors the legacy survey_one content."""
    row: Dict[str, object] = {c: "" for c in report.COLS}
    row.update(formula=ex.display, **{"class": "?"}, mp="?", technique="-")

    br = _build.build(ex.value, is_hoa=ex.is_hoa, technique=technique,
                      timeout=build_timeout)
    row["technique"] = br.technique or "-"
    for k in ("dag_nodes", "temporals", "tree_nodes", "sharing"):
        if k in br.report:
            row[k] = br.report[k]
    if br.build_s is not None:
        row["build_s"] = br.build_s

    if br.status != "OK":
        if verify:
            row["mp"] = _verify.verify(ex.value, None, is_hoa=ex.is_hoa,
                                       timeout=equiv_timeout).mp
        row["equiv"] = br.status            # DECLINED / NOT_LTL / BUILD_TIMEOUT / CRASH
        return row

    rec = str(br.rec or "").replace("\n", " ").replace("\r", " ")
    row["reconstructed"] = rec[:FORMULA_SHOWN] + ("…" if len(rec) > FORMULA_SHOWN else "")
    if verify:
        checkable = None if rec.startswith("<unflattened") else rec
        vr = _verify.verify(ex.value, checkable, is_hoa=ex.is_hoa,
                            timeout=equiv_timeout)
        row["mp"] = vr.mp
        if checkable is None:
            row["equiv"] = "UNVERIFIED_SIZE"
        else:
            row["equiv"] = {True: "True", False: "FALSE"}.get(vr.equiv, str(vr.equiv))
    return row


def _trace_header() -> None:
    hdr = (f"  {'formula':26s} {'mp':2s} {'tech':16s} "
           f"{'DAG':>6s} {'temp':>5s} {'build':>7s}  equiv")
    print(hdr, file=sys.stderr)
    print("  " + "-" * (len(hdr) - 2), file=sys.stderr)


def _trace(row: Dict[str, object]) -> None:
    bs = f"{row['build_s']}s" if row["build_s"] != "" else "-"
    print(f"  {str(row['formula']):26.26s} {str(row['mp']):2s} "
          f"{str(row['technique']):16.16s} {str(row['dag_nodes']):>6s} "
          f"{str(row['temporals']):>5s} {bs:>7s}  {row['equiv']}", file=sys.stderr)


def run(examples: Sequence[Example], uses: Sequence[str], *,
        logs_dir: Optional[Path] = None, verify: bool = True,
        verbose: bool = False, build_timeout: int = 15,
        equiv_timeout: int = 15) -> int:
    """Run every example under every resolved technique. Returns 1 iff a verified
    NON-equivalent answer occurred (only possible with verify), else 0."""
    techniques = resolve(uses)
    if verbose:
        _trace_header()

    groups: List[Tuple[str, List[Dict[str, object]]]] = []
    all_rows: List[Dict[str, object]] = []
    for technique in techniques:
        rows: List[Dict[str, object]] = []
        for ex in examples:
            row = _record(ex, technique, verify=verify,
                          build_timeout=build_timeout, equiv_timeout=equiv_timeout)
            rows.append(row)
            all_rows.append(row)
            if verbose:
                _trace(row)
        groups.append((technique or "default", rows))

    # One flat CSV: to a file under --logs, else to stdout.
    if logs_dir is not None:
        logs_dir = Path(logs_dir)
        logs_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = logs_dir / f"survey_{ts}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            report.write_csv(all_rows, fh)
        print(f"CSV: {csv_path}", file=sys.stderr)
    else:
        report.write_csv(all_rows, sys.stdout)

    for label, rows in groups:
        for line in report.summarize(rows, label):
            print(line)

    return 1 if any(r.get("equiv") == "FALSE" for r in all_rows) else 0
