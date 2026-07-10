# V1b — operation costs, calculus vs Spot

- date: 2026-07-10
- git: 4478ba943
- sample: first 1000 uniform pairs of V1a (1550 distinct languages for the unary rows)
- corpus: /home/ythierry/git/BuchiToLTL/genaut/corpus/flat_canon

**Headline.** Over the 3938-language flat_canon census the generated product is affordable — median uniform alignment ratio 0.174 of the `n_A·n_B` rectangle (V1a) — and held-object operations are microsecond-scale: a containment decision runs in 0.0083 ms once the product is aligned (V1b). The stutter read-off agrees with Spot on 3938/3938 languages (V2).

Held-object economy (§8.4): inputs are deterministic, so Spot complement is `dualize`; the NBA-complementation theory row stands on [TFVT10], not these timings. Per-op times are WARM (median of 7); `align` is COLD and excluded from per-op rows. Counts are the argument, times corroborate.

| operation | calc median ms | Spot median ms | median nodes | median cells | median linked | F2 |
|---|---|---|---|---|---|---|
| complement | 0.1751 | 0.0008 | 19 | — | 51 | 0 |
| membership | 0.0002 | 0.0014 | 19 | — | 51 | 0 |
| inclusion | 0.0083 | 0.0029 | 68 | 4624 | 139 | 0 |
| equivalence | 0.0072 | 0.0031 | 68 | 4624 | 139 | 0 |
| intersect_word | 0.0083 | 0.0043 | 68 | 4624 | 139 | 0 |
| intersect_obj | 2.4160 | 0.0018 | 68 | 4624 | 304 | 0 |

`intersect_obj` calc is the canonical `reduce` (a normal form); its Spot column is raw `spot.product`. A SEPARATE `product + postprocess(Small)` simplification (a heuristic, NOT compared to `reduce` as a ratio — trap #12) has median 0.0332 ms.

Align-amortized `inclusion` cost `(align_cold + k·op)/k` — the cold `align` is a shared entry price, paid once per held product then spread over the k decisions run on it:

| k | ms/decision |  (align_cold 0.0696 ms, op 0.0083 ms) |
|---|---|---|
| 1 | 0.0779 | |
| 5 | 0.0222 | |
| 10 | 0.0153 | |

