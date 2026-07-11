# E1 — Scaling against the target

`N` = reference class count; `|Σ|` = 2^ap. Designed bounds: splits ≤ N; table (fill) membership ~ O(N²·|Σ|).

| case | N | \|Σ\| | init | splits | splits≤N | fill | N²·\|Σ\| | member | eq | wall (s) |
|---|--:|--:|--:|--:|:--:|--:|--:|--:|--:|--:|
| a_once | 4 | 2 | 2 | 2 | yes | 26 | 32 | 35 | 2 | 0.002 |
| a_implies_xa | 5 | 2 | 4 | 1 | yes | 32 | 50 | 43 | 1 | 0.002 |
| even | 5 | 2 | 3 | 2 | yes | 32 | 50 | 51 | 2 | 0.003 |
| gf_aa_parity | 6 | 2 | 3 | 3 | yes | 51 | 72 | 74 | 2 | 0.004 |
| gf_aa_reset | 6 | 2 | 3 | 3 | yes | 51 | 72 | 74 | 2 | 0.003 |
| evenblocks | 8 | 2 | 3 | 5 | yes | 67 | 128 | 99 | 2 | 0.004 |

**Splits ≤ N holds on every case: yes.** The table (fill) membership count stays under the N²·|Σ| envelope; harvest and saturation add the counterexample-analysis term.

Scatter plots vs N are deferred until the census tier supplies an N-spread (the named cases give N ∈ {4,5,6,8}); the generator already emits the per-metric columns the plots consume.
