# survey/normalize — AP-normalisation + dedup

Canonicalise the atomic propositions of LTL formulas and HOA automata, and keep a
folder of them AP-canonical and irredundant. It is **orthogonal to sample
collection** — it does not generate a corpus; the dataset collectors under
`samples/` reuse it as a shared key. The folder tools report by default (dry run);
`--prune` is the explicit opt-in that writes.

Importable as a module path:

    from survey.normalize import normalize_ltl, polarity_normalize_ltl
    normalize_ltl("p & q")            # -> "a & b"
    polarity_normalize_ltl("!p & q")  # -> "p & q"

## Services

Two **normalisers** (pure, content-level — one touches names, the other signs, so
they compose freely):

- **`names.py`** — rename APs to `a, b, c…` in order of first occurrence, nothing
  else. `normalize_ltl` / `normalize_hoa` / `normalize_text` (content dispatch).
- **`polarity.py`** — complement each AP so its first literal occurrence is positive,
  nothing else (`!a X F a` and `a X F !a` both fold to `a X F !a`).
  `polarity_normalize_ltl` / `polarity_normalize_hoa` / `polarity_normalize_text`.

Two **folder tools** that walk a tree recursively and either report (dry run) or
`--prune` to write, both on the shared **`sweep`** engine:

- **`dedup.py`** — keep the first item per **pluggable** key (one item per HOA file,
  one per non-comment `.ltl` line), drop later duplicates. `default_key` is
  `polarity ∘ names`.
- **`canon.py`** — `dedup` **with renaming built in**: AP-rename every file to
  canonical form *and* drop duplicates in one recursive pass — the maximal normalize.

`sweep.py` is the engine: each folder tool supplies only its per-file `Op`; the
walk, the dry-run/`--prune` switch and the tally live in `sweep`, once — so `dedup`
and `canon` share one API.

## CLI

Isolated — print the canonical form of one formula / file:

    python3 -m survey.normalize.names    '<formula>' | file.hoa | file.ltl
    python3 -m survey.normalize.polarity '<formula>' | file.hoa | file.ltl

Whole folder — dry run, then add `--prune` to apply (from the repo root):

    python3 -m survey.normalize.dedup FOLDER     # drop duplicates
    python3 -m survey.normalize.canon FOLDER     # AP-rename + drop duplicates

## Test

    python3 -m survey.normalize.test_polarity   # OK / raises
    python3 -m survey.normalize.test_imports    # OK / raises

Run from the repo root (so `import survey.normalize` resolves).
