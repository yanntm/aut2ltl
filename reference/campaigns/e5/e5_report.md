# E5 — Counterexample sensitivity

Per case, the same run under increasing counterexample padding (`padded:<k>` pumps the minimal counterexample by k, same ω-word). `|cex|` is the max stem+loop length the teacher returned.

| case | policy | \|cex\| (stem/loop) | harvest | member | wall (s) | classes | verdict |
|---|---|---|--:|--:|--:|--:|---|
| a_once | minimal | 1/1 | 1 | 10 | 0.001 | 4 | SOUND |
| a_once | first | 1/1 | 1 | 10 | 0.001 | 4 | SOUND |
| a_once | padded:2 | 2/2 | 1 | 10 | 0.001 | 4 | SOUND |
| a_once | padded:4 | 4/4 | 1 | 10 | 0.001 | 4 | SOUND |
| a_once | padded:8 | 8/8 | 1 | 10 | 0.001 | 4 | SOUND |
| a_once | padded:16 | 16/16 | 1 | 10 | 0.001 | 4 | SOUND |
| a_once | padded:32 | 32/32 | 1 | 10 | 0.001 | 4 | SOUND |
| even | minimal | 0/3 | 4 | 25 | 0.001 | 5 | SOUND |
| even | first | 0/3 | 4 | 25 | 0.001 | 5 | SOUND |
| even | padded:2 | 3/6 | 4 | 25 | 0.001 | 5 | SOUND |
| even | padded:4 | 9/12 | 4 | 25 | 0.001 | 5 | SOUND |
| even | padded:8 | 21/24 | 4 | 25 | 0.001 | 5 | SOUND |
| even | padded:16 | 45/48 | 4 | 25 | 0.001 | 5 | SOUND |
| even | padded:32 | 93/96 | 4 | 25 | 0.002 | 5 | SOUND |
| evenblocks | minimal | 0/3 | 3 | 44 | 0.001 | 8 | SOUND |
| evenblocks | first | 0/3 | 3 | 44 | 0.001 | 8 | SOUND |
| evenblocks | padded:2 | 3/6 | 5 | 47 | 0.001 | 8 | SOUND |
| evenblocks | padded:4 | 9/12 | 6 | 48 | 0.001 | 8 | SOUND |
| evenblocks | padded:8 | 21/24 | 7 | 49 | 0.001 | 8 | SOUND |
| evenblocks | padded:16 | 45/48 | 8 | 50 | 0.002 | 8 | SOUND |
| evenblocks | padded:32 | 93/96 | 9 | 51 | 0.002 | 8 | SOUND |
| gf_aa_parity | minimal | 0/3 | 3 | 31 | 0.002 | 6 | SOUND |
| gf_aa_parity | first | 0/3 | 3 | 31 | 0.001 | 6 | SOUND |
| gf_aa_parity | padded:2 | 3/6 | 4 | 31 | 0.001 | 6 | SOUND |
| gf_aa_parity | padded:4 | 9/12 | 5 | 32 | 0.001 | 6 | SOUND |
| gf_aa_parity | padded:8 | 21/24 | 6 | 33 | 0.001 | 6 | SOUND |
| gf_aa_parity | padded:16 | 45/48 | 7 | 34 | 0.001 | 6 | SOUND |
| gf_aa_parity | padded:32 | 93/96 | 8 | 35 | 0.001 | 6 | SOUND |

Every padded run stays correct (same learned invariant as minimal); padding changes only the query cost, never the outcome. The harvest term grows far slower than |cex| — consistent with the logarithmic counterexample analysis.
