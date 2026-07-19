# corpus — the language tier of the benchmark inputs

One canonical automaton and one syntactic ω-semigroup **per distinct ω-language**
realized by `samples/benchmark/inputs/`. Where the benchmark is a corpus of
*presentations* — LTL formulas and HOA automata, many denoting the same language —
this is the corpus of the **languages themselves**: shape-insensitive, irredundant,
and closed under complement.

    corpus/det/    the deterministic, complete, transition-based, generic
                   automaton D (`sosl … importer.canonical`) as HOA — one per
                   distinct language.
    corpus/sos/    the syntactic ω-semigroup 𝓘(L) as `.sos` — one per distinct
                   language; the compact canonical form downstream runs (e.g. the
                   classifier) consume directly, with no presentation to reduce.
    corpus/census.md + corpus.json    the presentation → language funnel.

`det/` and `sos/` are 1:1 and share basenames. This is structurally
`genaut/corpus/flat/` (see [`genaut/README.md`](../genaut/README.md)), over a
different source: genaut's flat pool folds an *exhaustive small-shape census*,
this folds the *hand-curated benchmark*.

## Why it sits here and not under `samples/`

It is **derived** — regenerable from `samples/benchmark/inputs/`, which is the
hand-curated source of truth — and the survey harness recurses whatever folder it
is handed. A `det/` of 460 HOA files under `samples/benchmark/` would silently
join the bench's own input set and move its committed results
(`results/reference/benchmark/`). Keeping the tier a sibling of `samples/` keeps
`aut2ltl_survey --folder samples/benchmark` meaning what it has always meant.

## Dedup notion

**Language identity up to a fixed AP labeling**: the `.sos` `𝓘` key — by
[SωS26 Thm. 5.1] two dumps are byte-equal iff the languages are equal. Two
consequences, both deliberate:

- `GF(a)` and `GF(!a)` are **two entries**. Folding relabel/polarity twins is the
  stronger `B_k` orbit fold that `genaut/corpus/flat_canon/` performs; it is not
  done here.
- A language over `{a}` and the same language over `{a,b}` are **two entries** — a
  different alphabet is a different canonical `D`, hence a different `.sos`. (No
  `remove_unused_ap` pass runs, matching `flat/`.)

## Complement closure

The catalogue is closed under complement. For every language whose dual is not
itself catalogued, `<primal>_c` is added: the `.sos` by `Invariant.complement()`
(the free flip of `P` against the linked pairs — `I(L)` and `I(L̄)` share their
algebra, the syntactic congruence being complement-invariant), and the `det/` HOA
by `spot.dualize`. The two are **cross-checked** against each other on every dual;
a disagreement raises rather than silently preferring one. No language equals its
own complement, so the closed catalogue is even.

## Naming

A language is named for the **first input that realized it**, so the name traces it
back to its source:

    core_recurrence_L07    line 7 of samples/benchmark/inputs/core/recurrence.ltl
    kinska_counting-1ap-counting_buchi_1ap_03   that HOA file
    core_safety_L04_c      the complement of core_safety_L04 (an added dual)

## What is *not* here, and why

Some benchmark inputs denote languages with genuinely enormous syntactic algebras —
the tails of the Kinská `counting-*` families, whose semigroup grows with the
counter modulus. Three budgets bound the build; an input that trips one is
**recorded as skipped in `census.md`, never dropped silently**:

| budget | default | what it rejects |
|---|--:|---|
| `--cap` | `20000` | an `|EM1|` closure larger than this |
| `--timeout` | `15` s | an input that outruns its per-input wall clock |
| `--max-sos` | `1 MiB` | a language whose `.sos` dump is too big to commit |

The size cap is the reason the corpus is a few MB rather than ~46 MB: the largest
surviving counting automaton dumps a **19 MiB** `.sos`, which has no place in a test
set. It is discarded **by policy, not missing** — every skipped language is a real
one, and all of them are rebuildable:

    python3 corpus/canonize.py --max-sos 0 --cap 0 --timeout 0   # admit everything

`--max-sos` gates a language **and its dual together**: they share an algebra and
their dumps differ only in the `P` block, so admitting one without the other would
leave the catalogue not complement-closed.

## Rebuilding

    python3 corpus/canonize.py                  # (re)build det/ + sos/ + census
    python3 corpus/canonize.py --timeout 30     # per-input wall clock (0 disables)
    python3 corpus/canonize.py --no-complement  # primals only

Every input is carried `spot.translate`/`spot.automaton` → `importer.canonical` →
`invariant_of`. Skipping is a limit of the build's budget, not a failure of the
construction.

The structural claims are asserted independently of the build's own bookkeeping by

    python3 -m tests.corpus.check_corpus        # paired, irredundant, closed, coherent
