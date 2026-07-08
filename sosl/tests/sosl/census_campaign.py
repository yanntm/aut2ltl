"""Census-backed campaign: learn every language of one or more genaut shapes and
classify the outcome (E1 scaling data + E2 permanent-stall hunt).

    python3 -m tests.sosl.census_campaign [shape ...] [--config default|ablate|both]

Shapes name `genaut/corpus/det/<shape>/` folders (default: `2state1ap0acc`); the
precomputed `corpus/sos/<shape>/*.sos` files are the byte-equality references
(no per-case rebuild). `default` learns with saturation on (soundness + E1
metrics); `ablate` runs `--no-saturation --eq-mode exact` (E2: every surviving
stall is provably permanent). Results stream to `tests/sosl/logs/census/<run>/`.

Reports: verdict tally (any MISMATCH is a bug — spec §9 P2/P3), the E1 metric
rows, and every permanent specimen surfaced by the ablation leg — the first-class
E2 exhibits, reported individually.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List

from sosl.experiment.driver import run_matrix
from sosl.experiment.manifest import DEFAULT, NOSAT_EXACT, census_shapes
from sosl.experiment.run import Config

OUT = Path("tests/sosl/logs/census")
PER_CASE_BUDGET = 15


def _tally(results, config_id: str) -> dict:
    d: dict = {}
    for r in results:
        if r.stats.config_id != config_id:
            continue
        d[r.stats.verdict] = d.get(r.stats.verdict, 0) + 1
    return d


def main(argv: List[str]) -> int:
    config_sel = "both"
    shapes: List[str] = []
    skip = -1
    for i, a in enumerate(argv):
        if i == skip:
            continue
        if a == "--config":
            config_sel = argv[i + 1] if i + 1 < len(argv) else config_sel
            skip = i + 1
        elif not a.startswith("--"):
            shapes.append(a)
    if not shapes:
        shapes = ["2state1ap0acc"]

    cases = census_shapes(shapes=shapes)
    if not cases:
        print(f"no census cases for shapes={shapes} "
              f"(is genaut/corpus/det/ built?)", file=sys.stderr)
        return 2

    configs: List[Config] = []
    if config_sel in ("default", "both"):
        configs.append(Config(**{**DEFAULT.__dict__, "budget_seconds": PER_CASE_BUDGET}))
    if config_sel in ("ablate", "both"):
        configs.append(Config(**{**NOSAT_EXACT.__dict__, "budget_seconds": PER_CASE_BUDGET}))

    matrix = [(c, cfg) for cfg in configs for c in cases]
    out_dir = OUT / ("_".join(shapes)[:40])
    campaign = run_matrix(matrix, str(out_dir))

    print(f"shapes={shapes}  cases={len(cases)}  runs={len(campaign.results)}")
    for cfg in configs:
        print(f"  [{cfg.config_id}] {_tally(campaign.results, cfg.config_id)}")

    # Soundness: no MISMATCH anywhere (a census byte-mismatch is a real bug).
    mism = [r for r in campaign.results if r.stats.verdict == "MISMATCH"]
    if mism:
        print("\nMISMATCH (bug — investigate):")
        for r in mism[:20]:
            print(f"  {r.stats.case_id}/{r.stats.config_id}: {r.stats.detail}")

    # E2: permanent specimens from the ablation leg.
    perms = [r for r in campaign.results
             if r.stats.config_id == "no-sat-exact"
             and r.stats.stall_class == "permanent"]
    print(f"\npermanent specimens (ablation leg): {len(perms)}")
    for r in sorted(perms, key=lambda r: (r.stats.ref_classes, r.stats.case_id)):
        s = r.stats
        print(f"  {s.case_id}: ref={s.ref_classes} learned={s.learned_classes} "
              f"gap={s.ref_classes - s.learned_classes} cert={s.eq_certification}")

    print(f"\nartifacts: {campaign.csv_path}")
    return 1 if mism else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
