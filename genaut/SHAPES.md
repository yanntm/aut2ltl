# genaut shapes — the bestiary map

The shapes the census enumerates, and the tractability wall. A **shape** is
`Shape(n, k, c)` — `n` states, `k` atomic propositions, `c` acceptance sets (see
[`gen/algorithm.md`](gen/algorithm.md)). Each shape's generator-id space is

```
slots = n^2 * 2^c                      (one edge slot per (src, dst, markset))
N     = (2^(2^k)) ^ slots              (guards = all Boolean functions over k APs)
```

`N` is **doubly exponential in `k`**, exponential in `n^2` and `2^c`, so exhaustive
enumeration only reaches small shapes. Each row below is a one-off census written to
`corpus/<tag>/` with a `census.md`; **this table is generated from those census.md
files** (`python3 genaut/shapes_table.py`), not hand-kept.

## Feasible shapes (from corpus/*/census.md)

`kept` = distinct automata after both dedup gates (md5, then polarity o names);
`polarity` = relabel twins folded by the second gate. `survey`: most are surveyed
into `logs/<tag>/`; the high-`kept` ones (**deferred**) are heavy and run separately.

| shape | n | k | c | slots | N (combos) | byte-distinct | polarity | **kept** | survey |
|---|---|---|---|---|---|---|---|---|---|
| `1state0ap0acc` | 1 | 0 | 0 | 1 | 2 | 2 | 0 | **2** |  |
| `1state0ap1acc` | 1 | 0 | 1 | 2 | 4 | 2 | 0 | **2** |  |
| `1state1ap0acc` | 1 | 1 | 0 | 1 | 4 | 4 | 1 | **3** |  |
| `1state1ap1acc` | 1 | 1 | 1 | 2 | 16 | 7 | 2 | **5** |  |
| `1state2ap0acc` | 1 | 2 | 0 | 1 | 16 | 16 | 10 | **6** |  |
| `2state0ap0acc` | 2 | 0 | 0 | 4 | 16 | 3 | 0 | **3** |  |
| `1state1ap2acc` | 1 | 1 | 2 | 4 | 256 | 10 | 3 | **7** |  |
| `1state2ap1acc` | 1 | 2 | 1 | 2 | 256 | 77 | 52 | **25** |  |
| `1state3ap0acc` | 1 | 3 | 0 | 1 | 256 | 256 | 204 | **52** |  |
| `2state0ap1acc` | 2 | 0 | 1 | 8 | 256 | 6 | 0 | **6** |  |
| `2state1ap0acc` | 2 | 1 | 0 | 4 | 256 | 53 | 23 | **30** |  |
| `3state0ap0acc` | 3 | 0 | 0 | 9 | 512 | 3 | 0 | **3** |  |
| `1state1ap3acc` | 1 | 1 | 3 | 8 | 65536 | 10 | 3 | **7** |  |
| `1state2ap2acc` | 1 | 2 | 2 | 4 | 65536 | 272 | 189 | **83** |  |
| `1state3ap1acc` | 1 | 3 | 1 | 2 | 65536 | 6553 | 5041 | **1512** | deferred |
| `2state0ap2acc` | 2 | 0 | 2 | 16 | 65536 | 91 | 0 | **91** |  |
| `2state1ap1acc` | 2 | 1 | 1 | 8 | 65536 | 1845 | 916 | **929** |  |
| `2state2ap0acc` | 2 | 2 | 0 | 4 | 65536 | 30613 | 19071 | **11542** | deferred |
| `4state0ap0acc` | 4 | 0 | 0 | 16 | 65536 | 3 | 0 | **3** |  |
| `3state0ap1acc` | 3 | 0 | 1 | 18 | 262144 | 281 | 0 | **281** |  |
| `3state1ap0acc` | 3 | 1 | 0 | 9 | 262144 | 7908 | 3875 | **4033** | deferred |

## Beyond the wall (first intractable)

| shape | N | why |
|---|---|---|
| `2state2ap1acc` | 16^8 ~ 4.3e9 | the true k=2 analog of 2state1ap1acc |
| `1state2ap3acc` | 16^8 ~ 4.3e9 | |
| `1state3ap2acc` | 256^4 ~ 4.3e9 | |
| `3state2ap0acc` | 16^9 ~ 6.9e10 | |
| `3state1ap1acc` | 4^18 ~ 6.9e10 | 3-state with both an AP and acceptance |

## Reading the numbers

- **0-AP shapes never fold by polarity** (no literals to flip) and collapse hardest:
  over a one-letter alphabet a language is fixed by its accepting structure alone, so
  `2state0ap0acc`, `3state0ap0acc`, `4state0ap0acc` all keep just 3.
- **`k` drives the polarity fold**: the relabel group is `2^k * k!`, so the fold grows
  fast with APs.
- **Generation is cheap; surveying is not** — running `aut2ltl` over a shape's `kept`
  automata scales with `kept`, so the high-`kept` shapes are surveyed separately.
