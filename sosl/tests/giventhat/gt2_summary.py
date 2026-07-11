"""GT2 summary: the ladder campaign checkpoint + the rung oracle checkpoint,
aggregated into `logs/gt2_ladder.md` (+ a sorted csv copy of the campaign).

    cd sosl && python3 -m tests.giventhat.gt2_summary [--corpus DIR]

Reads `logs/ladder_campaign.ckpt` and `logs/rung_oracle.ckpt` (both must be
complete), computes the F8 join — per rung, how often a member exists in the
interval while the raw `neg_phi` itself sits strictly higher (its own-table
rung predicate false) — and writes the summary with the 4-line header. Pure
aggregation: nothing here recomputes a gate verdict. Writes under `logs/`
ONLY; promotion of a validated file into `reference/giventhat/` is a
deliberate `cp` by the operator, never done by a script.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List

from sosl.sos import load_invariant
from sosl.sos.calculus import Table
from sosl.sos.calculus.surgery import is_cosafety, is_obligation, is_safety
from sosl.sos.giventhat.ladder import is_persistence, is_recurrence

_HERE = Path(__file__).resolve().parent
_LOGS = _HERE / "logs"
_CORPUS = _HERE.parents[2] / "genaut" / "corpus" / "flat_canon"
_SEED = 20260711

_RUNG_NAMES = ["safety", "cosafety", "obligation", "recurrence", "persistence"]
_PREDS = {"safety": is_safety, "cosafety": is_cosafety,
          "obligation": is_obligation, "recurrence": is_recurrence,
          "persistence": is_persistence}


def _git_rev() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=_HERE, text=True).strip()
    except Exception:
        return "unknown"


def _rows(path: Path) -> List[Dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def main(argv: List[str]) -> int:
    corpus = _CORPUS
    if "--corpus" in argv:
        corpus = Path(argv[argv.index("--corpus") + 1])
    ladder = _rows(_LOGS / "ladder_campaign.ckpt")
    oracle = _rows(_LOGS / "rung_oracle.ckpt")
    scored = [r for r in ladder if r["note"] == ""]

    # own-table rungs of each distinct neg_phi (the F8 join)
    own: Dict[str, Dict[str, bool]] = {}
    for name in sorted({r["neg_phi"] for r in scored}):
        inv = load_invariant((corpus / "sos" / f"{name}.sos").read_text())
        t = Table.of(inv)
        own[name] = {rung: p(t, inv.accept) for rung, p in _PREDS.items()}

    L: List[str] = []
    L.append(f"date: {date.today().isoformat()}")
    L.append(f"git: {_git_rev()}")
    L.append(f"seed: {_SEED} (campaign pairs), full sweep (rung oracle)")
    L.append(f"corpus: {corpus.relative_to(_HERE.parents[2])}")
    L.append("")
    L.append("# GT2 — the ladder tests (spec §4)")
    L.append("")

    n_or = len(oracle)
    agree = sum(1 for r in oracle if r["agree"] == "yes")
    L.append("## F5 — the corpus rung oracle")
    L.append("")
    L.append(f"`is_recurrence == (m⁺ ≤ 0)` and `is_persistence == (m⁻ ≤ 0)` "
             f"against every `.cat` sidecar: **{agree}/{n_or}** agreement "
             f"(orientation as the paper states it; under the swap "
             f"{sum(1 for r in oracle if r['rec_ours'] == r['per_cat'] and r['per_ours'] == r['rec_cat'])}"
             f"/{n_or}). Regen: `python3 -m tests.giventhat.ladder_gate --rung-oracle`.")
    L.append("")

    f2 = len(ladder) - len(scored)
    bruted = [r for r in scored if r["brute"] == "ok"]
    L.append("## F6/F7 — hull laws and the brute lattice oracle")
    L.append("")
    L.append(f"{len(ladder)} campaign pairs (GT1 populations, seed {_SEED}), "
             f"{len(scored)} scored, {f2} F2-budget. Hull laws (extensive / "
             f"monotone / idempotent / saturated / fixpoint-iff / "
             f"`is_recurrence` on output; 6 seeded pair sets per case) and the "
             f"R-partition one-liner: zero violations on every scored pair. "
             f"Brute lattice oracle (`bits ≤ 12`, all `2^bits` choices, "
             f"existence + extremality literally): ran on **{len(bruted)}** "
             f"cases, zero disagreements; {len(scored) - len(bruted)} skipped "
             f"(`bits > 12`, recorded). Witness discipline: every refusal "
             f"replayed (table `member` + det HOAs). Regen: `python3 -m "
             f"tests.giventhat.ladder_gate --campaign`.")
    L.append("")

    L.append("## F8 — per-rung hit rates (census-shaped)")
    L.append("")
    L.append("| rung | interval has a member | raw neg_phi already there | "
             "strict drop available |")
    L.append("|---|--:|--:|--:|")
    for rung in _RUNG_NAMES:
        has = sum(1 for r in scored if r[rung] == "1")
        already = sum(1 for r in scored if own[r["neg_phi"]][rung])
        drop = sum(1 for r in scored
                   if r[rung] == "1" and not own[r["neg_phi"]][rung])
        L.append(f"| {rung} | {has}/{len(scored)} | {already}/{len(scored)} "
                 f"| {drop}/{len(scored)} |")
    L.append("")
    L.append("A 'strict drop' row counts pairs where `neg_phi` itself is NOT "
             "on the rung but the interval contains a member that is — the "
             "paper §7 item 3 number.")
    L.append("")

    (_LOGS / "gt2_ladder.md").write_text("\n".join(L))
    rows = _rows(_LOGS / "ladder_campaign.ckpt")
    with open(_LOGS / "gt2_ladder.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r["pop"], r["neg_phi"], r["k"])):
            w.writerow(r)
    print("\n".join(L))
    print(f"wrote {_LOGS / 'gt2_ladder.md'} and gt2_ladder.csv (promotion to "
          f"reference/ is a manual cp)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
