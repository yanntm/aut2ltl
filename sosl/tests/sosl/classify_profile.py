"""X1 — aggregate a census ledger into the per-language Wagner-degree profile.

    python3 -m tests.sosl.classify_profile <records.csv> [...] [--out DIR]

Reads the enriched ledger(s) written by `classify_census` and produces the spec
§5 rev.2 deliverables, all over **distinct languages** (dedup by `ihash`, the
canonical-`𝓘` key of [SωS26 Thm. 5.1]) with enumeration **abundance** — the
number of automata realizing each language — kept as a column:

  * the **bench manifest**: one row per (shape family × acceptance family) with
    raw automata, survivors, distinct languages, the automaton-to-language
    compression ratio, and the `N = |𝒞|` distribution (min / median / max);
  * the **degree profile**, distinct languages per Wagner degree `ϕ = (γ, s)`,
    ordered weakest-first with the trivial pair `(0,σ)/(0,π)` set apart, each
    row carrying its `(m±, n±)` coordinates and its abundance;
  * the same profile **ventilated per acceptance family** (C§11's effect made
    visible), and the aperiodic (LTL) split.

Two free correctness gates run while dedupling: within one `ihash` bucket every
record must carry the same `ϕ` and coordinates (a language invariant — a split
bucket convicts the classifier), and the spectrum-law verdict of the ledger is
surfaced. Writes `PROFILE.txt` under `--out` (default the first ledger's dir).
"""
from __future__ import annotations

import csv
import os
import statistics
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

from sosl.sos.classify.io import class_reading, degree_sort_key


def _coords(rec: Dict) -> Tuple[int, int, int, int]:
    """The four chain/superchain integers of a CSV row."""
    return (int(rec["m_plus"]), int(rec["m_minus"]),
            int(rec["n_plus"]), int(rec["n_minus"]))


class _Lang:
    """One distinct language: its degree, coordinates, algebra size, and the
    enumeration abundance / families that realized it."""

    def __init__(self, rec: Dict) -> None:
        self.phi: Tuple[str, str] = (rec["phi_gamma"], rec["phi_sign"])
        self.coords = _coords(rec)
        self.classes: int = int(rec["classes"])
        self.aperiodic: bool = rec["ltl"] == "yes"
        self.stutter: bool = rec["stutter"] == "invariant"
        self.abundance = 0
        self.shapes: Counter = Counter()
        self.families: Counter = Counter()

    def add(self, rec: Dict) -> Optional[str]:
        self.abundance += 1
        self.shapes[rec["shape_family"]] += 1
        self.families[rec["acceptance_family"]] += 1
        got = ((rec["phi_gamma"], rec["phi_sign"]), _coords(rec))
        if got != (self.phi, self.coords):
            return f"ihash split: {self.phi}/{self.coords} vs {got}"
        return None


def _load(paths: List[str]) -> List[Dict]:
    recs: List[Dict] = []
    for p in paths:
        with open(p, newline="") as fh:
            recs += list(csv.DictReader(fh))
    return recs


def _dedup(recs: List[Dict]) -> Tuple[Dict[str, _Lang], List[str]]:
    langs: Dict[str, _Lang] = {}
    splits: List[str] = []
    for r in recs:
        if r["verdict"] not in ("SOUND", "PARTIAL"):
            continue
        lang = langs.get(r["ihash"])
        if lang is None:
            lang = langs[r["ihash"]] = _Lang(r)
        err = lang.add(r)
        if err:
            splits.append(f"{r['ihash']}: {err}")
    return langs, splits


def _manifest(recs: List[Dict], langs: Dict[str, _Lang]) -> List[str]:
    """One row per shape family (the enumeration tag — `_parity` shapes are their
    own rows): raw automata / survivors / distinct languages / the
    automaton-to-language compression ratio / the `N = |𝒞|` distribution. The
    canonical-acceptance mix of each shape's languages is a trailing column — the
    per-automaton acceptance is read off the deterministic-complete form, not the
    tag, so a shape can carry several."""
    raw: Counter = Counter()
    surv: Counter = Counter()
    lang_by_shape: Dict[str, set] = defaultdict(set)
    for r in recs:
        shape = r["shape_family"]
        raw[shape] += 1
        if r["verdict"] in ("SOUND", "PARTIAL"):
            surv[shape] += 1
            lang_by_shape[shape].add(r["ihash"])

    rows = ["bench manifest — one row per shape family (enumeration tag)",
            f"{'shape':<24} {'raw':>6} {'surv':>6} {'langs':>6} {'ratio':>6}  "
            f"{'N(min/med/max)':<14}  canonical-acc mix (languages)",
            "-" * 96]
    for shape in sorted(raw):
        hashes = lang_by_shape[shape]
        nl = len(hashes)
        sizes = sorted(langs[h].classes for h in hashes) or [0]
        ratio = surv[shape] / nl if nl else 0.0
        accmix = Counter(af for h in hashes for af in langs[h].families)
        mix = " ".join(f"{a}:{n}" for a, n in accmix.most_common())
        rows.append(
            f"{shape:<24} {raw[shape]:>6} {surv[shape]:>6} {nl:>6} {ratio:>6.1f}  "
            f"{sizes[0]}/{int(statistics.median(sizes))}/{sizes[-1]:<10}  {mix}")
    return rows


_TRIVIAL = {("0", "sigma"), ("0", "pi")}


def _degree_table(langs: Dict[str, _Lang], subset=None, abund_of=None) -> List[str]:
    """Distinct-language degree profile, weakest-first, trivial pair set apart;
    abundance and coordinates per row. `subset`: a predicate on `_Lang`.
    `abund_of`: a `_Lang -> int` abundance (default the language's total; a
    per-family view passes the family's own count so the column stays local)."""
    if abund_of is None:
        abund_of = lambda l_: l_.abundance
    per_lang: Counter = Counter()
    abund: Counter = Counter()
    coords: Dict[Tuple[str, str], Tuple] = {}
    for lang in langs.values():
        if subset and not subset(lang):
            continue
        per_lang[lang.phi] += 1
        abund[lang.phi] += abund_of(lang)
        coords[lang.phi] = lang.coords
    if not per_lang:
        return ["  (none)"]

    def _fmt(phi: Tuple[str, str]) -> str:
        c = coords[phi]
        return (f"  ({phi[0]}, {phi[1]:<5}) {str(c):<18} "
                f"langs={per_lang[phi]:>5}  autos={abund[phi]:>6}  "
                f"{class_reading(phi)}")

    trivial = sorted((p for p in per_lang if p in _TRIVIAL), key=degree_sort_key)
    proper = sorted((p for p in per_lang if p not in _TRIVIAL), key=degree_sort_key)
    rows = [_fmt(p) for p in trivial]
    if trivial and proper:
        tl = sum(per_lang[p] for p in trivial)
        rows.append(f"  --- trivial pair (weakest), {tl} languages ---")
    rows += [_fmt(p) for p in proper]
    return rows


def run(argv: List[str]) -> int:
    paths, out = [], None
    it = iter(argv)
    for a in it:
        if a == "--out":
            out = next(it)
        else:
            paths.append(a)
    if not paths:
        print("usage: classify_profile <records.csv> [...] [--out DIR]",
              file=sys.stderr)
        return 1
    if out is None:
        out = os.path.dirname(os.path.abspath(paths[0]))

    recs = _load(paths)
    langs, splits = _dedup(recs)
    verdicts = Counter(r["verdict"] for r in recs)

    lines: List[str] = []
    lines.append(f"census profile — {len(recs)} automata, "
                 f"{len(langs)} distinct languages")
    lines.append(f"verdicts: {dict(verdicts)}")
    spectrum_viol = [r for r in recs if r.get("error") == "spectrum law"]
    lines.append(f"spectrum-law violations: {len(spectrum_viol)}   "
                 f"ihash splits (cross-abundance): {len(splits)}")
    lines.append("")
    lines += _manifest(recs, langs)
    lines.append("")

    lines.append("Wagner-degree profile — distinct languages, weakest-first")
    lines += _degree_table(langs)
    ltl = sum(1 for l in langs.values() if l.aperiodic)
    stutter = sum(1 for l in langs.values() if l.stutter)
    lines.append(f"  LTL-definable languages: {ltl} / {len(langs)}   "
                 f"non-LTL: {len(langs) - ltl}")
    lines.append(f"  stutter-invariant (X-free ⊆ LTL): {stutter} / {len(langs)}")
    lines.append("")

    fams = sorted({f for l_ in langs.values() for f in l_.families})
    for fam in fams:
        lines.append(f"— ventilation: acceptance family = {fam} —")
        lines += _degree_table(langs,
                               subset=lambda l_, f=fam: f in l_.families,
                               abund_of=lambda l_, f=fam: l_.families[f])
        lines.append("")

    text = "\n".join(lines)
    print(text)
    dest = os.path.join(out, "PROFILE.txt")
    with open(dest, "w") as fh:
        fh.write(text + "\n")
    print(f"[written {dest}]")
    return 0 if not splits and not spectrum_viol else 1


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
