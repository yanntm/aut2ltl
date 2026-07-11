date: 2026-07-11
git: 0aef7ebac
seed: full sweep (no sampling)
corpus: genaut/corpus/flat_canon

# V4 — the classification battery vs Spot

6222 languages, 6222 scored. Ours: the `surgery` scans on the held invariant (warm, median of 7). Spot's: the automaton-level route on the paired deterministic HOA — `is_safety_automaton`, the same on `dualize`, and `minimize_wdba` + equivalence (Spot's Manna-Pnueli classifiers themselves are formula-level and do not apply to an automaton-only input).

## Census — the Manna-Pnueli rungs of `flat_canon`

| rung | languages | share |
|---|--:|--:|
| B — safety ∧ co-safety (bottom) | 84 | 1.4% |
| S — safety only | 1430 | 23.0% |
| G — co-safety only (guarantee) | 1430 | 23.0% |
| O — obligation, neither | 238 | 3.8% |
| above the obligation rung | 3040 | 48.9% |
| **total** | **6222** | |

Obligation languages: **3182/6222 = 51.1%**.

A consistency check the census must pass: co-safety is safety of the complement and the corpus is complement-closed, so the S and G counts have to match — S = 1430, G = 1430 (they do; a strict subset of the corpus need not be complement-closed, so this only binds a full sweep).

## Agreement with Spot, per read-off

| read-off | agree | disagree | ours true | Spot true |
|---|--:|--:|--:|--:|
| `is_safety` | 6222 | 0 | 1514 | 1514 |
| `is_cosafety` | 6222 | 0 | 1514 | 1514 |
| `is_obligation` | 6222 | 0 | 3182 | 3182 |

Full-triple agreement: **6222/6222 = 100.00%** (perfect).

`obligation_degree` has no Spot counterpart — Spot decides the obligation rung but does not measure the Wagner superchain coordinates. The column is ours-only.

## Obligation degree — the histogram (ours-only)

| degree (n⁺, n⁻) | languages | rungs |
|---|--:|---|
| (-1, 0) | 1 | B |
| (0, -1) | 1 | B |
| (0, 0) | 82 | B |
| (0, 1) | 1430 | G |
| (1, 0) | 1430 | S |
| (1, 1) | 18 | O |
| (1, 2) | 68 | O |
| (2, 1) | 68 | O |
| (2, 3) | 40 | O |
| (3, 2) | 40 | O |
| (3, 4) | 2 | O |
| (4, 3) | 2 | O |

A second consistency check, free from the same sweep: complement swaps the two polarities of the superchain, so on a complement-closed corpus the histogram must be symmetric under `(n⁺, n⁻) ↦ (n⁻, n⁺)` — it is, on every entry.

## Head-to-head timings (ms, median of 7 per case, then the median over cases)

| read-off | ours | Spot | Spot / ours |
|---|--:|--:|--:|
| safety | 0.0029 | 0.0007 | 0.25× |
| co-safety | 0.0029 | 0.0017 | 0.59× |
| obligation | 0.0027 | 0.0061 | 2.27× |
| degree | 0.0265 | — | — |

Ours are warm scans of a held object; Spot's are calls on a deterministic automaton it has already parsed (the parse is outside the timer on both sides). Python against C++ — the ratio is corroboration of the asymptotics, not a benchmark claim: the scans are linear in the table, while `dualize` and `minimize_wdba` + equivalence build and compare automata.

## Disagreement dossier

None — the algebraic read-offs and Spot's automaton-level oracle agree on every scored language, on all three verdicts.
