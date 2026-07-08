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

import spot

from sosl.experiment.driver import run_matrix
from sosl.experiment.manifest import DEFAULT, NOSAT_EXACT, census_shapes
from sosl.experiment.report import _permanent_exhibit
from sosl.experiment.run import RunResult
from sosl.sos.build import reference_of_hoa
from sosl.sos.invariant import Invariant

OUT = Path("tests/sosl/logs/census_e2")


def _prefix_independent(inv: Invariant) -> bool:
    """Is L prefix-independent? Exactly: acceptance of every linked pair ``(s, e)``
    is invariant under left-multiplication ``s -> c·s`` (prepending any word maps
    ``s`` into its left ideal, and ``c·s`` stays ``e``-stable), so membership does
    not depend on the stem."""
    acc = inv.accept
    for (s, e) in inv.linked_pairs():
        bit = (s, e) in acc
        for c in range(inv.n):
            if (((inv.mult[c][s], e) in acc)) != bit:
                return False
    return True


def _acc_type(hoa_path: str) -> str:
    """The acceptance shape of the canonical D: buchi / co-buchi / parity /
    trivial / other (read off the automaton's acceptance condition via Spot)."""
    acc = spot.automaton(hoa_path).acc()
    if acc.is_t() or acc.is_f():
        return "trivial"
    if acc.is_buchi():
        return "buchi"
    if acc.is_co_buchi():
        return "co-buchi"
    if acc.is_parity()[0]:
        return "parity"
    return "other"


def main(argv: List[str]) -> int:
    shape = argv[0] if argv else "2state1ap1acc"
    top_k = int(argv[1]) if len(argv) > 1 else 6

    cases = census_shapes(shapes=[shape])
    if not cases:
        print(f"no census cases for {shape}", file=sys.stderr)
        return 2
    ref_of: Dict[str, str] = {c.case_id: c.sos for c in cases}
    hoa_of: Dict[str, str] = {c.case_id: c.hoa for c in cases}

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

    # Structural cross-tabulation (theory §6.3 ask): the 44 permanent languages
    # by prefix-independence x acceptance type, and by gap x prefix-independence.
    feats = []
    for r in distinct:
        inv = reference_of_hoa(hoa_of[r.stats.case_id])
        feats.append((_prefix_independent(inv), _acc_type(hoa_of[r.stats.case_id]),
                      r.stats.ref_classes - r.stats.learned_classes))
    acc_types = sorted({at for _pi, at, _g in feats})
    lines.append("Structural features of the permanent languages "
                 "(prefix-independence × acceptance type):")
    lines.append("")
    lines.append("| prefix-indep | " + " | ".join(acc_types) + " | total |")
    lines.append("|---|" + "--:|" * (len(acc_types) + 1))
    for pi in (True, False):
        row = [sum(1 for p, at, _g in feats if p == pi and at == t)
               for t in acc_types]
        lines.append(f"| {'yes' if pi else 'no'} | "
                     + " | ".join(str(x) for x in row)
                     + f" | {sum(row)} |")
    tot = [sum(1 for _p, at, _g in feats if at == t) for t in acc_types]
    lines.append("| **total** | " + " | ".join(f"**{x}**" for x in tot)
                 + f" | **{len(feats)}** |")
    lines.append("")
    lines.append("Gap × prefix-independence:")
    lines.append("")
    lines.append("| prefix-indep | " + " | ".join(f"gap {g}" for g in sorted(gaps))
                 + " |")
    lines.append("|---|" + "--:|" * len(gaps))
    for pi in (True, False):
        row = [sum(1 for p, _at, g in feats if p == pi and g == gg)
               for gg in sorted(gaps)]
        lines.append(f"| {'yes' if pi else 'no'} | "
                     + " | ".join(str(x) for x in row) + " |")
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

    pi_count = sum(1 for p, _at, _g in feats if p)
    at_counts = {t: sum(1 for _p, at, _g in feats if at == t) for t in acc_types}
    print(f"{shape}: {len(perms)} permanent runs -> {len(distinct)} distinct "
          f"languages; gaps {dict(sorted(gaps.items()))}")
    print(f"  structural: prefix-independent {pi_count}/{len(feats)}; "
          f"acceptance {at_counts}")
    print(f"sharpest {top_k} rendered -> {OUT / (shape + '.md')}")
    for r in sharpest:
        s = r.stats
        print(f"  {s.case_id}: ref={s.ref_classes} stall={s.learned_classes} "
              f"gap={s.ref_classes - s.learned_classes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
