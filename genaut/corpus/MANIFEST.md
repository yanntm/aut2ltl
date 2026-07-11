# genaut bench manifest — the reduction funnel per shape × acceptance family

Parsed from the corpus census reports by `python3 genaut/manifest.py` (recomputes nothing — see the script's doc for the sources). `collapse` is `kept / langs`, the automaton→language compression the `𝓘` dedup achieves; `abundance` is how many enumerated automata realise one language (median / max); `N = |𝒞|` is the syntactic-algebra size spread over the shape's languages.

## Exhaustive census (small shapes, every language)

| shape | n | k | c | acc | combos | byte-distinct | kept | langs | collapse | abundance med/max | N min/med/max |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `1state1ap0acc` | 1 | 1 | 0 | gba | 4 | 4 | 3 | 3 | 1.00x | 1 / 1 | 2 / 2 / 3 |
| `1state1ap1acc` | 1 | 1 | 1 | gba | 16 | 7 | 5 | 4 | 1.25x | 1 / 2 | 2 / 2 / 3 |
| `1state1ap2acc` | 1 | 1 | 2 | gba | 256 | 9 | 6 | 5 | 1.20x | 1 / 2 | 2 / 3 / 4 |
| `1state1ap2acc_parity` | 1 | 1 | 2 | parity | 256 | 19 | 12 | 5 | 2.40x | 2 / 4 | 2 / 3 / 3 |
| `1state1ap3acc` | 1 | 1 | 3 | gba | 65536 | 9 | 6 | 5 | 1.20x | 1 / 2 | 2 / 3 / 4 |
| `1state1ap3acc_parity` | 1 | 1 | 3 | parity | 65536 | 39 | 23 | 6 | 3.83x | 2 / 10 | 2 / 3 / 3 |
| `1state2ap0acc` | 1 | 2 | 0 | gba | 16 | 16 | 6 | 6 | 1.00x | 1 / 1 | 2 / 3 / 3 |
| `1state2ap1acc` | 1 | 2 | 1 | gba | 256 | 77 | 24 | 22 | 1.09x | 1 / 2 | 2 / 3 / 4 |
| `1state2ap2acc` | 1 | 2 | 2 | gba | 65536 | 271 | 76 | 66 | 1.15x | 1 / 2 | 2 / 4 / 6 |
| `1state2ap2acc_parity` | 1 | 2 | 2 | parity | 65536 | 317 | 92 | 58 | 1.59x | 2 / 4 | 2 / 4 / 5 |
| `1state3ap0acc` | 1 | 3 | 0 | gba | 256 | 256 | 51 | 52 | 0.98x | 1 / 1 | 2 / 3 / 3 |
| `1state3ap1acc` | 1 | 3 | 1 | gba | 65536 | 6553 | 1243 | 1480 | 0.84x | 1 / 2 | 2 / 4 / 4 |
| `2state1ap0acc` | 2 | 1 | 0 | gba | 256 | 44 | 25 | 25 | 1.00x | 1 / 2 | 2 / 5 / 12 |
| `2state1ap1acc` | 2 | 1 | 1 | gba | 65536 | 1812 | 912 | 129 | 7.07x | 2 / 331 | 2 / 8 / 21 |
| `2state2ap0acc` | 2 | 2 | 0 | gba | 65536 | 29888 | 9401 | 11312 | 0.83x | 1 / 2 | 2 / 12 / 17 |
| `3state1ap0acc` | 3 | 1 | 0 | gba | 262144 | 5646 | 2970 | 1645 | 1.81x | 2 / 128 | 2 / 21 / 121 |

## Non-exhaustive samples (past the tractability wall)

A uniform random probe of the id space (rows with probe stats), or a curated selection adopted from a campaign (`seed` = `curated`, no probe stats) — never a complete census. `langs` is the live folder count.

| shape | seed | acc | id-space | draws | langs (live) | capped |
|---|---|---|---|---|---|---|
| `1state2ap3acc_parity` | curated | parity | — | — | 5 | — |
| `1state3ap2acc_parity` | curated | parity | — | — | 8 | — |
| `2state1ap2acc_parity` | 0 | parity | — | — | 591 | — |
| `2state1ap2acc_parity` | curated | parity | — | — | 3 | — |
| `2state2ap1acc_parity` | curated | parity | — | — | 57 | — |
| `2state2ap2acc_parity` | curated | parity | — | — | 325 | — |
| `2state3ap1acc_parity` | curated | parity | — | — | 156 | — |
| `3state1ap1acc` | 0 | gba | — | — | 500 | — |
| `3state1ap1acc_parity` | curated | parity | — | — | 70 | — |
| `3state1ap2acc_parity` | curated | parity | — | — | 52 | — |
| `3state2ap1acc_parity` | curated | parity | — | — | 42 | — |
| `3state2ap2acc_parity` | curated | parity | — | — | 203 | — |
| `4state1ap1acc_parity` | curated | parity | — | — | 40 | — |
| `4state1ap2acc_parity` | curated | parity | — | — | 9 | — |
| `4state2ap1acc_parity` | curated | parity | — | — | 31 | — |
