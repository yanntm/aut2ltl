"""Profile the languages a sampling campaign adds over the tracked corpus.

Reads a `flat_canon/` built from corpus+campaign (`flatten --canon` into a scratch
`--out`) and the tracked `corpus/flat_canon/`, and reports — for the **primals new
to the corpus** (canonical `.sos` bytes not already tracked; complements `_c`
excluded, they are derived duals) — the pool a selection draws from:

  * per origin shape: how many new, and the canonical automaton size (HOA
    `States:`) and algebra size (`.sos classes:`) min/median/max;
  * the Wagner-degree profile (from each `.cat` sidecar), overall and per shape;
  * the LTL / stutter-invariant split.

The point: pick minimal, high-degree, category-representative languages rather than
whatever the sampler drew first. Pure file reads, no construction.

Run: ``python3 genaut/tests/campaign_profile.py [MEASURE_FLATCANON] [CORPUS_FLATCANON]``
  defaults: logs/genaut/measure3/flat_canon  and  genaut/corpus/flat_canon
"""
from __future__ import annotations

import glob
import os
import re
import statistics
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, os.pardir, os.pardir))

_TAG_RE = re.compile(r"^(\d+state\d+ap\d+acc(?:_parity)?)_[0-9]+$")


def _origin_tag(basename: str) -> Optional[str]:
    """The shape tag of a primal `.sos` basename (`<tag>_<id>`); `None` for a
    complement (`<...>_c`) or an unrecognized name."""
    m = _TAG_RE.match(basename)
    return m.group(1) if m else None


def _read_cat(path: str) -> Dict[str, str]:
    """The `key: value` lines of a `.cat` sidecar as a dict (empty if absent)."""
    out: Dict[str, str] = {}
    if os.path.isfile(path):
        for line in open(path):
            if ":" in line:
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip()
    return out


def _states(hoa_path: str) -> Optional[int]:
    """The `States:` count declared in a HOA file, or `None`."""
    if not os.path.isfile(hoa_path):
        return None
    for line in open(hoa_path):
        if line.startswith("States:"):
            return int(line.split(":", 1)[1])
    return None


def _algebra_size(sos_text: str) -> Optional[int]:
    """The `classes: N` count of a `.sos` dump."""
    for line in sos_text.splitlines():
        if line.startswith("classes:"):
            return int(line.split(":", 1)[1])
    return None


def main(argv: List[str]) -> int:
    measure = argv[0] if len(argv) > 0 else os.path.join(
        _REPO, "logs", "genaut", "measure3", "flat_canon")
    corpus = argv[1] if len(argv) > 1 else os.path.join(
        _REPO, "genaut", "corpus", "flat_canon")

    tracked = {open(f).read() for f in glob.glob(os.path.join(corpus, "sos", "*.sos"))}
    print(f"tracked corpus primals+complements: {len(tracked)} .sos")

    # New primals: canonical .sos not already tracked, complement files excluded.
    per_shape_states: Dict[str, List[int]] = defaultdict(list)
    per_shape_algebra: Dict[str, List[int]] = defaultdict(list)
    per_shape_phi: Dict[str, Counter] = defaultdict(Counter)
    phi_all: Counter = Counter()
    ltl_all: Counter = Counter()
    stutter_all: Counter = Counter()
    n_new = 0

    for f in glob.glob(os.path.join(measure, "sos", "*.sos")):
        base = os.path.basename(f)[:-4]
        tag = _origin_tag(base)
        if tag is None:
            continue                       # complement or non-shape name
        text = open(f).read()
        if text in tracked:
            continue                       # already in the corpus
        n_new += 1
        cat = _read_cat(os.path.join(measure, "sos", base + ".cat"))
        phi = cat.get("phi", "?")
        phi_all[phi] += 1
        per_shape_phi[tag][phi] += 1
        ltl_all[cat.get("ltl", "?")] += 1
        stutter_all[cat.get("stutter", "?")] += 1
        st = _states(os.path.join(measure, "det", base + ".hoa"))
        if st is not None:
            per_shape_states[tag].append(st)
        alg = _algebra_size(text)
        if alg is not None:
            per_shape_algebra[tag].append(alg)

    def span(xs: List[int]) -> str:
        return f"{min(xs)}/{int(statistics.median(xs))}/{max(xs)}" if xs else "-"

    print(f"\nNEW primals over the tracked corpus: {n_new}\n")
    print(f"{'shape':26}{'new':>6}{'states m/md/M':>16}{'algebra m/md/M':>16}")
    for tag in sorted(per_shape_phi, key=lambda t: -len(_flatten(per_shape_phi[t]))):
        cnt = sum(per_shape_phi[tag].values())
        print(f"{tag:26}{cnt:6d}{span(per_shape_states[tag]):>16}"
              f"{span(per_shape_algebra[tag]):>16}")

    print("\nWagner-degree profile of the new primals (phi -> count):")
    for phi, c in sorted(phi_all.items(), key=lambda kv: -kv[1]):
        print(f"  {phi:20} {c:6d}")
    print(f"\nLTL: {dict(ltl_all)}")
    print(f"stutter: {dict(stutter_all)}")

    print("\nPer-shape Wagner degrees (shape: phi=count ...):")
    for tag in sorted(per_shape_phi):
        parts = " ".join(f"{p}={c}" for p, c in sorted(per_shape_phi[tag].items()))
        print(f"  {tag:26} {parts}")
    return 0


def _flatten(counter: Counter) -> List:
    return list(counter.elements())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
