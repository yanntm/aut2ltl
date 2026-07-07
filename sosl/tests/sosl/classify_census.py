"""X0/X1 — classify a census of automata and profile the results.

    python3 -m tests.sosl.classify_census <folder-or-file> [...] \
        [--limit N] [--budget SECONDS] [--logs DIR]

For every HOA input (a `genaut/corpus/<tag>/` folder, or named files such as
the triptych / stall specimens) this builds the reference invariant, classifies
it (`sosl.sos.classify.classify`), and runs the duality gate — classifying the
complement and asserting the C section 7 swaps. It records one JSON line per
input and prints the X1 distribution: aperiodicity, rung membership, the
`(m,n)` coordinate multiset, and the Wagner degrees `phi` seen.

Per-input budget (default 15s, the repo cap) via a real-time alarm: a build or
classification that overruns is a BUDGET verdict, not a failure — the ceiling is
the construction, not the classifier (spec X3/F3). Verdicts per input:
SOUND (classified, duality holds), PARTIAL (gamma needs the derivative),
MISMATCH (duality or an internal law broke — a bug), BUDGET (overran or the
construction raised). Self-terminating; run large buckets in the background.
"""
from __future__ import annotations

import json
import os
import signal
import sys
import time
from collections import Counter
from typing import Dict, List, Optional, Tuple

from sosl.sos import Invariant
from sosl.sos.build import ReferenceError, reference_of_hoa
from sosl.sos.classify import classify, record_to_dict

_LOGS = os.path.join(os.path.dirname(__file__), "logs", "classify_census")
_FLIP = {"sigma": "pi", "pi": "sigma", "delta": "delta", "PARTIAL": "PARTIAL"}


class _Budget(Exception):
    pass


def _complement(inv: Invariant) -> Invariant:
    linked = inv.linked_pairs()
    return Invariant(inv.alphabet, inv.keys, inv.letter_class, inv.mult,
                     accept=frozenset(linked - inv.accept), identity=inv.identity)


def _duality_ok(inv: Invariant) -> bool:
    a = classify(inv)
    b = classify(_complement(inv))
    return (
        (a.m_plus, a.m_minus) == (b.m_minus, b.m_plus)
        and (a.n_plus, a.n_minus) == (b.n_minus, b.n_plus)
        and b.sign == _FLIP[a.sign]
        and (a.rungs.open, a.rungs.dba) == (b.rungs.closed, b.rungs.dca)
        and (a.rungs.closed, a.rungs.dca) == (b.rungs.open, b.rungs.dba)
        and a.rungs.weak == b.rungs.weak
        and str(a.gamma) == str(b.gamma)
    )


def _one(path: str, budget: int) -> Dict:
    """Classify one HOA file under the alarm budget; return its JSON record."""
    rec: Dict = {"case": os.path.basename(path)}
    t0 = time.time()
    signal.setitimer(signal.ITIMER_REAL, budget)
    try:
        inv = reference_of_hoa(path)
        r = classify(inv)
        doc = record_to_dict(r)
        ok = _duality_ok(inv)
        signal.setitimer(signal.ITIMER_REAL, 0)
        rec.update(
            classes=inv.n, aperiodic=r.aperiodic,
            m_plus=r.m_plus, m_minus=r.m_minus, n_plus=r.n_plus, n_minus=r.n_minus,
            rungs=doc["rungs"], phi=doc["phi"], gamma_partial=r.gamma_partial,
            verdict=("MISMATCH" if not ok else
                     "PARTIAL" if r.gamma_partial else "SOUND"),
        )
    except _Budget:
        rec.update(verdict="BUDGET", error="timeout")
    except (ReferenceError, MemoryError) as exc:
        rec.update(verdict="BUDGET", error=f"{type(exc).__name__}: {exc}")
    except AssertionError as exc:
        rec.update(verdict="MISMATCH", error=f"internal law: {exc}")
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    rec["wall"] = round(time.time() - t0, 3)
    return rec


def _inputs(args: List[str]) -> List[str]:
    files: List[str] = []
    for a in args:
        if os.path.isdir(a):
            files += sorted(os.path.join(a, f) for f in os.listdir(a)
                            if f.endswith(".hoa"))
        elif a.endswith(".hoa"):
            files.append(a)
    return files


def run(argv: List[str]) -> int:
    args, limit, budget, logs = [], None, 15, _LOGS
    it = iter(argv)
    for a in it:
        if a == "--limit":
            limit = int(next(it))
        elif a == "--budget":
            budget = int(next(it))
        elif a == "--logs":
            logs = next(it)
        else:
            args.append(a)

    def _alarm(signum, frame):
        raise _Budget()
    signal.signal(signal.SIGALRM, _alarm)

    files = _inputs(args)
    if limit is not None:
        files = files[:limit]
    if not files:
        print("no HOA inputs found", file=sys.stderr)
        return 1

    os.makedirs(logs, exist_ok=True)
    out = os.path.join(logs, "records.jsonl")
    verdicts: Counter = Counter()
    aperiodic: Counter = Counter()
    rung_tally: Counter = Counter()
    coords: Counter = Counter()
    phis: Counter = Counter()

    with open(out, "w") as fh:
        for path in files:
            rec = _one(path, budget)
            fh.write(json.dumps(rec) + "\n")
            verdicts[rec["verdict"]] += 1
            if rec["verdict"] in ("SOUND", "PARTIAL"):
                aperiodic["LTL" if rec["aperiodic"] else "non-LTL"] += 1
                coords[(rec["m_plus"], rec["m_minus"], rec["n_plus"], rec["n_minus"])] += 1
                phis[tuple(rec["phi"])] += 1
                for name, on in rec["rungs"].items():
                    if on:
                        rung_tally[name] += 1

    n = len(files)
    print(f"=== census profile: {n} inputs -> {out} ===")
    print("verdicts:", dict(verdicts))
    print("aperiodic:", dict(aperiodic))
    print("rungs:", dict(rung_tally))
    print("distinct (m+,m-,n+,n-):", len(coords),
          "  top:", coords.most_common(6))
    print("distinct phi:", len(phis), "  top:", phis.most_common(6))
    return 0 if verdicts["MISMATCH"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
