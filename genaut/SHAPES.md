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

## Feasible shapes (the dedup funnel, from corpus/*/census.md)

The columns trace one shape's collapse across the pipeline's dedup levels:
`combos` (generator-id space `N`) -> `byte-distinct` (md5 after Spot reduction) ->
`kept` (AP-canonical, the `tgba/` tier: distinct up to `a<->!a` polarity and AP
rename) -> **`langs`** (the `det/` and `sos/` tiers: distinct languages by the
syntactic `𝓘` dedup). `collapse` is `kept / langs` — how many relabel-distinct
TGBA share one language. `survey`: the high-`kept` shapes (**deferred**) are heavy
and run separately. A `—` in `langs` means the canonical tier is not built yet
(`python3 genaut/gen/rebuild.py`).

| shape | n | k | c | slots | N (combos) | byte-distinct | **kept** | **langs** | collapse | survey |
|---|---|---|---|---|---|---|---|---|---|---|
| `1state1ap0acc` | 1 | 1 | 0 | 1 | 4 | 4 | **3** | **3** | 1.00x |  |
| `1state1ap1acc` | 1 | 1 | 1 | 2 | 16 | 7 | **5** | **4** | 1.25x |  |
| `1state2ap0acc` | 1 | 2 | 0 | 1 | 16 | 16 | **6** | **6** | 1.00x |  |
| `1state1ap2acc` | 1 | 1 | 2 | 4 | 256 | 10 | **7** | **5** | 1.40x |  |
| `1state2ap1acc` | 1 | 2 | 1 | 2 | 256 | 77 | **25** | **22** | 1.14x |  |
| `1state3ap0acc` | 1 | 3 | 0 | 1 | 256 | 256 | **52** | **52** | 1.00x |  |
| `2state1ap0acc` | 2 | 1 | 0 | 4 | 256 | 53 | **30** | **25** | 1.20x |  |
| `1state1ap3acc` | 1 | 1 | 3 | 8 | 65536 | 10 | **7** | **5** | 1.40x |  |
| `1state1ap3acc_parity` | 1 | 1 | 3 | 8 | 65536 | 39 | **23** | **6** | 3.83x |  |
| `1state2ap2acc` | 1 | 2 | 2 | 4 | 65536 | 272 | **83** | **66** | 1.26x |  |
| `1state2ap2acc_parity` | 1 | 2 | 2 | 4 | 65536 | 317 | **98** | **58** | 1.69x |  |
| `1state3ap1acc` | 1 | 3 | 1 | 2 | 65536 | 6553 | **1512** | **1480** | 1.02x | deferred |
| `2state1ap1acc` | 2 | 1 | 1 | 8 | 65536 | 1845 | **929** | **129** | 7.20x |  |
| `2state2ap0acc` | 2 | 2 | 0 | 4 | 65536 | 30613 | **11542** | **11312** | 1.02x | deferred |
| `3state1ap0acc` | 3 | 1 | 0 | 9 | 262144 | 7908 | **4033** | **1645** | 2.45x | deferred |

## Beyond the wall (first intractable)

| shape | N | why |
|---|---|---|
| `2state2ap1acc` | 16^8 ~ 4.3e9 | the true k=2 analog of 2state1ap1acc |
| `1state2ap3acc` | 16^8 ~ 4.3e9 | |
| `1state3ap2acc` | 256^4 ~ 4.3e9 | |
| `3state2ap0acc` | 16^9 ~ 6.9e10 | |
| `3state1ap1acc` | 4^18 ~ 6.9e10 | 3-state with both an AP and acceptance |

## Reading the numbers

- **`k >= 1` only.** 0-AP shapes are excluded: a one-letter alphabet has a single
  ω-word, so the only languages are `0` and `1` — no linguistic content to census.
- **`k` drives the polarity fold**: the relabel group is `2^k * k!`, so the fold grows
  fast with APs.
- **The LTL frontier is `n >= 2` AND `k >= 1`**: counting needs a multi-state cycle
  over a real alphabet (a non-aperiodic monoid). 1-state shapes stay all-LTL; not-LTL
  first appears at `2state1ap0acc`.
- **Generation is cheap; surveying is not** — running `aut2ltl` over a shape's `kept`
  automata scales with `kept`, so the high-`kept` shapes are surveyed separately.
