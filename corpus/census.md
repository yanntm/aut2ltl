# corpus — the language tier (`det/` + `sos/`)

**456** languages: **241** distinct ones realized by the 336 inputs of `samples/benchmark/inputs/`, plus **215** complements added to close the catalogue under complement. One `det/*.hoa` (the canonical deterministic D) and one `sos/*.sos` (the syntactic `𝓘`) per language, deduped by the `𝓘` key ([SωS26 Thm. 5.1]: byte-equal ⟺ equal language) — **up to a fixed AP labeling**, so `GF(a)` and `GF(!a)` are two entries, as are a language over `{a}` and the same over `{a,b}`. Each language is named for the **first input that realized it** (`<category>_<stem>[_L<line>]`); each added dual is `<primal>_c`.

Inputs that produced no language are listed under *Skipped* below — an algebra closure past the `|EM1| > 20000` cap, or a `>15.0s` per-input budget, or a `.sos` dump over the `1.0 MiB` size cap. Those are **not** failures of the construction, only of this build's budget: each is a genuine language whose syntactic algebra is simply large. Every one of them is rebuildable — `python3 corpus/canonize.py --max-sos 0 --cap 0 --timeout 0` admits them all — but the largest dumps tens of MiB, too big to carry as a committed test input, so they are **discarded here by policy, not missing**.


## Composition

| category | languages first seen here |
|---|--:|
| `chains/` | 17 |
| `core/` | 42 |
| `fixtures/` | 147 |
| `kinska/` | 35 |
| **primals** | **241** |
| complements added | 215 |
| **total (closed)** | **456** |

## Contribution by source file (walk order)

A source's `new` is the languages first realized there — those an earlier input did not already own. `collapsed` counts inputs whose language was already catalogued.

| # | source | scanned | new | collapsed | capped | timeout | oversize | cumulative |
|--:|---|--:|--:|--:|--:|--:|--:|--:|
| 1 | `chains/mixed.ltl` | 4 | 4 | 0 | 0 | 0 | 0 | 4 |
| 2 | `chains/release.ltl` | 3 | 3 | 0 | 0 | 0 | 0 | 7 |
| 3 | `chains/strong_until.ltl` | 3 | 3 | 0 | 0 | 0 | 0 | 10 |
| 4 | `chains/weak_until.ltl` | 3 | 1 | 2 | 0 | 0 | 0 | 11 |
| 5 | `chains/x_laced.ltl` | 6 | 6 | 0 | 0 | 0 | 0 | 17 |
| 6 | `core/bottom.ltl` | 2 | 2 | 0 | 0 | 0 | 0 | 19 |
| 7 | `core/guarantee.ltl` | 10 | 10 | 0 | 0 | 0 | 0 | 29 |
| 8 | `core/mod3_a.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 30 |
| 9 | `core/obligation.ltl` | 5 | 5 | 0 | 0 | 0 | 0 | 35 |
| 10 | `core/persistence.ltl` | 3 | 3 | 0 | 0 | 0 | 0 | 38 |
| 11 | `core/prefix_nonltl_1.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 39 |
| 12 | `core/prefix_nonltl_2.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 40 |
| 13 | `core/reactivity.ltl` | 2 | 2 | 0 | 0 | 0 | 0 | 42 |
| 14 | `core/recurrence.ltl` | 10 | 10 | 0 | 0 | 0 | 0 | 52 |
| 15 | `core/safety.ltl` | 8 | 7 | 1 | 0 | 0 | 0 | 59 |
| 16 | `fixtures/f2_successes.ltl` | 43 | 36 | 7 | 0 | 0 | 0 | 95 |
| 17 | `fixtures/formulas.ltl` | 7 | 6 | 1 | 0 | 0 | 0 | 101 |
| 18 | `fixtures/motivating_example.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 101 |
| 19 | `fixtures/second_example.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 102 |
| 20 | `fixtures/t2_successes.ltl` | 62 | 51 | 11 | 0 | 0 | 0 | 153 |
| 21 | `fixtures/terminal_2scc.ltl` | 56 | 53 | 3 | 0 | 0 | 0 | 206 |
| 22 | `fixtures/very_weak_w_until.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 206 |
| 23 | `kinska/counting-1ap-counting_buchi_1ap_01.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 207 |
| 24 | `kinska/counting-1ap-counting_buchi_1ap_02.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 207 |
| 25 | `kinska/counting-1ap-counting_buchi_1ap_03.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 208 |
| 26 | `kinska/counting-1ap-counting_buchi_1ap_04.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 208 |
| 27 | `kinska/counting-1ap-counting_buchi_1ap_05.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 209 |
| 28 | `kinska/counting-1ap-counting_buchi_1ap_06.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 210 |
| 29 | `kinska/counting-1ap-counting_buchi_1ap_07.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 211 |
| 30 | `kinska/counting-1ap-counting_buchi_1ap_08.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 212 |
| 31 | `kinska/counting-1ap-counting_buchi_1ap_09.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 213 |
| 32 | `kinska/counting-1ap-counting_buchi_1ap_10.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 214 |
| 33 | `kinska/counting-1ap-counting_buchi_1ap_11.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 215 |
| 34 | `kinska/counting-1ap-counting_buchi_1ap_12.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 216 |
| 35 | `kinska/counting-1ap-counting_buchi_1ap_13.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 216 |
| 36 | `kinska/counting-1ap-counting_buchi_1ap_14.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 216 |
| 37 | `kinska/counting-1ap-counting_buchi_1ap_15.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 217 |
| 38 | `kinska/counting-1ap-counting_buchi_1ap_16.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 217 |
| 39 | `kinska/counting-1ap-counting_buchi_1ap_17.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 217 |
| 40 | `kinska/counting-1ap-counting_buchi_1ap_18.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 218 |
| 41 | `kinska/counting-1ap-counting_buchi_1ap_19.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 218 |
| 42 | `kinska/counting-1ap-counting_buchi_1ap_20.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 218 |
| 43 | `kinska/counting-1ap-counting_buchi_1ap_21.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 219 |
| 44 | `kinska/counting-1ap-counting_buchi_1ap_22.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 219 |
| 45 | `kinska/counting-1ap-counting_buchi_1ap_23.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 219 |
| 46 | `kinska/counting-1ap-counting_buchi_1ap_24.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 220 |
| 47 | `kinska/counting-1ap-counting_buchi_1ap_25.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 220 |
| 48 | `kinska/counting-1ap-counting_buchi_1ap_26.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 220 |
| 49 | `kinska/counting-1ap-counting_buchi_1ap_27.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 221 |
| 50 | `kinska/counting-1ap-counting_buchi_1ap_28.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 221 |
| 51 | `kinska/counting-1ap-counting_buchi_1ap_29.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 222 |
| 52 | `kinska/counting-1ap-counting_buchi_1ap_30.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 222 |
| 53 | `kinska/counting-1ap-counting_buchi_1ap_31.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 222 |
| 54 | `kinska/counting-1ap-counting_buchi_1ap_32.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 222 |
| 55 | `kinska/counting-1ap-counting_buchi_1ap_33.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 222 |
| 56 | `kinska/counting-1ap-counting_buchi_1ap_34.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 222 |
| 57 | `kinska/counting-1ap-counting_buchi_1ap_35.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 222 |
| 58 | `kinska/counting-1ap-counting_buchi_1ap_36.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 222 |
| 59 | `kinska/counting-1ap-counting_buchi_1ap_37.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 222 |
| 60 | `kinska/counting-1ap-counting_buchi_1ap_38.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 222 |
| 61 | `kinska/counting-1ap-counting_buchi_1ap_39.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 222 |
| 62 | `kinska/counting-1ap-counting_buchi_1ap_40.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 222 |
| 63 | `kinska/counting-2ap-counting_buchi_2ap_01.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 222 |
| 64 | `kinska/counting-2ap-counting_buchi_2ap_02.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 223 |
| 65 | `kinska/counting-2ap-counting_buchi_2ap_03.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 223 |
| 66 | `kinska/counting-2ap-counting_buchi_2ap_04.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 224 |
| 67 | `kinska/counting-2ap-counting_buchi_2ap_05.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 225 |
| 68 | `kinska/counting-2ap-counting_buchi_2ap_06.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 226 |
| 69 | `kinska/counting-2ap-counting_buchi_2ap_07.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 226 |
| 70 | `kinska/counting-2ap-counting_buchi_2ap_08.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 227 |
| 71 | `kinska/counting-2ap-counting_buchi_2ap_09.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 227 |
| 72 | `kinska/counting-2ap-counting_buchi_2ap_10.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 227 |
| 73 | `kinska/counting-2ap-counting_buchi_2ap_11.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 228 |
| 74 | `kinska/counting-2ap-counting_buchi_2ap_12.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 228 |
| 75 | `kinska/counting-2ap-counting_buchi_2ap_13.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 228 |
| 76 | `kinska/counting-2ap-counting_buchi_2ap_14.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 229 |
| 77 | `kinska/counting-2ap-counting_buchi_2ap_15.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 229 |
| 78 | `kinska/counting-2ap-counting_buchi_2ap_16.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 229 |
| 79 | `kinska/counting-2ap-counting_buchi_2ap_17.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 230 |
| 80 | `kinska/counting-2ap-counting_buchi_2ap_18.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 230 |
| 81 | `kinska/counting-2ap-counting_buchi_2ap_19.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 230 |
| 82 | `kinska/counting-2ap-counting_buchi_2ap_20.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 231 |
| 83 | `kinska/counting-2ap-counting_buchi_2ap_21.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 231 |
| 84 | `kinska/counting-2ap-counting_buchi_2ap_22.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 231 |
| 85 | `kinska/counting-2ap-counting_buchi_2ap_23.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 231 |
| 86 | `kinska/counting-2ap-counting_buchi_2ap_24.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 232 |
| 87 | `kinska/counting-2ap-counting_buchi_2ap_25.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 233 |
| 88 | `kinska/counting-2ap-counting_buchi_2ap_26.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 233 |
| 89 | `kinska/counting-2ap-counting_buchi_2ap_27.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 233 |
| 90 | `kinska/counting-2ap-counting_buchi_2ap_28.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 233 |
| 91 | `kinska/counting-2ap-counting_buchi_2ap_29.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 233 |
| 92 | `kinska/counting-2ap-counting_buchi_2ap_30.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 234 |
| 93 | `kinska/counting-2ap-counting_buchi_2ap_31.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 235 |
| 94 | `kinska/counting-2ap-counting_buchi_2ap_32.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 236 |
| 95 | `kinska/counting-2ap-counting_buchi_2ap_33.hoa` | 1 | 0 | 0 | 0 | 0 | 1 | 236 |
| 96 | `kinska/counting-2ap-counting_buchi_2ap_34.hoa` | 1 | 0 | 0 | 0 | 0 | 1 | 236 |
| 97 | `kinska/counting-2ap-counting_buchi_2ap_35.hoa` | 1 | 0 | 0 | 0 | 1 | 0 | 236 |
| 98 | `kinska/counting-2ap-counting_buchi_2ap_36.hoa` | 1 | 0 | 0 | 0 | 1 | 0 | 236 |
| 99 | `kinska/counting-2ap-counting_buchi_2ap_37.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 236 |
| 100 | `kinska/counting-2ap-counting_buchi_2ap_38.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 236 |
| 101 | `kinska/counting-2ap-counting_buchi_2ap_39.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 236 |
| 102 | `kinska/counting-2ap-counting_buchi_2ap_40.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 236 |
| 103 | `kinska/counting-2ap-counting_buchi_2ap_41.hoa` | 1 | 0 | 0 | 0 | 1 | 0 | 236 |
| 104 | `kinska/counting-2ap-counting_buchi_2ap_42.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 236 |
| 105 | `kinska/counting-2ap-counting_buchi_2ap_43.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 236 |
| 106 | `kinska/counting-2ap-counting_buchi_2ap_44.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 236 |
| 107 | `kinska/counting-2ap-counting_buchi_2ap_45.hoa` | 1 | 0 | 0 | 1 | 0 | 0 | 236 |
| 108 | `kinska/randltl-1ap-ba-randltl-10-a-hoa-1.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 236 |
| 109 | `kinska/randltl-1ap-ba-randltl-10-a-hoa-10.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 237 |
| 110 | `kinska/randltl-1ap-ba-randltl-10-a-hoa-2.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 237 |
| 111 | `kinska/randltl-1ap-ba-randltl-10-a-hoa-4.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 238 |
| 112 | `kinska/randltl-1ap-ba-randltl-10-a-hoa-5.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 238 |
| 113 | `kinska/randltl-1ap-ba-randltl-10-a-hoa-8.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 238 |
| 114 | `kinska/randltl-1ap-ba-randltl-10-a-hoa-9.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 238 |
| 115 | `kinska/randltl-2ap-ba-randltl-10-a-hoa-3.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 238 |
| 116 | `kinska/randltl-2ap-ba-randltl-10-a-hoa-4.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 238 |
| 117 | `kinska/randltl-4ap-ba-randltl-10-a-hoa-10.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 239 |
| 118 | `kinska/randltl-4ap-ba-randltl-10-a-hoa-2.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 239 |
| 119 | `kinska/randltl-4ap-ba-randltl-10-a-hoa-3.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 239 |
| 120 | `kinska/randltl-4ap-ba-randltl-10-a-hoa-4.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 240 |
| 121 | `kinska/randltl-4ap-ba-randltl-10-a-hoa-8.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 240 |
| 122 | `kinska/randltl-8ap-ba-randltl-10-a-hoa-10.hoa` | 1 | 1 | 0 | 0 | 0 | 0 | 241 |
| 123 | `kinska/randltl-8ap-ba-randltl-10-a-hoa-4.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 241 |
| 124 | `kinska/randltl-8ap-ba-randltl-10-a-hoa-5.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 241 |
| 125 | `kinska/randltl-8ap-ba-randltl-10-a-hoa-8.hoa` | 1 | 0 | 1 | 0 | 0 | 0 | 241 |

## Skipped

| input | reason |
|---|---|
| `counting-1ap-counting_buchi_1ap_31.hoa` | capped (\|EM1\| > 20000) |
| `counting-1ap-counting_buchi_1ap_32.hoa` | capped (\|EM1\| > 20000) |
| `counting-1ap-counting_buchi_1ap_33.hoa` | capped (\|EM1\| > 20000) |
| `counting-1ap-counting_buchi_1ap_34.hoa` | capped (\|EM1\| > 20000) |
| `counting-1ap-counting_buchi_1ap_35.hoa` | capped (\|EM1\| > 20000) |
| `counting-1ap-counting_buchi_1ap_36.hoa` | capped (\|EM1\| > 20000) |
| `counting-1ap-counting_buchi_1ap_37.hoa` | capped (\|EM1\| > 20000) |
| `counting-1ap-counting_buchi_1ap_38.hoa` | capped (\|EM1\| > 20000) |
| `counting-1ap-counting_buchi_1ap_39.hoa` | capped (\|EM1\| > 20000) |
| `counting-1ap-counting_buchi_1ap_40.hoa` | capped (\|EM1\| > 20000) |
| `counting-2ap-counting_buchi_2ap_33.hoa` | oversize (\|.sos\| = 3.1 MiB > 1.0 MiB) |
| `counting-2ap-counting_buchi_2ap_34.hoa` | oversize (\|.sos\| = 18.3 MiB > 1.0 MiB) |
| `counting-2ap-counting_buchi_2ap_35.hoa` | timeout (>15.0s) |
| `counting-2ap-counting_buchi_2ap_36.hoa` | timeout (>15.0s) |
| `counting-2ap-counting_buchi_2ap_37.hoa` | capped (\|EM1\| > 20000) |
| `counting-2ap-counting_buchi_2ap_38.hoa` | capped (\|EM1\| > 20000) |
| `counting-2ap-counting_buchi_2ap_39.hoa` | capped (\|EM1\| > 20000) |
| `counting-2ap-counting_buchi_2ap_40.hoa` | capped (\|EM1\| > 20000) |
| `counting-2ap-counting_buchi_2ap_41.hoa` | timeout (>15.0s) |
| `counting-2ap-counting_buchi_2ap_42.hoa` | capped (\|EM1\| > 20000) |
| `counting-2ap-counting_buchi_2ap_43.hoa` | capped (\|EM1\| > 20000) |
| `counting-2ap-counting_buchi_2ap_44.hoa` | capped (\|EM1\| > 20000) |
| `counting-2ap-counting_buchi_2ap_45.hoa` | capped (\|EM1\| > 20000) |

Built by `python3 corpus/canonize.py`.
