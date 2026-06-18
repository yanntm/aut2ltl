# tests/benchmark/inputs — the benchmark corpus

Raw inputs for the portfolio bench, classified by **category subfolder**
(`chains/`, `reactive/`, `counter/`, … — add freely, nest if useful). The sweep
walks this tree and feeds every input to `tests/survey.py`.

## File formats (no python here)

- **`.ltl`** — LTL formulas, **one per line**. `#` starts a comment to end-of-line;
  blank lines are ignored. (Trailing `# id` tags are fine — stripped by the sweep.)
- **`.hoa`** — one ω-automaton in HOA format (fed whole to `--hoa`; routed by content,
  so the extension is only for discovery).
- **`.md`** — documentation; **ignored by the sweep.**

`survey.py` already strips `#`/blank lines and detects HOA by content, so no special
handling is needed — drop files in and they are picked up.

## Provenance

Some categories are **generated** (committed for reproducibility) by a generator that
lives *outside* this tree (e.g. `chains/` from `tests/benchmark/patterns.py --emit`,
`fixtures/` from `collect_fixtures.py`); others are hand-written or collected (HOA we
have, Kinská models). Generated files say so in their header comment — do not hand-edit
those.

Every emitted example is stored in **AP-canonical form** (`normalize.py`: APs renamed
to `a,b,c…`, nothing else simplified/reordered) — the same key used for dedup, applied
to the stored content so the corpus is uniform.

## Status: collection phase

Inputs are gathered indiscriminately for now. Dedup (syntactic, via AP-canonicalisation)
and a curated, classified representative set come in the curation phase — see
`../README.md`.
