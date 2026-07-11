date: 2026-07-11
git: 0137f6a63
seed: 20260711 (campaign pairs), full sweep (rung oracle)
corpus: genaut/corpus/flat_canon

# GT2 — the ladder tests (spec §4)

## F5 — the corpus rung oracle

`is_recurrence == (m⁺ ≤ 0)` and `is_persistence == (m⁻ ≤ 0)` against every `.cat` sidecar: **6222/6222** agreement (orientation as the paper states it; under the swap 4914/6222). Regen: `python3 -m tests.giventhat.ladder_gate --rung-oracle`.

## F6/F7 — hull laws and the brute lattice oracle

700 campaign pairs (GT1 populations, seed 20260711), 700 scored, 0 F2-budget. Hull laws (extensive / monotone / idempotent / saturated / fixpoint-iff / `is_recurrence` on output; 6 seeded pair sets per case) and the R-partition one-liner: zero violations on every scored pair. Brute lattice oracle (`bits ≤ 12`, all `2^bits` choices, existence + extremality literally): ran on **264** cases, zero disagreements; 436 skipped (`bits > 12`, recorded). Witness discipline: every refusal replayed (table `member` + det HOAs). Regen: `python3 -m tests.giventhat.ladder_gate --campaign`.

## F8 — per-rung hit rates (census-shaped)

| rung | interval has a member | raw neg_phi already there | strict drop available |
|---|--:|--:|--:|
| safety | 318/700 | 169/700 | 149/700 |
| cosafety | 321/700 | 164/700 | 157/700 |
| obligation | 453/700 | 347/700 | 106/700 |
| recurrence | 516/700 | 424/700 | 92/700 |
| persistence | 529/700 | 429/700 | 100/700 |

A 'strict drop' row counts pairs where `neg_phi` itself is NOT on the rung but the interval contains a member that is — the paper §7 item 3 number.
