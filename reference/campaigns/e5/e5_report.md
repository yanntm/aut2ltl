# E5 — Counterexample sensitivity

Per case, the same run under increasing counterexample padding (`padded:<k>` pumps the minimal counterexample by k, same ω-word). `|cex|` is the max stem+loop length the teacher returned.

| case | policy | \|cex\| (stem/loop) | harvest | member | wall (s) | classes | verdict |
|---|---|---|--:|--:|--:|--:|---|
| a_once | minimal | 1/1 | 3 | 35 | 1.886 | 4 | SOUND |
| a_once | first | 1/1 | 3 | 35 | 1.898 | 4 | SOUND |
| a_once | padded:2 | 2/2 | 4 | 36 | 1.883 | 4 | SOUND |
| a_once | padded:4 | 4/4 | 5 | 37 | 1.884 | 4 | SOUND |
| a_once | padded:8 | 8/8 | 6 | 38 | 1.894 | 4 | SOUND |
| a_once | padded:16 | 16/16 | 7 | 39 | 1.900 | 4 | SOUND |
| a_once | padded:32 | 32/32 | 8 | 40 | 1.899 | 4 | SOUND |
| even | minimal | 0/3 | 4 | 51 | 1.934 | 5 | SOUND |
| even | first | 0/3 | 4 | 51 | 1.941 | 5 | SOUND |
| even | padded:2 | 3/6 | 5 | 52 | 1.948 | 5 | SOUND |
| even | padded:4 | 9/12 | 6 | 53 | 1.925 | 5 | SOUND |
| even | padded:8 | 21/24 | 7 | 54 | 1.926 | 5 | SOUND |
| even | padded:16 | 45/48 | 8 | 55 | 1.943 | 5 | SOUND |
| even | padded:32 | 93/96 | 9 | 56 | 1.941 | 5 | SOUND |
| evenblocks | minimal | 0/3 | 4 | 99 | 2.415 | 8 | SOUND |
| evenblocks | first | 0/3 | 4 | 99 | 2.404 | 8 | SOUND |
| evenblocks | padded:2 | 3/6 | 5 | 95 | 2.411 | 8 | SOUND |
| evenblocks | padded:4 | 9/12 | 6 | 96 | 2.457 | 8 | SOUND |
| evenblocks | padded:8 | 21/24 | 7 | 97 | 2.386 | 8 | SOUND |
| evenblocks | padded:16 | 45/48 | 8 | 98 | 2.416 | 8 | SOUND |
| evenblocks | padded:32 | 93/96 | 9 | 99 | 2.416 | 8 | SOUND |
| gf_aa_parity | minimal | 0/3 | 4 | 74 | 2.127 | 6 | SOUND |
| gf_aa_parity | first | 0/3 | 4 | 74 | 2.115 | 6 | SOUND |
| gf_aa_parity | padded:2 | 3/6 | 5 | 75 | 2.123 | 6 | SOUND |
| gf_aa_parity | padded:4 | 9/12 | 6 | 76 | 2.108 | 6 | SOUND |
| gf_aa_parity | padded:8 | 21/24 | 7 | 77 | 2.110 | 6 | SOUND |
| gf_aa_parity | padded:16 | 45/48 | 8 | 78 | 2.131 | 6 | SOUND |
| gf_aa_parity | padded:32 | 93/96 | 9 | 79 | 2.146 | 6 | SOUND |

Every padded run stays correct (same learned invariant as minimal); padding changes only the query cost, never the outcome. The harvest term grows far slower than |cex| — consistent with the logarithmic counterexample analysis.
