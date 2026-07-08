"""E2 exhibits from the exhaustive census: characterize the permanent-stall
languages of a shape and render the sharpest as first-class exhibits.

    python3 -m tests.sosl.census_e2_exhibits [shape] [top_k]

Runs the shape (default 2state1ap1acc) under both `default` (canonical) and
`no-sat-exact` (the ablation leg — every surviving stall is provably permanent),
deduplicates the permanent specimens to distinct languages by their reference
`.sos`, tabulates the gap distribution, and renders the `top_k` sharpest
(largest reference-minus-stall gap) via the E2 exhibit renderer: coarse fixpoint,
canonical fixpoint, and the saturation escalations that separate them. Writes
`tests/sosl/logs/census_e2/<shape>.md`.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Tuple

from sosl.experiment.driver import run_matrix
from sosl.experiment.manifest import DEFAULT, NOSAT_EXACT, census_shapes
from sosl.experiment.report import _permanent_exhibit
from sosl.experiment.run import RunResult

OUT = Path("tests/sosl/logs/census_e2")


def main(argv: List[str]) -> int:
    shape = argv[0] if argv else "2state1ap1acc"
    top_k = int(argv[1]) if len(argv) > 1 else 6

    cases = census_shapes(shapes=[shape])
    if not cases:
        print(f"no census cases for {shape}", file=sys.stderr)
        return 2
    ref_of: Dict[str, str] = {c.case_id: c.sos for c in cases}

    matrix = ([(c, DEFAULT) for c in cases]
              + [(c, NOSAT_EXACT) for c in cases])
    campaign = run_matrix(matrix, str(OUT / f"{shape}_runs"))
    index: Dict[Tuple[str, str], RunResult] = {
        (r.stats.case_id, r.stats.config_id): r for r in campaign.results}

    # permanent specimens (ablation leg), deduplicated to distinct languages by
    # the reference .sos content — one representative (smallest id) per language.
    perms = [r for r in campaign.results
             if r.stats.config_id == "no-sat-exact"
             and r.stats.stall_class == "permanent"]
    by_lang: Dict[str, RunResult] = {}
    for r in sorted(perms, key=lambda r: r.stats.case_id):
        ref_path = ref_of.get(r.stats.case_id)
        lang = Path(ref_path).read_text() if ref_path else r.stats.case_id
        by_lang.setdefault(lang, r)
    distinct = list(by_lang.values())

    gaps: Dict[int, int] = {}
    for r in distinct:
        g = r.stats.ref_classes - r.stats.learned_classes
        gaps[g] = gaps.get(g, 0) + 1

    lines: List[str] = []
    lines.append(f"# E2 permanent-stall exhibits — {shape} (exhaustive)")
    lines.append("")
    lines.append(f"{len(perms)} permanent runs over the ablation leg dedup to "
                 f"**{len(distinct)} distinct languages** (by reference `.sos`).")
    lines.append("")
    lines.append("Gap (reference − stall) distribution over distinct languages:")
    lines.append("")
    lines.append("| gap | " + " | ".join(str(g) for g in sorted(gaps)) + " |")
    lines.append("|---|" + "--:|" * len(gaps))
    lines.append("| languages | " + " | ".join(str(gaps[g]) for g in sorted(gaps)) + " |")
    lines.append("")
    lines.append(f"## The {top_k} sharpest specimens")
    lines.append("")
    sharpest = sorted(distinct,
                      key=lambda r: (r.stats.learned_classes - r.stats.ref_classes,
                                     r.stats.case_id))[:top_k]
    for r in sharpest:
        lines.append(_permanent_exhibit(r.stats.case_id, index))

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{shape}.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"{shape}: {len(perms)} permanent runs -> {len(distinct)} distinct "
          f"languages; gaps {dict(sorted(gaps.items()))}")
    print(f"sharpest {top_k} rendered -> {OUT / (shape + '.md')}")
    for r in sharpest:
        s = r.stats
        print(f"  {s.case_id}: ref={s.ref_classes} stall={s.learned_classes} "
              f"gap={s.ref_classes - s.learned_classes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
