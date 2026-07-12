# M5 — the Markov product `Pr_M(L)`: the four gates

- date: 2026-07-12
- git: 115e8a7cf
- seed: 1 (random chains keyed by case name; oracle sample of 250)
- corpus: /home/ythierry/git/BuchiToLTL/genaut/corpus/flat_canon (6222 .sos files)
- regeneration (from `sosl/`): `python3 -m tests.quant.m5_gate --list | while read f; do timeout 15 python3 -m tests.quant.m5_gate "$f" >/dev/null; done; python3 -m tests.quant.m5_gate --sample | while read f; do timeout 15 python3 -m tests.quant.m5_gate --oracle "$f" >/dev/null; done; python3 -m tests.quant.m5_gate --aggregate`

**Laws.** Bernoulli embedding `sum_a p(a) . Pr_{M_a}(L) == mu_p(L)` (uniform and skewed p, the chain restarted at every letter state); complement flip `Pr_M(L) + Pr_M(~L) == 1` on a seeded random chain; `.mc` reader round-trip on every chain; Route A product-side oracle on the sample. All exact `Fraction`s.

| cases | green | red | missing |
|---|---|---|---|
| 6222 | 6222 | 0 | 0 |

| median product states | max | median ms | max ms |
|---|---|---|---|
| 17 | 178 | 4 | 1198 |

## Route A product-side oracle (sample)

| sampled | green | red | skip | missing |
|---|---|---|---|---|
| 250 | 250 | 0 | 0 | 0 |
