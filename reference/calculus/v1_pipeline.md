# V1c — pipeline demo: normal-form economy + entry price

- date: 2026-07-10
- git: 979244e28
- seed: 20260712  |  20 same-alphabet pairs, middle |𝒞| decile
- corpus: /home/ythierry/git/BuchiToLTL/genaut/corpus/flat_canon

Pipeline `E1=¬A · E2=E1∩B · E3=¬E2 · E4=E3∪A`. Calculus times are surgery + `reduce(check=False)` (∩/∪ via `calculus.product`); Spot times are the op + `postprocess(Small)`. Medians over the pairs. Trap #14: deterministic corpus — this is the normal-form economy, not a Safra story.

| stage | median classes (calc) | calc ms | median states (Spot) | Spot ms |
|---|---|---|---|---|
| entry: build 𝓘(L) from D | — | 0.4253 | — | native |
| E1=¬A | 14 | 0.1106 | 5 | 0.0164 |
| E2=E1∩B | 32 | 0.9791 | 8 | 0.0308 |
| E3=¬E2 | 32 | 0.4431 | 10 | 0.0283 |
| E4=E3∪A | 32 | 0.9317 | 10 | 0.0369 |
| **cumulative** (entry + 4 stages) | — | **2.8899** | — | **0.1124** |

**Re-check economy.** Median per-stage "did my rewrite change the language" re-check: calculus 0.0001 ms (a byte compare of canonical `.sos` dumps) vs Spot 0.0039 ms (`equivalent_to`). The canonical normal form turns the query every pipeline runs into a string comparison.

**Entry price.** The calculus pays a one-time 0.4253 ms to build `𝓘(L)` from the deterministic D that Spot consumes natively; thereafter each surgery is a set operation on a held object and each re-check is free. Amortized over a four-stage pipeline the entry is a 15% share of the calculus total.

**Trap #14.** Every automaton here is deterministic and small, so no Safra determinization is forced and intermediate sizes stay modest on both sides; the demo isolates the normal-form / free-recheck economy, not the exponential entry the theory row reserves.
