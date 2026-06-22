# samples/benchmark — portfolio evaluation bench

A **bench, not a gate**. Where `samples/validation` checks the curated 40-formula
corpus stays sound, this measures *output size* of one portfolio against another
(first target: `default` vs `best`) over a large, growing, structured input set —
to see where `best` wins/loses at scale before promoting it to the default.

It is run with the **survey** harness (it has no runner of its own):

    aut2ltl_survey --folder samples/benchmark --use default --use best --logs logs

survey routes HOA vs LTL by content, applies a strict per-input budget, and emits
one flat CSV per run with a per-technique summary. Compare two runs with
`python3 -m survey.diff.results A.csv B.csv` (keys on the input column; reports
key-set overlap and DAG/tree/equiv movement on the common fragment). Committed
reference runs live in `results/reference/benchmark/`.

## Inputs (`inputs/`, raw files — no python)

Category subfolders, each `.ltl` (one formula per line, `#` comments) or `.hoa`
(one automaton); see `inputs/README.md`. Generators live *outside* `inputs/` and
emit committed files into it:

- **`inputs/core/`** — the curated 40-formula corpus, one `.ltl` per Manna–Pnueli
  class. Benchmark's seed; the same 40 are the standalone gate at
  `samples/validation/` (a committed static copy — no generator).
- **`inputs/chains/`** — scalable W/U/R chains with optional `X`-lacing and W-U/U-R
  mixes, over non-trivial arms (`patterns.py --emit`).
- **`inputs/kinska/`** — Büchi automata (HOA), flattened + deduped from
  `samples/kinska` (`collect_kinska.py`), AP-renamed; many are not LTL-definable.
- **`inputs/fixtures/`** — fixture formulas adopted from `samples/fixtures`
  (committed static; the dev fixtures are already clean `.ltl`).

## Tools

- **`patterns.py`** — chain-family generator (`--emit DIR`).
- **`collect_kinska.py`** — adopt + dedup Kinská HOA from `samples/kinska` into
  `inputs/kinska/`, AP-renamed.

Both use the shared **`survey.normalize`** utility (its own
[README](../../survey/normalize/README.md)) for AP **name**/**polarity**
canonicalisation and folder `dedup`; they apply the name rename on store. Run them
from the repo root (with `pip install -e .`).

## Extending the corpus

The corpus is kept **hierarchical, AP-canonical and irredundant**. To add inputs:

1. **Add a category subfolder** under `inputs/` (nest if useful).
2. **Add a `README.md`** for it — what the category is, and its provenance.
3. **Populate** it with `.ltl` (one formula per line, `#` comments) and/or `.hoa`
   (one automaton) files.
4. **Normalize, then dedup.** Canonicalise the new files' APs so the corpus stays
   uniform, then drop redundancy under that key — always **dry run first**, then
   `--prune` to apply. From the repo root:

       python3 -m survey.normalize.names FILE          # print the AP-canonical form of one file
       python3 -m survey.normalize.dedup        inputs # dry run: per-file drop counts, nothing written
       python3 -m survey.normalize.dedup --prune inputs # apply: delete dup .hoa / strip dup .ltl lines

   `dedup` keys on the canonical form (names then polarity), so it catches
   name/polarity variants too — run it after **any** addition to `inputs/`.

