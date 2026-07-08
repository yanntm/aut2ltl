# genaut bench manifest — the reduction funnel per shape × acceptance family

Parsed from the corpus census reports by `python3 genaut/manifest.py` (recomputes nothing — see the script's doc for the sources). `collapse` is `kept / langs`, the automaton→language compression the `𝓘` dedup achieves; `abundance` is how many enumerated automata realise one language (median / max); `N = |𝒞|` is the syntactic-algebra size spread over the shape's languages.

## Exhaustive census (small shapes, every language)

| shape | n | k | c | acc | combos | byte-distinct | kept | langs | collapse | abundance med/max | N min/med/max |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `1state1ap0acc` | 1 | 1 | 0 | gba | 4 | 4 | 3 | 3 | 1.00x | 1 / 1 | 2 / 2 / 3 |
| `1state1ap1acc` | 1 | 1 | 1 | gba | 16 | 7 | 5 | 4 | 1.25x | 1 / 2 | 2 / 2 / 3 |
| `1state1ap1acc_parity` | 1 | 1 | 1 | parity | 16 | 7 | 5 | 4 | 1.25x | 1 / 2 | 2 / 2 / 3 |
| `1state1ap2acc` | 1 | 1 | 2 | gba | 256 | 10 | 7 | 5 | 1.40x | 1 / 2 | 2 / 3 / 4 |
| `1state1ap2acc_parity` | 1 | 1 | 2 | parity | 256 | 19 | 12 | 5 | 2.40x | 2 / 4 | 2 / 3 / 3 |
| `1state1ap3acc` | 1 | 1 | 3 | gba | 65536 | 10 | 7 | 5 | 1.40x | 1 / 2 | 2 / 3 / 4 |
| `1state1ap3acc_parity` | 1 | 1 | 3 | parity | 65536 | 39 | 23 | 6 | 3.83x | 2 / 10 | 2 / 3 / 3 |
| `1state2ap0acc` | 1 | 2 | 0 | gba | 16 | 16 | 6 | 6 | 1.00x | 1 / 1 | 2 / 3 / 3 |
| `1state2ap1acc` | 1 | 2 | 1 | gba | 256 | 77 | 25 | 22 | 1.14x | 1 / 2 | 2 / 3 / 4 |
| `1state2ap1acc_parity` | 1 | 2 | 1 | parity | 256 | 77 | 25 | 22 | 1.14x | 1 / 2 | 2 / 3 / 4 |
| `1state2ap2acc` | 1 | 2 | 2 | gba | 65536 | 272 | 83 | 66 | 1.26x | 1 / 2 | 2 / 4 / 6 |
| `1state2ap2acc_parity` | 1 | 2 | 2 | parity | 65536 | 317 | 98 | 58 | 1.69x | 2 / 4 | 2 / 4 / 5 |
| `1state3ap0acc` | 1 | 3 | 0 | gba | 256 | 256 | 52 | 52 | 1.00x | 1 / 1 | 2 / 3 / 3 |
| `1state3ap1acc` | 1 | 3 | 1 | gba | 65536 | 6553 | 1512 | 1480 | 1.02x | 1 / 2 | 2 / 4 / 4 |
| `2state1ap0acc` | 2 | 1 | 0 | gba | 256 | 53 | 30 | 25 | 1.20x | 1 / 2 | 2 / 5 / 12 |
| `2state1ap1acc` | 2 | 1 | 1 | gba | 65536 | 1845 | 929 | 129 | 7.20x | 2 / 331 | 2 / 8 / 21 |
| `2state1ap1acc_parity` | 2 | 1 | 1 | parity | 65536 | 1845 | 929 | 129 | 7.20x | 2 / 331 | 2 / 8 / 21 |
| `2state2ap0acc` | 2 | 2 | 0 | gba | 65536 | 30613 | 11542 | 11312 | 1.02x | 1 / 2 | 2 / 12 / 17 |
| `3state1ap0acc` | 3 | 1 | 0 | gba | 262144 | 7908 | 4033 | 1645 | 2.45x | 2 / 128 | 2 / 21 / 121 |

## Non-exhaustive samples (past the tractability wall)

A uniform random probe of the id space, distinct languages accumulated as found — never a complete census (`exhaustive: false`). `langs` is the live folder count; extraction may still be running.

| shape | seed | acc | id-space | draws | langs (live) | capped |
|---|---|---|---|---|---|---|
| `2state1ap1acc` | 0 | gba | 65536 | 261 | 30 | 0 |
| `2state1ap2acc_parity` | 0 | parity | 4294967296 | 204800 | 588 | 0 |
