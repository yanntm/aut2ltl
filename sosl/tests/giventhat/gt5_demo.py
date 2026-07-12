"""GT5 — the given-that survey: one fixed knowledge K against a folder of
properties, run through the real tool.

A client of `survey.collect` (the generic collector) and `survey.discovery`
(sos-only). Enumeration and invocation are the two configurable axes:

  * **enumeration** — `survey.discovery.discover(folder, keep={"sos"})` walks a
    folder into one `Example` per `.sos` property (the `¬φ`s);
  * **invocation** — `GivenThatScenario` maps each `¬φ` × the fixed `K` to the
    normal tool call `python3 -m sosl.sos.giventhat ¬φ.sos K.sos -o B.sos
    --json ...` and grabs the tool's own `--json` stats into the CSV row.

**Validation is the pluggable post step (`Scenario.validate`), and it is OFF
here.** A sound check is external (Spot) and takes only the inputs and the
output — `¬φ.sos`, `K.sos`, `B.sos` — via the two legality inclusions
`P_min ⊆ L(B) ⊆ P_max`. That needs an sos→HOA bridge to feed Spot; the calculus
is Spot-free by design and ships no such exporter yet, so this survey measures
only (legality is meanwhile guaranteed by the always-on `B ∩ P_K == P_min` set
identity inside the tool). Do NOT re-check legality with our own calculus — a
bug shared by construction and check passes both (circular).

    python3 -m tests.giventhat.gt5_demo --knowledge K.sos --folder DIR
            [--budget S] [--limit N] [--logs DIR]

Runs from `sosl/`. Isolation, checkpoint/resume and crash-safety come from the
collector; the resulting `.csv` is promoted by hand to `reference/giventhat/`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Sequence

_HERE = Path(__file__).resolve().parent
_SOSL_ROOT = _HERE.parents[1]
_REPO = _HERE.parents[2]
if str(_REPO) not in sys.path:  # so `survey` and `aut2ltl` (repo root) import
    sys.path.insert(0, str(_REPO))

from survey.collect import Invocation, Row, Scenario, collect  # noqa: E402
from survey.discovery import discover  # noqa: E402
from survey.example import Example  # noqa: E402

_LOGS = _HERE / "logs"
_MODULE = "sosl.sos.giventhat"

# Coarse Manna-Pnueli rank for the drop headline; guarantee/safety are siblings
# (same rank), recurrence/persistence likewise. A drop is rank_out < rank_in.
_RANK = {"clopen": 0, "guarantee": 1, "safety": 1, "obligation": 2,
         "recurrence": 3, "persistence": 3, "reactivity": 4}

_COLS = ["input", "verdict", "n_negphi", "n_k", "n_table", "bits", "n_pmin",
         "n_pmax", "n_b", "rung_in", "rung_out", "stut_in", "stut_out",
         "stut_verdict", "side", "seed", "win", "ratio", "note"]


class GivenThatScenario(Scenario):
    """Each `¬φ` example run against the fixed `K` through the tool main. The
    fixed context (`K`, the work dir) is captured on the instance — the shape
    the collector is built for. Stats come from the tool's own `--json`."""

    columns = _COLS

    def __init__(self, k_path: Path, work_dir: Path) -> None:
        self.k_path = k_path
        self.work_dir = work_dir
        work_dir.mkdir(parents=True, exist_ok=True)

    def _out(self, ex: Example) -> "tuple[Path, Path]":
        stem = Path(ex.value).stem
        return self.work_dir / f"{stem}.B.sos", self.work_dir / f"{stem}.json"

    def invoke(self, ex: Example) -> Invocation:
        b_path, j_path = self._out(ex)
        argv = [sys.executable, "-m", _MODULE, ex.value, str(self.k_path),
                "-o", str(b_path), "--json", str(j_path)]
        return Invocation(argv=argv, cwd=_SOSL_ROOT)

    def extract(self, ex: Example, res) -> Row:
        row: Row = {"input": ex.display}
        _, j_path = self._out(ex)
        if res.timed_out:
            row["verdict"], row["note"] = "TIMEOUT", "budget"
            return row
        if not j_path.exists():
            tail = (res.err or res.out or "no output").strip().splitlines()
            row["verdict"] = "CRASH"
            row["note"] = ((tail[-1][:80] if tail else "") + f" rc={res.rc}")
            return row
        d = json.loads(j_path.read_text())
        v = d["verdict"]
        row["verdict"], row["bits"] = v, d.get("bits", "")
        c = d.get("classes", {})
        row["n_negphi"], row["n_k"] = c.get("neg_phi", ""), c.get("k", "")
        row["n_table"] = c.get("table", "")
        if v != "SIMPLIFIED":
            return row
        row["n_pmin"], row["n_pmax"], row["n_b"] = (
            c.get("p_min", ""), c.get("p_max", ""), c.get("b", ""))
        rung = d.get("rung", ["", ""])
        row["rung_in"], row["rung_out"] = rung[0], rung[1]
        st = d.get("stutter", [None, None])
        row["stut_in"], row["stut_out"] = int(bool(st[0])), int(bool(st[1]))
        row["stut_verdict"] = d.get("stutter_verdict", "")
        row["side"], row["seed"] = d.get("side", ""), d.get("seed", "")
        refs = [c.get("neg_phi"), c.get("p_min"), c.get("p_max")]
        if all(isinstance(x, int) for x in refs) and isinstance(c.get("b"), int):
            row["win"] = int(c["b"] < min(refs))
            row["ratio"] = round(c["b"] / c["neg_phi"], 4)
        return row

    def summary(self, rows: Sequence[Row]) -> List[str]:
        return _summary(rows, self.k_path)


# --- headlines -------------------------------------------------------------


def _median(xs: List[float]) -> float:
    if not xs:
        return float("nan")
    xs = sorted(xs)
    return xs[len(xs) // 2]


def _summary(rows: Sequence[Row], k_path: Path) -> List[str]:
    simp = [r for r in rows if r.get("verdict") == "SIMPLIFIED"]
    settled = sum(1 for r in rows if r.get("verdict") == "SETTLED")
    refuted = sum(1 for r in rows if r.get("verdict") == "REFUTED")
    to = sum(1 for r in rows if r.get("verdict") in ("TIMEOUT", "CRASH"))
    ns = len(simp) or 1

    wins = sum(1 for r in simp if r.get("win") == 1)
    ratios = [float(r["ratio"]) for r in simp if r.get("ratio") not in ("", None)]
    drops = sum(1 for r in simp
                if _RANK.get(str(r.get("rung_out")), 9) < _RANK.get(str(r.get("rung_in")), 9))
    gained = sum(1 for r in simp if r.get("stut_in") == 0 and r.get("stut_out") == 1)
    unknown = sum(1 for r in simp if r.get("stut_verdict") == "UNKNOWN")

    return [
        f"=== GT5: knowledge {k_path.name} vs {len(rows)} properties ===",
        f"outcomes: {len(simp)} SIMPLIFIED, {settled} SETTLED, {refuted} REFUTED, "
        f"{to} timeout/crash",
        f"headline 1 — |C(B)| below all three references: {wins}/{len(simp)} = {wins / ns:.3f}",
        f"headline 2 — median |C(B)|/|C(¬φ)|: {_median(ratios):.3f}",
        f"headline 3 — rung-drop rate: {drops}/{len(simp)} = {drops / ns:.3f}",
        f"headline 4 — stutter gained: {gained}/{len(simp)}; UNKNOWN {unknown}/{len(simp)}",
        "(legality not validated here — sound check awaits an sos→HOA Spot oracle)",
    ]


# --- driver ----------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python3 -m tests.giventhat.gt5_demo",
        description="given-that survey: one fixed K against a folder of sos properties")
    ap.add_argument("--knowledge", required=True, type=Path, help="the fixed K, a .sos file")
    ap.add_argument("--folder", required=True, type=Path, help="folder of ¬φ .sos files")
    ap.add_argument("--budget", type=int, default=15, help="per-property budget (s)")
    ap.add_argument("--limit", type=int, default=None, help="cap the number of properties")
    ap.add_argument("--logs", type=Path, default=_LOGS, help="output dir")
    args = ap.parse_args(argv)

    k_real = args.knowledge.resolve()
    examples = [ex for ex in discover([args.folder], keep={"sos"})
                if Path(ex.value).resolve() != k_real]
    if args.limit is not None:
        examples = examples[:args.limit]
    if not examples:
        print("gt5_demo: no .sos properties found under --folder", file=sys.stderr)
        return 2

    scenario = GivenThatScenario(args.knowledge, args.logs / "gt5_work")
    collect(examples, scenario, csv_path=args.logs / "gt5_demo.csv",
            ckpt_path=args.logs / "gt5_demo.ckpt", budget=args.budget,
            validate=False, verbose=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
