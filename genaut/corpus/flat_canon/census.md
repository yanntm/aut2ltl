# flat_canon — distinct languages up to AP relabeling, complement-closed

**3938** languages: **2007** distinct up to AP relabeling (the `B_k` orbit-min of `flat/`, folding the signed permutations of the atomic propositions — `GF(a) ≡ GF(!a)`, `a↔b` twins) plus **1931** complements added to close the catalogue under complement. Both the det HOA and the `.sos` are relabeled into the orbit's canonical labeling (σ* applied to both — a self-consistent pair); primals keep the smallest-shape `<tag>_<id>` name, each added dual is `<primal>_c`. σ* is chosen on the semigroup core alone, so `L` and `L̄` pick the same labeling (`𝓘(L̄)` = `𝓘(L)` with `accept` flipped, byte-exact) — the complement is the trivial P-flip, cross-checked against `dualize(det)`. No language is its own complement, so the closed count is even.

Excluded: `2state2ap0acc`.


## Composition (primals — the shape-realized languages)

| axis | bucket | languages |
|---|---|--:|
| acceptance family | `gba` | 1744 |
| acceptance family | `parity` | 263 |
| provenance | exhaustive | 1764 |
| provenance | sampled | 243 |
| acceptance colours | c=0 | 1393 |
| acceptance colours | c=1 | 329 |
| acceptance colours | c=2 | 285 |
| acceptance colours | c=3 | 0 |
| **primals** | | **2007** |
| complements added | | 1931 |
| **total (closed)** | | **3938** |

## Contribution by source (traversal order)

| # | source | n | k | c | family | tier | scanned | new | cumulative |
|--:|---|--:|--:|--:|---|---|--:|--:|--:|
| 1 | `1state1ap0acc` | 1 | 1 | 0 | gba | exhaustive | 3 | 3 | 3 |
| 2 | `1state1ap1acc` | 1 | 1 | 1 | gba | exhaustive | 4 | 1 | 4 |
| 3 | `1state1ap1acc_parity` | 1 | 1 | 1 | parity | exhaustive | 4 | 0 | 4 |
| 4 | `1state1ap2acc` | 1 | 1 | 2 | gba | exhaustive | 5 | 1 | 5 |
| 5 | `1state1ap2acc_parity` | 1 | 1 | 2 | parity | exhaustive | 5 | 1 | 6 |
| 6 | `1state1ap3acc` | 1 | 1 | 3 | gba | exhaustive | 5 | 0 | 6 |
| 7 | `1state1ap3acc_parity` | 1 | 1 | 3 | parity | exhaustive | 6 | 0 | 6 |
| 8 | `1state2ap0acc` | 1 | 2 | 0 | gba | exhaustive | 6 | 4 | 10 |
| 9 | `1state2ap1acc` | 1 | 2 | 1 | gba | exhaustive | 22 | 10 | 20 |
| 10 | `1state2ap1acc_parity` | 1 | 2 | 1 | parity | exhaustive | 22 | 0 | 20 |
| 11 | `1state2ap2acc` | 1 | 2 | 2 | gba | exhaustive | 66 | 21 | 41 |
| 12 | `1state2ap2acc_parity` | 1 | 2 | 2 | parity | exhaustive | 58 | 19 | 60 |
| 13 | `1state3ap0acc` | 1 | 3 | 0 | gba | exhaustive | 52 | 20 | 80 |
| 14 | `1state3ap1acc` | 1 | 3 | 1 | gba | exhaustive | 1480 | 225 | 305 |
| 15 | `2state1ap0acc` | 2 | 1 | 0 | gba | exhaustive | 25 | 21 | 326 |
| 16 | `2state1ap1acc` | 2 | 1 | 1 | gba | exhaustive | 129 | 93 | 419 |
| 17 | `2state1ap1acc_parity` | 2 | 1 | 1 | parity | exhaustive | 129 | 0 | 419 |
| 18 | `3state1ap0acc` | 3 | 1 | 0 | gba | exhaustive | 1645 | 1345 | 1764 |
| 19 | `2state1ap2acc_parity__seed0` | 2 | 1 | 2 | parity | **sampled** | 591 | 243 | 2007 |

Built by `python3 genaut/gen/flatten.py --canon`.
