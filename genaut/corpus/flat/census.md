# flat — cross-shape union of distinct languages

One representative per distinct language (5111 in all), pooled from 30 shape sources and deduped by language identity (the `.sos` `𝓘` key, [SωS26 Thm. 5.1], up to a fixed AP labeling — relabel/polarity twins are kept, a later work item). Each language is kept from the **smallest** shape that emits it, so the `<tag>_<id>` filename traces it to its minimal setting.

Excluded (alphabet-blow-up dominators): `2state2ap0acc`.


## Composition

| axis | bucket | languages |
|---|---|--:|
| acceptance family | `gba` | 3608 |
| acceptance family | `parity` | 1503 |
| provenance | exhaustive | 3326 |
| provenance | sampled | 1785 |
| acceptance colours | c=0 | 1699 |
| acceptance colours | c=1 | 2260 |
| acceptance colours | c=2 | 1146 |
| acceptance colours | c=3 | 6 |
| **total** | | **5111** |

## Contribution by source (traversal order)

A source's `new` is the languages first seen there — those a smaller shape did not already own.

| # | source | n | k | c | family | tier | scanned | new | cumulative |
|--:|---|--:|--:|--:|---|---|--:|--:|--:|
| 1 | `1state1ap0acc` | 1 | 1 | 0 | gba | exhaustive | 3 | 3 | 3 |
| 2 | `1state1ap1acc` | 1 | 1 | 1 | gba | exhaustive | 4 | 1 | 4 |
| 3 | `1state1ap2acc` | 1 | 1 | 2 | gba | exhaustive | 5 | 1 | 5 |
| 4 | `1state1ap2acc_parity` | 1 | 1 | 2 | parity | exhaustive | 5 | 1 | 6 |
| 5 | `1state1ap3acc` | 1 | 1 | 3 | gba | exhaustive | 5 | 0 | 6 |
| 6 | `1state1ap3acc_parity` | 1 | 1 | 3 | parity | exhaustive | 6 | 1 | 7 |
| 7 | `1state2ap0acc` | 1 | 2 | 0 | gba | exhaustive | 6 | 4 | 11 |
| 8 | `1state2ap1acc` | 1 | 2 | 1 | gba | exhaustive | 22 | 16 | 27 |
| 9 | `1state2ap2acc` | 1 | 2 | 2 | gba | exhaustive | 66 | 44 | 71 |
| 10 | `1state2ap2acc_parity` | 1 | 2 | 2 | parity | exhaustive | 58 | 36 | 107 |
| 11 | `1state3ap0acc` | 1 | 3 | 0 | gba | exhaustive | 52 | 50 | 157 |
| 12 | `1state3ap1acc` | 1 | 3 | 1 | gba | exhaustive | 1480 | 1427 | 1584 |
| 13 | `2state1ap0acc` | 2 | 1 | 0 | gba | exhaustive | 25 | 22 | 1606 |
| 14 | `2state1ap1acc` | 2 | 1 | 1 | gba | exhaustive | 129 | 100 | 1706 |
| 15 | `3state1ap0acc` | 3 | 1 | 0 | gba | exhaustive | 1645 | 1620 | 3326 |
| 16 | `1state2ap3acc_parity__seedcurated` | 1 | 2 | 3 | parity | **sampled** | 5 | 5 | 3331 |
| 17 | `1state3ap2acc_parity__seedcurated` | 1 | 3 | 2 | parity | **sampled** | 8 | 8 | 3339 |
| 18 | `2state1ap2acc_parity__seed0` | 2 | 1 | 2 | parity | **sampled** | 591 | 464 | 3803 |
| 19 | `2state1ap2acc_parity__seedcurated` | 2 | 1 | 2 | parity | **sampled** | 3 | 3 | 3806 |
| 20 | `2state2ap1acc_parity__seedcurated` | 2 | 2 | 1 | parity | **sampled** | 57 | 57 | 3863 |
| 21 | `2state2ap2acc_parity__seedcurated` | 2 | 2 | 2 | parity | **sampled** | 325 | 325 | 4188 |
| 22 | `2state3ap1acc_parity__seedcurated` | 2 | 3 | 1 | parity | **sampled** | 156 | 156 | 4344 |
| 23 | `3state1ap1acc__seed0` | 3 | 1 | 1 | gba | **sampled** | 500 | 320 | 4664 |
| 24 | `3state1ap1acc_parity__seedcurated` | 3 | 1 | 1 | parity | **sampled** | 70 | 70 | 4734 |
| 25 | `3state1ap2acc_parity__seedcurated` | 3 | 1 | 2 | parity | **sampled** | 52 | 52 | 4786 |
| 26 | `3state2ap1acc_parity__seedcurated` | 3 | 2 | 1 | parity | **sampled** | 42 | 42 | 4828 |
| 27 | `3state2ap2acc_parity__seedcurated` | 3 | 2 | 2 | parity | **sampled** | 203 | 203 | 5031 |
| 28 | `4state1ap1acc_parity__seedcurated` | 4 | 1 | 1 | parity | **sampled** | 40 | 40 | 5071 |
| 29 | `4state1ap2acc_parity__seedcurated` | 4 | 1 | 2 | parity | **sampled** | 9 | 9 | 5080 |
| 30 | `4state2ap1acc_parity__seedcurated` | 4 | 2 | 1 | parity | **sampled** | 31 | 31 | 5111 |

Built by `python3 genaut/gen/flatten.py`.
