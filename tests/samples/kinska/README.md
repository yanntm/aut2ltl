# Benchmark samples — Kinská

Benchmark Büchi automata (HOA format) and their source LTL formulae, adopted as
test inputs for our automata→LTL construction.

## Provenance

- **Source:** <https://gitlab.fi.muni.cz/xkinska/master-thesis-implementation>
  (commit `1a1b45d`, 2025-05-20)
- **Author:** Tereza Kinská
- **Thesis:** *Detection of LTL-Definability in Büchi Automata*, Master's thesis,
  Faculty of Informatics, Masaryk University (FI MUNI), Brno, Spring 2025.
- **Tool:** `ba2ltlDecider`

Quoted from the source repository's README:

> This tool was created as a part of masters thesis at FI MUNI. It was created
> with an aim to make it a part of the Spot library.

## License

The source repository carries a GNU GPLv3 / AGPLv3 license (its README states GNU
GPL v3 "the same as the license of Spot"; its `LICENSE` file is the GNU Affero
GPL v3). Both are compatible with this project's GPLv3 license. Copyright (c)
2025 Tereza Kinská.

## Layout

Mirrors the upstream `experiments_data/` directory:

- `counting/{1ap,2ap}/` — counting Büchi automata.
- `randltl/{1,2,4,8}ap-ba/` — random-LTL Büchi automata, with the source formula
  lists in the sibling `*-formulae/` directories.

## Our results on this corpus (2026-06-15, preliminary)

Run with the default portfolio at a strict 15s/run, verified by Spot
`are_equivalent` (the survey's VERIFY oracle); `NOT_LTL` is our own aperiodicity
gate declining the language as not LTL-definable. Regenerate with
`tests/kinska_sweep.sh`; ventilate by folder with `tests/kinska_breakdown.py`.
Full detail (per-input formula, sizes, verdict) is in
**`logs/reference/kinska.csv`** + `SUMMARY.txt`.

| folder                | cases | validated | NOT_LTL | timeout | unverified-size |
|-----------------------|------:|----------:|--------:|--------:|----------------:|
| counting/1ap          |    40 |     **4** |      15 |      10 |              11 |
| counting/2ap          |    45 |     **4** |      28 |      13 |               0 |
| randltl/{1,2,4,8}ap-ba       (×4) |    40 |        40 |       0 |       0 |               0 |
| randltl/{1,2,4,8}ap-formulae (×4) |    40 |        40 |       0 |       0 |               0 |
| **TOTAL**             |   165 |        88 |      43 |      23 |              11 |

- **randltl** (BA + source formulae, all AP counts): 80/80 reconstructed and
  Spot-validated equivalent. No surprises — these are LTL by construction.
- **counting** (the set understood to be the *non*-LTL-definable challenge): we
  produced **8 Spot-validated LTL formulae** (4 in 1ap, 4 in 2ap) for automata in
  this set, i.e. languages our construction reconstructs AND Spot confirms
  equivalent. Our aperiodicity gate independently declined 43 as `NOT_LTL`.

### This is NOT yet a claim that the benchmark is mislabelled

It is a flag to investigate, not a conclusion. Before asserting anything about
the corpus we must strengthen the study:

- **34 of 85 counting cases are inconclusive** — 23 hit the 15s build budget and
  11 produced a sound but too-large DAG (`UNVERIFIED_SIZE`). Neither is an LTL
  verdict; raise the budget / handle size before counting them either way.
- **Confirm the 8 "validated" cases end-to-end**: that the HOA we import is
  exactly Kinská's intended automaton (import preserves the language) and that
  her decider's verdict on those specific inputs is indeed "not LTL-definable" —
  check against the thesis tool's own expected-verdict output, not our reading.
- **Cross-check our `NOT_LTL` gate** (43 declines) against the upstream decider
  case by case; agreement there is the evidence that our LTL/non-LTL split is
  trustworthy enough to call the 8 a genuine discrepancy.

### Their thesis setup (comparison pending — not done here)

Per the thesis (Chapter 5–6), important asymmetries to respect before any
head-to-head:

- Their tool `ba2ltlDecider` **decides** LTL-definability (aperiodicity); it does
  **not** translate. So their analogue to our work is only our `NOT_LTL` gate,
  not the formulae we build.
- The counting set (85) is the **intended-non-LTL** dataset; their best (the
  word-generating algorithm) **confirmed 51 as non-LTL and timed out on 34**.
  The randltl/formulae set (40) is the **intended-LTL** one; their lazy-matrix
  variant solved 35, timed out on 5.
- Budgets differ by orders of magnitude: **theirs 600s / 30 GB**, ours **15s**.
  Our 23 counting build-timeouts are at 15s and say nothing at their budget.

A like-for-like comparison (our aperiodicity gate vs their decider, per instance,
and whether our 8 validated cases fall in their confirmed-51 or timed-out-34) is
left for a dedicated follow-up.
