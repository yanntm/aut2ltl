"""E1 census driver — the compression scatter over the flat_canon corpus.

Per instance: parse `genaut/corpus/flat_canon/det/<name>.hoa` (already
canonical D — `spot.automaton` + `sos_sdd.hoa.digest_twa`, no
postprocess), run the full pipeline under per-instance budgets, emit
`.sos`, and byte-compare against the precomputed corpus reference
`flat_canon/sos/<name>.sos` (the two tiers are a self-consistent pair,
so the spec §3 conformance gate needs no reference run). Records one CSV
row per case (appended as produced — a killed sweep keeps its prefix)
and one stats JSONL per instance; a blown budget is a status row
carrying its phase, never an abort (spec §3); a byte MISMATCH is
recorded, printed loudly, and the sweep continues.

CSV columns: instance name; status (OK / MISMATCH / TIME_BUDGET /
DIAGRAM_BUDGET / ERROR); phase reached on a budget finding; digest shape
(states, APs, marks, letter classes — the guard-equal-letters covariate);
|EM¹|, closure depth, invariant classes; final/peak diagram nodes; wall
ms; conformance verdict.

Usage (from the repo root):
    python3 tests/sos_sdd/e1_census.py <name> [...]   # named instances
    python3 tests/sos_sdd/e1_census.py --all          # the whole corpus
    --budget <seconds>   engine time budget per instance (default 10)
    --nodes <n>          engine node budget (default 0 = unlimited)
    --shard <k>/<N>      with --all: slice k of N (cluster runs fan the
                         corpus over ~300 such jobs; each shard appends
                         to its own census_<k>of<N>.csv, no write races)
    --isolate            fresh subprocess per instance under the repo's
                         bounded runner (aut2ltl.bounded: timeout
                         --signal=INT --kill-after=1 — the SIGKILL is
                         unconditional, the C++ core observes no
                         signals), hard-killed at budget + 5s; names
                         already in the CSV are skipped (resume). A hard
                         kill that outran the engine's own TimeBudget is
                         ledgered as a KILLED row. MANDATORY for big
                         in-machine sweeps: libDDD's unique table is
                         never GC'd, so one process accumulates every
                         instance's diagrams and OOMs at corpus scale.
    --out <csv>          override the CSV name (internal: isolate/shard
                         children write where their parent points)
Outputs under tests/sos_sdd/logs/e1/: census.csv (or the shard CSV)
+ <name>.jsonl per instance.
"""

import csv
import sys
import time
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import spot  # noqa: E402

from sos_sdd import Engine  # noqa: E402
from sos_sdd.errors import DiagramBudget, TimeBudget  # noqa: E402
from sos_sdd.hoa import digest_twa  # noqa: E402
from sos_sdd.letters import letter_classes  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
CORPUS = REPO / "genaut" / "corpus" / "flat_canon"
OUT = Path(__file__).resolve().parent / "logs" / "e1"

FIELDS = ["name", "status", "phase", "states", "n_ap", "marks",
          "letter_classes", "em1", "depth", "classes",
          "nodes_final", "nodes_peak", "ms", "conform"]


def run_one(name: str, budget: float, nodes: int) -> dict:
    row: dict = {f: "" for f in FIELDS}
    row["name"] = name
    t0 = time.monotonic()
    try:
        aut = digest_twa(spot.automaton(str(CORPUS / "det" / f"{name}.hoa")), name)
        row.update(states=aut.states, n_ap=len(aut.ap), marks=aut.marks,
                   letter_classes=len(letter_classes(aut)))
        eng = Engine(square="off", time_budget=budget, node_budget=nodes,
                     stats=str(OUT / f"{name}.jsonl"))
        s = eng.build(aut, until_phase=6)
        got = s.to_sos()
        final, peak = s.nodes
        row.update(em1=int(s.em1_count()), depth=s.depth, classes=s.n_classes(),
                   nodes_final=final, nodes_peak=peak)
        want = (CORPUS / "sos" / f"{name}.sos").read_text()
        if got == want:
            row.update(status="OK", conform="byte-equal")
        else:
            row.update(status="MISMATCH", conform="DIVERGES")
            print(f"*** MISMATCH {name}: engine .sos diverges from corpus "
                  f"reference — stop-the-line, inspect with conformance_diff")
    except TimeBudget as e:
        row.update(status="TIME_BUDGET", phase=e.phase)
    except DiagramBudget as e:
        row.update(status="DIAGRAM_BUDGET", phase=e.phase)
    except Exception as e:  # noqa: BLE001 — ERROR rows are findings too
        row.update(status="ERROR", conform=f"{type(e).__name__}: {e}")
    row["ms"] = round((time.monotonic() - t0) * 1e3, 1)
    return row


def run_isolated(names: List[str], out: Path, out_name: str,
                 budget: float, nodes: int) -> None:
    """One bounded subprocess per instance; the child appends its own CSV
    row, the parent ledgers only hard kills and crashes."""
    from aut2ltl import bounded
    done: set = set()
    if out.exists():
        with out.open() as fh:
            done = {r["name"] for r in csv.DictReader(fh)}
    todo = [n for n in names if n not in done]
    print(f"isolate: {len(todo)} to run ({len(done)} already in {out.name})")
    counts: dict = {}
    with out.open("a", newline="") as fh:
        w = csv.DictWriter(fh, FIELDS)
        if not done and todo:
            w.writeheader()
            fh.flush()
        for k, name in enumerate(todo):
            res = bounded.run([sys.executable, str(Path(__file__).resolve()),
                               name, "--budget", str(budget),
                               "--nodes", str(nodes), "--out", out_name],
                              int(budget) + 5)
            if res.timed_out or res.rc != 0:
                status = "KILLED" if res.timed_out else f"CRASH_rc{res.rc}"
                w.writerow({"name": name, "status": status,
                            "ms": round(res.wall_s * 1e3, 1)})
                fh.flush()
            else:
                status = "child"
            counts[status] = counts.get(status, 0) + 1
            if (k + 1) % 25 == 0:
                print(f"[{k + 1}/{len(todo)}] {counts}")
    print(f"done: {len(todo)} instances, {counts} -> {out}")


def main() -> None:
    args = sys.argv[1:]
    budget, nodes = 10.0, 0
    if "--budget" in args:
        i = args.index("--budget")
        budget = float(args[i + 1]); del args[i:i + 2]
    if "--nodes" in args:
        i = args.index("--nodes")
        nodes = int(args[i + 1]); del args[i:i + 2]
    shard: Optional[str] = None
    if "--shard" in args:
        i = args.index("--shard")
        shard = args[i + 1]; del args[i:i + 2]
    isolate = "--isolate" in args
    if isolate:
        args.remove("--isolate")
    out_name = "census.csv"
    if "--out" in args:
        i = args.index("--out")
        out_name = args[i + 1]; del args[i:i + 2]
    if args == ["--all"]:
        names: List[str] = sorted(p.stem for p in (CORPUS / "det").glob("*.hoa"))
        if shard is not None:
            k, n = (int(x) for x in shard.split("/"))
            names = names[k::n]
            out_name = f"census_{k}of{n}.csv"
    else:
        names = args
    if not names:
        print(__doc__)
        return

    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / out_name
    if isolate:
        run_isolated(names, out, out_name, budget, nodes)
        return
    fresh = not out.exists()
    counts: dict = {}
    with out.open("a", newline="") as fh:
        w = csv.DictWriter(fh, FIELDS)
        if fresh:
            w.writeheader()
        for k, name in enumerate(names):
            row = run_one(name, budget, nodes)
            w.writerow(row)
            fh.flush()
            counts[row["status"]] = counts.get(row["status"], 0) + 1
            if len(names) > 1 and (k + 1) % 500 == 0:
                print(f"[{k + 1}/{len(names)}] {counts}")
            elif len(names) <= 10:
                print({f: row[f] for f in FIELDS if row[f] != ""})
    print(f"done: {len(names)} instances, {counts} -> {out}")


if __name__ == "__main__":
    main()
