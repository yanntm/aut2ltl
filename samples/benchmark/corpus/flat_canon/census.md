# flat_canon — distinct languages up to AP relabeling, complement-closed

**372** languages: **211** distinct up to AP relabeling (the `B_k` orbit-min of `flat/`, folding the signed permutations of the atomic propositions — `GF(a) ≡ GF(!a)`, `a↔b` twins) plus **161** complements added to close the catalogue under complement. Both the det HOA and the `.sos` are relabeled into the orbit's canonical labeling (σ* applied to both — a self-consistent pair); primals keep the smallest-shape `<tag>_<id>` name, each added dual is `<primal>_c`. σ* is chosen on the semigroup core alone, so `L` and `L̄` pick the same labeling (`𝓘(L̄)` = `𝓘(L)` with `accept` flipped, byte-exact) — the complement is the trivial P-flip, cross-checked against `dualize(det)`. No language is its own complement, so the closed count is even.


## Composition (primals — the shape-realized languages)

| axis | bucket | languages |
|---|---|--:|
| acceptance family | `gba` | 211 |
| provenance | exhaustive | 0 |
| provenance | sampled | 211 |
| acceptance colours | c=1000000 | 211 |
| **primals** | | **211** |
| complements added | | 161 |
| **total (closed)** | | **372** |

## Contribution by source (traversal order)

| # | source | n | k | c | family | tier | scanned | new | cumulative |
|--:|---|--:|--:|--:|---|---|--:|--:|--:|
| 1 | `benchmark` | 1000000 | 1000000 | 1000000 | gba | **sampled** | 241 | 211 | 211 |

Built by `python3 genaut/gen/flatten.py --canon`.
