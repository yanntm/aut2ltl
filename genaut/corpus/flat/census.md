# flat — cross-shape union of distinct languages

One representative per distinct language (3790 in all), pooled from 19 shape sources and deduped by language identity (the `.sos` `𝓘` key, [SωS26 Thm. 5.1], up to a fixed AP labeling — relabel/polarity twins are kept, a later work item). Each language is kept from the **smallest** shape that emits it, so the `<tag>_<id>` filename traces it to its minimal setting.

Excluded (alphabet-blow-up dominators): `2state2ap0acc`.


## Composition

| axis | bucket | languages |
|---|---|--:|
| acceptance family | `gba` | 3288 |
| acceptance family | `parity` | 502 |
| provenance | exhaustive | 3326 |
| provenance | sampled | 464 |
| acceptance colours | c=0 | 1699 |
| acceptance colours | c=1 | 1544 |
| acceptance colours | c=2 | 546 |
| acceptance colours | c=3 | 1 |
| **total** | | **3790** |

## Contribution by source (traversal order)

A source's `new` is the languages first seen there — those a smaller shape did not already own.

| # | source | n | k | c | family | tier | scanned | new | cumulative |
|--:|---|--:|--:|--:|---|---|--:|--:|--:|
| 1 | `1state1ap0acc` | 1 | 1 | 0 | gba | exhaustive | 3 | 3 | 3 |
| 2 | `1state1ap1acc` | 1 | 1 | 1 | gba | exhaustive | 4 | 1 | 4 |
| 3 | `1state1ap1acc_parity` | 1 | 1 | 1 | parity | exhaustive | 4 | 0 | 4 |
| 4 | `1state1ap2acc` | 1 | 1 | 2 | gba | exhaustive | 5 | 1 | 5 |
| 5 | `1state1ap2acc_parity` | 1 | 1 | 2 | parity | exhaustive | 5 | 1 | 6 |
| 6 | `1state1ap3acc` | 1 | 1 | 3 | gba | exhaustive | 5 | 0 | 6 |
| 7 | `1state1ap3acc_parity` | 1 | 1 | 3 | parity | exhaustive | 6 | 1 | 7 |
| 8 | `1state2ap0acc` | 1 | 2 | 0 | gba | exhaustive | 6 | 4 | 11 |
| 9 | `1state2ap1acc` | 1 | 2 | 1 | gba | exhaustive | 22 | 16 | 27 |
| 10 | `1state2ap1acc_parity` | 1 | 2 | 1 | parity | exhaustive | 22 | 0 | 27 |
| 11 | `1state2ap2acc` | 1 | 2 | 2 | gba | exhaustive | 66 | 44 | 71 |
| 12 | `1state2ap2acc_parity` | 1 | 2 | 2 | parity | exhaustive | 58 | 36 | 107 |
| 13 | `1state3ap0acc` | 1 | 3 | 0 | gba | exhaustive | 52 | 50 | 157 |
| 14 | `1state3ap1acc` | 1 | 3 | 1 | gba | exhaustive | 1480 | 1427 | 1584 |
| 15 | `2state1ap0acc` | 2 | 1 | 0 | gba | exhaustive | 25 | 22 | 1606 |
| 16 | `2state1ap1acc` | 2 | 1 | 1 | gba | exhaustive | 129 | 100 | 1706 |
| 17 | `2state1ap1acc_parity` | 2 | 1 | 1 | parity | exhaustive | 129 | 0 | 1706 |
| 18 | `3state1ap0acc` | 3 | 1 | 0 | gba | exhaustive | 1645 | 1620 | 3326 |
| 19 | `2state1ap2acc_parity__seed0` | 2 | 1 | 2 | parity | **sampled** | 591 | 464 | 3790 |

Built by `python3 genaut/gen/flatten.py`.
