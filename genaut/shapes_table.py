"""genaut/shapes_table.py — regenerate SHAPES.md from the corpus census.md files.

Composes the full dedup **funnel** of every censused shape, one row per shape,
from the two census.md sources generation writes:

  corpus/tgba/<tag>/census.md      combos -> byte-distinct (md5) -> AP-canonical
                                   `kept` (gen/enumerate.py);
  corpus/spot_det/<tag>/census.md  kept -> **det-forms** (structural dedup of the
                                   deterministic D, gen/canonize.py);
  corpus/det/<tag>/census.md       det-forms -> **language-distinct** (the syntactic
                                   `𝓘` dedup, gen/canonize.py).

No arithmetic here beyond the collapse ratio — just read what each stage
recorded — and write the SHAPES.md feasible-shapes table sorted by N. A shape
whose `det/` tier is not built yet shows `—` in the language column.

  python3 genaut/shapes_table.py        # -> logs/genaut/corpus/SHAPES.md
"""
from __future__ import annotations

import glob
import os
import re
from typing import Dict, List, Optional

HERE = os.path.dirname(__file__)
_CORPUS = os.path.join(HERE, "corpus")
# A generated report is not source: it goes beside the corpus it summarizes,
# under the write root, never into genaut/ itself.
_OUT = os.path.normpath(os.path.join(HERE, os.pardir, "logs", "genaut", "corpus"))
DEFERRED_KEPT = 1000          # kept above this is heavy to survey -> flagged "deferred"

_FIELDS = {
    "nstates": r"nstates=(\d+)", "naps": r"naps=(\d+)", "nacc": r"nacc=(\d+)",
    "slots": r"slots:\s*(\d+)", "combos": r"combos \(generator-id space N\):\s*(\d+)",
    "byte": r"byte-distinct \(md5[^)]*\):\s*(\d+)",
    "polarity": r"polarity/name twins folded:\s*(\d+)",
    "kept": r"kept \(AP-canonical survivors\):\s*(\d+)",
}


def parse_census(path: str) -> Dict[str, int]:
    text = open(path).read()
    row: Dict[str, int] = {}
    for name, pat in _FIELDS.items():
        m = re.search(pat, text)
        if not m:
            raise ValueError(f"{path}: field {name!r} not found")
        row[name] = int(m.group(1))
    row["tag"] = os.path.basename(os.path.dirname(path))
    return row


def parse_languages(tag: str, corpus: str) -> Optional[int]:
    """The language-distinct count from `corpus/det/<tag>/census.md`, or `None`
    if the canonical tier is not built yet."""
    path = os.path.join(corpus, "det", tag, "census.md")
    if not os.path.isfile(path):
        return None
    m = re.search(r"distinct languages \(syntactic[^)]*\):\s*(\d+)", open(path).read())
    return int(m.group(1)) if m else None


def parse_det_forms(tag: str, corpus: str) -> Optional[int]:
    """The structural determinized-form count from
    `corpus/spot_det/<tag>/census.md`, or `None` if the tier is not built."""
    path = os.path.join(corpus, "spot_det", tag, "census.md")
    if not os.path.isfile(path):
        return None
    m = re.search(r"kept \(AP-canonical determinized forms\):\s*(\d+)",
                  open(path).read())
    return int(m.group(1)) if m else None


PROSE_HEAD = """# genaut shapes — the bestiary map

The shapes the census enumerates, and the tractability wall. A **shape** is
`Shape(n, k, c)` — `n` states, `k` atomic propositions, `c` acceptance sets (see
[`gen/algorithm.md`](gen/algorithm.md)). Each shape's generator-id space is

```
slots = n^2 * 2^c                      (one edge slot per (src, dst, markset))
N     = (2^(2^k)) ^ slots              (guards = all Boolean functions over k APs)
```

`N` is **doubly exponential in `k`**, exponential in `n^2` and `2^c`, so exhaustive
enumeration only reaches small shapes. Each row below is a one-off census written to
`corpus/<tag>/` with a `census.md`; **this table is generated from those census.md
files** (`python3 genaut/shapes_table.py`), not hand-kept.

## Feasible shapes (the dedup funnel, from corpus/*/census.md)

The columns trace one shape's collapse across the pipeline's dedup levels:
`combos` (generator-id space `N`) -> `byte-distinct` (md5 after Spot reduction) ->
`kept` (AP-canonical, the `tgba/` tier: distinct up to `a<->!a` polarity and AP
rename) -> `det-forms` (the `spot_det/` tier: distinct deterministic presentations
of the canonical automaton `D`, structural dedup) -> **`langs`** (the `det/` and
`sos/` tiers: distinct languages by the syntactic `𝓘` dedup). `collapse` is
`kept / langs` — how many relabel-distinct TGBA share one language. `survey`: the high-`kept` shapes (**deferred**) are heavy
and run separately. A `—` in `langs` means the canonical tier is not built yet
(`python3 genaut/gen/rebuild.py`).
"""

PROSE_TAIL = """
## Beyond the wall (first intractable)

| shape | N | why |
|---|---|---|
| `2state2ap1acc` | 16^8 ~ 4.3e9 | the true k=2 analog of 2state1ap1acc |
| `1state2ap3acc` | 16^8 ~ 4.3e9 | |
| `1state3ap2acc` | 256^4 ~ 4.3e9 | |
| `3state2ap0acc` | 16^9 ~ 6.9e10 | |
| `3state1ap1acc` | 4^18 ~ 6.9e10 | 3-state with both an AP and acceptance |

## Reading the numbers

- **`k >= 1` only.** 0-AP shapes are excluded: a one-letter alphabet has a single
  ω-word, so the only languages are `0` and `1` — no linguistic content to census.
- **`k` drives the polarity fold**: the relabel group is `2^k * k!`, so the fold grows
  fast with APs.
- **The LTL frontier is `n >= 2` AND `k >= 1`**: counting needs a multi-state cycle
  over a real alphabet (a non-aperiodic monoid). 1-state shapes stay all-LTL; not-LTL
  first appears at `2state1ap0acc`.
- **Generation is cheap; surveying is not** — running `aut2ltl` over a shape's `kept`
  automata scales with `kept`, so the high-`kept` shapes are surveyed separately.
"""


def main(argv: Optional[List[str]] = None) -> None:
    import argparse
    ap = argparse.ArgumentParser(prog="shapes_table")
    ap.add_argument("--corpus", default=_CORPUS, help="corpus root to READ")
    ap.add_argument("--out", default=_OUT, help="corpus root to WRITE SHAPES.md under")
    args = ap.parse_args(argv)
    corpus, out_root = args.corpus, args.out
    out_path = os.path.join(out_root, "SHAPES.md")
    os.makedirs(out_root, exist_ok=True)
    rows: List[Dict[str, int]] = [
        parse_census(p)
        for p in glob.glob(os.path.join(corpus, "tgba", "*", "census.md"))]
    rows.sort(key=lambda r: (r["combos"], r["tag"]))
    lines = ["| shape | n | k | c | slots | N (combos) | byte-distinct "
             "| **kept** | det-forms | **langs** | collapse | survey |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        survey = "deferred" if r["kept"] > DEFERRED_KEPT else ""
        langs = parse_languages(r["tag"], corpus)
        detforms = parse_det_forms(r["tag"], corpus)
        lang_cell = "—" if langs is None else f"**{langs}**"
        det_cell = "—" if detforms is None else str(detforms)
        collapse = "—" if not langs else f"{r['kept'] / langs:.2f}x"
        lines.append(
            f"| `{r['tag']}` | {r['nstates']} | {r['naps']} | {r['nacc']} "
            f"| {r['slots']} | {r['combos']} | {r['byte']} "
            f"| **{r['kept']}** | {det_cell} | {lang_cell} | {collapse} | {survey} |")
    with open(out_path, "w") as out:
        out.write(PROSE_HEAD + "\n" + "\n".join(lines) + "\n" + PROSE_TAIL)
    print(f"wrote {out_path} from {len(rows)} census.md files")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
