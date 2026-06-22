# samples/benchmark/inputs — the benchmark corpus

Raw inputs for the portfolio bench, classified by **category subfolder**
(`core/`, `chains/`, `kinska/`, `fixtures/` — add freely, nest if useful). The
survey harness walks this tree (`aut2ltl_survey --folder samples/benchmark`) and
feeds every input to `python3 -m aut2ltl`.

## File formats (no python here)

- **`.ltl`** — LTL formulas, **one per line**. `#` starts a comment to end-of-line;
  blank lines are ignored. (Trailing `# id` tags are fine.)
- **`.hoa`** — one ω-automaton in HOA format (routed by content, so the extension
  is only for discovery).
- **`.md`** — documentation; ignored by discovery.

survey strips `#`/blank lines and detects HOA by content, so no special handling
is needed — drop files in and they are picked up.

## Provenance

Some categories are **generated** (committed for reproducibility) by a generator
*outside* this tree: `chains/` from `patterns.py --emit`, `kinska/` adopted from
`samples/kinska` via `collect_kinska.py`. Others are committed static sets:
`core/` (the 40, also the gate at `samples/validation`) and `fixtures/` (adopted
from `samples/fixtures`). Generated files say so in their header comment — do not
hand-edit those.

Every emitted example is stored in **AP-canonical form** (`survey.normalize`: APs
renamed to `a,b,c…`, nothing else simplified/reordered) — the same key used for
dedup, applied to the stored content so the corpus is uniform.
