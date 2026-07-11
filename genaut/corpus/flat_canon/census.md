# flat_canon — distinct languages up to AP relabeling, complement-closed

**6220** languages: **3212** distinct up to AP relabeling (the `B_k` orbit-min of `flat/`, folding the signed permutations of the atomic propositions — `GF(a) ≡ GF(!a)`, `a↔b` twins) plus **3008** complements added to close the catalogue under complement. Both the det HOA and the `.sos` are relabeled into the orbit's canonical labeling (σ* applied to both — a self-consistent pair); primals keep the smallest-shape `<tag>_<id>` name, each added dual is `<primal>_c`. σ* is chosen on the semigroup core alone, so `L` and `L̄` pick the same labeling (`𝓘(L̄)` = `𝓘(L)` with `accept` flipped, byte-exact) — the complement is the trivial P-flip, cross-checked against `dualize(det)`. No language is its own complement, so the closed count is even.

Excluded: `2state2ap0acc`.


## Composition (primals — the shape-realized languages)

| axis | bucket | languages |
|---|---|--:|
| acceptance family | `gba` | 1949 |
| acceptance family | `parity` | 1263 |
| provenance | exhaustive | 1764 |
| provenance | sampled | 1448 |
| acceptance colours | c=0 | 1393 |
| acceptance colours | c=1 | 930 |
| acceptance colours | c=2 | 884 |
| acceptance colours | c=3 | 5 |
| **primals** | | **3212** |
| complements added | | 3008 |
| **total (closed)** | | **6220** |

## Contribution by source (traversal order)

| # | source | n | k | c | family | tier | scanned | new | cumulative |
|--:|---|--:|--:|--:|---|---|--:|--:|--:|
| 1 | `1state1ap0acc` | 1 | 1 | 0 | gba | exhaustive | 3 | 3 | 3 |
| 2 | `1state1ap1acc` | 1 | 1 | 1 | gba | exhaustive | 4 | 1 | 4 |
| 3 | `1state1ap2acc` | 1 | 1 | 2 | gba | exhaustive | 5 | 1 | 5 |
| 4 | `1state1ap2acc_parity` | 1 | 1 | 2 | parity | exhaustive | 5 | 1 | 6 |
| 5 | `1state1ap3acc` | 1 | 1 | 3 | gba | exhaustive | 5 | 0 | 6 |
| 6 | `1state1ap3acc_parity` | 1 | 1 | 3 | parity | exhaustive | 6 | 0 | 6 |
| 7 | `1state2ap0acc` | 1 | 2 | 0 | gba | exhaustive | 6 | 4 | 10 |
| 8 | `1state2ap1acc` | 1 | 2 | 1 | gba | exhaustive | 22 | 10 | 20 |
| 9 | `1state2ap2acc` | 1 | 2 | 2 | gba | exhaustive | 66 | 21 | 41 |
| 10 | `1state2ap2acc_parity` | 1 | 2 | 2 | parity | exhaustive | 58 | 19 | 60 |
| 11 | `1state3ap0acc` | 1 | 3 | 0 | gba | exhaustive | 52 | 20 | 80 |
| 12 | `1state3ap1acc` | 1 | 3 | 1 | gba | exhaustive | 1480 | 225 | 305 |
| 13 | `2state1ap0acc` | 2 | 1 | 0 | gba | exhaustive | 25 | 21 | 326 |
| 14 | `2state1ap1acc` | 2 | 1 | 1 | gba | exhaustive | 129 | 93 | 419 |
| 15 | `3state1ap0acc` | 3 | 1 | 0 | gba | exhaustive | 1645 | 1345 | 1764 |
| 16 | `1state2ap3acc_parity__seedcurated` | 1 | 2 | 3 | parity | **sampled** | 5 | 5 | 1769 |
| 17 | `1state3ap2acc_parity__seedcurated` | 1 | 3 | 2 | parity | **sampled** | 8 | 8 | 1777 |
| 18 | `2state1ap2acc_parity__seed0` | 2 | 1 | 2 | parity | **sampled** | 591 | 243 | 2020 |
| 19 | `2state1ap2acc_parity__seedcurated` | 2 | 1 | 2 | parity | **sampled** | 3 | 3 | 2023 |
| 20 | `2state2ap1acc_parity__seedcurated` | 2 | 2 | 1 | parity | **sampled** | 57 | 57 | 2080 |
| 21 | `2state2ap2acc_parity__seedcurated` | 2 | 2 | 2 | parity | **sampled** | 325 | 325 | 2405 |
| 22 | `2state3ap1acc_parity__seedcurated` | 2 | 3 | 1 | parity | **sampled** | 156 | 156 | 2561 |
| 23 | `3state1ap1acc__seed0` | 3 | 1 | 1 | gba | **sampled** | 500 | 205 | 2766 |
| 24 | `3state1ap1acc_parity__seedcurated` | 3 | 1 | 1 | parity | **sampled** | 70 | 70 | 2836 |
| 25 | `3state1ap2acc_parity__seedcurated` | 3 | 1 | 2 | parity | **sampled** | 51 | 51 | 2887 |
| 26 | `3state2ap1acc_parity__seedcurated` | 3 | 2 | 1 | parity | **sampled** | 42 | 42 | 2929 |
| 27 | `3state2ap2acc_parity__seedcurated` | 3 | 2 | 2 | parity | **sampled** | 203 | 203 | 3132 |
| 28 | `4state1ap1acc_parity__seedcurated` | 4 | 1 | 1 | parity | **sampled** | 40 | 40 | 3172 |
| 29 | `4state1ap2acc_parity__seedcurated` | 4 | 1 | 2 | parity | **sampled** | 9 | 9 | 3181 |
| 30 | `4state2ap1acc_parity__seedcurated` | 4 | 2 | 1 | parity | **sampled** | 31 | 31 | 3212 |

Built by `python3 genaut/gen/flatten.py --canon`.
