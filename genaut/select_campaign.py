"""Curate a bounded, reproducible enrichment from a sampling campaign's new
languages, for adoption into the corpus.

A beyond-the-wall sampling campaign yields far more new languages than the bench
should absorb (tens of thousands), skewed to the largest shapes. This selects a
target-size subset (default 1000) by a **deterministic, seed-independent**
procedure — so the *criteria* reproduce even though the draws do not — favouring
the Wagner-degree frontier and minimal, category-representative examples.

Input: a `flat_canon/` built from corpus+campaign (`flatten --canon` into a
scratch `--out`) and the tracked `corpus/flat_canon/`. A **new primal** is a
canonical `.sos` (complement `_c` excluded — duals are added on closure, not
selected) whose bytes are not already tracked. Each carries: origin shape, Wagner
degree `phi`, LTL class, automaton states `s`, algebra size `|C|`.

Selection (documented in `genaut/README.md`, "Curating a campaign"):

  Minimality order (total, no seed): `(states, |C|, canonical .sos bytes)`.

  Tier A — the frontier, take all. Every new language whose degree is rare or
  absent in the pre-campaign corpus: ordinal `gamma in {omega*2, omega^3,
  omega^4, ...}` or finite `gamma >= 3`. (`omega`, `omega^2` and the shallow
  finite levels are common; they are sampled in Tier B, not taken wholesale.)

  Tier B — minimal representatives, to reach the target. Stratify the rest by
  `(shape, phi, LTL-class)`; visit strata in priority order — smaller shape
  (`n*k*2^c`) first, then higher degree, then non-LTL before LTL — and round-robin,
  each visit taking the next language in minimality order from that stratum
  (subject to a per-shape Tier-B cap), until the total reaches the target. Round-
  robin guarantees every stratum is represented before any is deepened, so rare
  (shape, degree) combinations survive.

Writes the selected det+`.sos` under `<out>/sampled/<shape>__seed<label>/` (grouped
by origin shape), ready to drop into `corpus/sampled/` and fold with
`flatten --canon`.

Run: ``python3 genaut/select_campaign.py [--measure DIR] [--corpus DIR]
        [--target N] [--tierb-cap N] [--out DIR] [--label S] [--dry-run]``
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import shutil
from collections import defaultdict
from typing import Dict, List, NamedTuple, Optional, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, os.pardir))
_TAG_RE = re.compile(r"^(\d+)state(\d+)ap(\d+)acc(_parity)?_[0-9]+$")

# Ordinal degree rank, for "higher degree first" in Tier B and for the frontier
# test. Finite gamma keeps its integer; the transfinite levels sort above them.
_ORD = {"omega": 1000, "omega*2": 2000, "omega^2": 1_000_000,
        "omega^3": 2_000_000, "omega^4": 3_000_000, "omega^5": 4_000_000}


class Lang(NamedTuple):
    tag: str
    base: str
    n: int
    k: int
    c: int
    states: int
    algebra: int
    phi: str
    ltl: str
    sos_bytes: str


def _gamma(phi: str) -> str:
    return phi.split(",", 1)[0]


def _ord_rank(phi: str) -> int:
    g = _gamma(phi)
    return int(g) if g.isdigit() else _ORD.get(g, 5_000_000)


def is_frontier(phi: str) -> bool:
    """Rare/absent-in-corpus degrees, taken in full: the deep ordinals
    (`omega*2`, `omega^3`, `omega^4`, ...) and the deep finite levels
    (`gamma >= 3`). `omega`, `omega^2` and shallow finite levels are excluded —
    they are common and sampled in Tier B."""
    g = _gamma(phi)
    if g.isdigit():
        return int(g) >= 3
    return g in ("omega*2", "omega^3", "omega^4", "omega^5")


def _read_cat(path: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if os.path.isfile(path):
        for line in open(path):
            if ":" in line:
                key, val = line.split(":", 1)
                out[key.strip()] = val.strip()
    return out


def _states(hoa_path: str) -> int:
    for line in open(hoa_path):
        if line.startswith("States:"):
            return int(line.split(":", 1)[1])
    return 0


def _algebra(sos_text: str) -> int:
    for line in sos_text.splitlines():
        if line.startswith("classes:"):
            return int(line.split(":", 1)[1])
    return 0


def load_new(measure: str, corpus: str) -> List[Lang]:
    """Every new primal in `measure/flat_canon` (canonical `.sos` not in the
    tracked `corpus/flat_canon`, complements excluded), with its attributes."""
    tracked = {open(f).read()
               for f in glob.glob(os.path.join(corpus, "sos", "*.sos"))}
    out: List[Lang] = []
    for f in sorted(glob.glob(os.path.join(measure, "sos", "*.sos"))):
        base = os.path.basename(f)[:-4]
        m = _TAG_RE.match(base)
        if not m:
            continue
        text = open(f).read()
        if text in tracked:
            continue
        cat = _read_cat(os.path.join(measure, "sos", base + ".cat"))
        n, k, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
        tag = base.rsplit("_", 1)[0]
        out.append(Lang(
            tag=tag, base=base, n=n, k=k, c=c,
            states=_states(os.path.join(measure, "det", base + ".hoa")),
            algebra=_algebra(text), phi=cat.get("phi", "?"),
            ltl=cat.get("ltl", "?"), sos_bytes=text))
    return out


def select(langs: List[Lang], target: int, tierb_cap: int) -> Tuple[List[Lang], List[Lang]]:
    """Apply Tier A (frontier, all) then Tier B (minimal-representative round-robin)
    to reach `target`. Returns (tierA, tierB)."""
    def minkey(x: Lang) -> Tuple[int, int, str]:
        return (x.states, x.algebra, x.sos_bytes)

    tier_a = sorted((x for x in langs if is_frontier(x.phi)), key=minkey)

    # Tier B strata: (shape, phi, ltl), each a queue in minimality order.
    strata: Dict[Tuple[str, str, str], List[Lang]] = defaultdict(list)
    for x in langs:
        if not is_frontier(x.phi):
            strata[(x.tag, x.phi, x.ltl)].append(x)
    for key in strata:
        strata[key].sort(key=minkey)

    # Priority: smaller shape (n*k*2^c), then higher degree, then non-LTL first.
    def strata_prio(key: Tuple[str, str, str]) -> Tuple[int, int, int, str]:
        tag, phi, ltl = key
        x = strata[key][0]
        return (x.n * x.k * (1 << x.c), -_ord_rank(phi), 0 if ltl == "no" else 1, phi)

    order = sorted(strata, key=strata_prio)
    per_shape: Dict[str, int] = defaultdict(int)
    tier_b: List[Lang] = []
    cursor: Dict[Tuple[str, str, str], int] = defaultdict(int)
    need = target - len(tier_a)
    progressed = True
    while len(tier_b) < need and progressed:
        progressed = False
        for key in order:
            if len(tier_b) >= need:
                break
            i = cursor[key]
            if i >= len(strata[key]):
                continue
            x = strata[key][i]
            if per_shape[x.tag] >= tierb_cap:
                continue
            cursor[key] = i + 1
            tier_b.append(x)
            per_shape[x.tag] += 1
            progressed = True
    return tier_a, tier_b


def _write(selected: List[Lang], measure: str, out: str, label: str) -> None:
    for x in selected:
        dst = os.path.join(out, "sampled", f"{x.tag}__seed{label}")
        for tier in ("det", "sos"):
            os.makedirs(os.path.join(dst, tier), exist_ok=True)
        shutil.copy(os.path.join(measure, "det", x.base + ".hoa"),
                    os.path.join(dst, "det", x.base + ".hoa"))
        shutil.copy(os.path.join(measure, "sos", x.base + ".sos"),
                    os.path.join(dst, "sos", x.base + ".sos"))


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="select_campaign")
    ap.add_argument("--measure", default=os.path.join(
        _REPO, "logs", "genaut", "measure3", "flat_canon"))
    ap.add_argument("--corpus", default=os.path.join(
        _REPO, "genaut", "corpus", "flat_canon"))
    ap.add_argument("--target", type=int, default=1000)
    ap.add_argument("--tierb-cap", type=int, default=80)
    ap.add_argument("--out", default=os.path.join(_REPO, "logs", "genaut", "selected"))
    ap.add_argument("--label", default="curated")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    langs = load_new(args.measure, args.corpus)
    tier_a, tier_b = select(langs, args.target, args.tierb_cap)
    chosen = tier_a + tier_b
    print(f"new primals in pool: {len(langs)}")
    print(f"Tier A (frontier, all): {len(tier_a)}")
    print(f"Tier B (minimal fill):  {len(tier_b)}")
    print(f"selected total:         {len(chosen)}\n")

    by_shape: Dict[str, int] = defaultdict(int)
    by_phi: Dict[str, int] = defaultdict(int)
    for x in chosen:
        by_shape[x.tag] += 1
        by_phi[x.phi] += 1
    print("by origin shape:")
    for tag in sorted(by_shape, key=lambda t: -by_shape[t]):
        print(f"  {tag:26} {by_shape[tag]:5d}")
    print("\nby Wagner degree:")
    for phi in sorted(by_phi, key=lambda p: -_ord_rank(p)):
        mark = "  <- frontier" if is_frontier(phi) else ""
        print(f"  {phi:16} {by_phi[phi]:5d}{mark}")

    if not args.dry_run:
        shutil.rmtree(os.path.join(args.out, "sampled"), ignore_errors=True)
        _write(chosen, args.measure, args.out, args.label)
        print(f"\nwrote {len(chosen)} languages to {args.out}/sampled/"
              f"<shape>__seed{args.label}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
