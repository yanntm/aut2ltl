# date: 2026-07-11
# git-rev: 87d8cdc5f
# seed: 20260711
# corpus: genaut/corpus/flat_canon/sos

# SY3 relations census summary

- cases: **6222** (by AP count: {'0': 2, '1': 4006, '2': 1438, '3': 776})
- corpus `.cat` stutter tag: {'invariant': 896, 'sensitive': 5326} — `stutter_inv` (stutter_rung(1)) count here: **896** (must equal the `invariant` tag — F8 cross-check)

## F9 — invisible letters (`[c] = 1`)

- cases with a nonempty invisible-letter set: **0** / 6222 (0%)
- structurally absent on this corpus, paralleling `inert_aps` (F3): an invisible letter is a *class* equality `[c]=1`, an inert AP a *fiber* equality — distinct read-offs, both empty here on the alphabet-minimal, canonized corpus.

## F10 — the tolerated independence relation `Î_L`

- density (fraction of ordered distinct class pairs with `[cd]=[dc]`): min 0.0000, mean 0.1923, max 1.0000
- fully rigid (`Î_L = ∅`, no tolerated commuting): **4318** (69.3989%); fully commutative (density 1): **744** (11.9576%); partial: **1160**
- mean density stratified by AP count (the load-bearing view):

| n | cases | mean Î_L density |
|---|---|---|
| 0 | 2 | 0.0000 |
| 1 | 4006 | 0.0140 |
| 2 | 1438 | 0.3767 |
| 3 | 776 | 0.7714 |

## F11 — the k-block ladder entry

- `ladder_entry` = least rung `k ≤ 3` with `stutter_rung(k)` (`[v]=[vv]` for all length-`k` class-words), `None` if none:

| ladder_entry | cases |
|---|---|
| 1 | 896 |
| 2 | 736 |
| 3 | 326 |
| None | 4264 |

- `ladder_entry == 1` count (**896**) equals the stutter-invariant count (rung 1 is stutter); rungs 2–3 add **1062** cases that are block-stutter at a deeper level but not letter-stutter — the non-nested spread the parameter measures.

- ladder entry stratified by AP count:

| n | cases | 1 | 2 | 3 | None |
|---|---|---|---|---|---|
| 0 | 2 | 2 | 0 | 0 | 0 |
| 1 | 4006 | 82 | 594 | 326 | 3004 |
| 2 | 1438 | 298 | 132 | 0 | 1008 |
| 3 | 776 | 514 | 10 | 0 | 252 |
