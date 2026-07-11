date: 2026-07-11
git: 4c7aa9fb5
seed: 20260711
corpus: genaut/corpus/flat_canon

# GT1 — the interval object and its endpoint decisions

The `sosl.sos.giventhat` interval core against its acceptance gates
(spec §3.6): the fixture pair of paper §5.2 and the 700-pair corpus
campaign. Regen: `cd sosl && python3 -m tests.giventhat.interval_gate
--fixture` and `... --campaign` (raw rows: `gt1_bits.csv` beside this
file; working checkpoint `sosl/tests/giventhat/logs/gt1_campaign.ckpt`).

## The fixture pair (spec §3.5, paper §5.2)

| fact | expected | measured |
|---|---|---|
| `\|C(D_ab)\|` | 6 (paper hand count) | **6** |
| `\|C(D_K)\|` | datum | **6** |
| product table | — | n = 6, linked pairs = 7 |
| `k_settles_phi` | False, loop-2 witness in both | False, `eps.(p;!p)^w` = `(ab)^w`, replays in both HOAs |
| `k_refutes_phi` | False, witness in `D_K` only | False, `eps.(!p;p)^w` = `(ba)^w`, in `D_K`, not in `D_ab` |
| `iv.bits` | >= 1 (datum) | **2** |

Metamorphic endpoint gate: 210 lassos (exhaustive `|u|,|v| <= 3`), zero
violations.

## The 700-pair campaign (seed 20260711)

300 same-stratum pairs sampled proportionally + the 300 reversed + 100
complement-partner pairs (content-hash partner map). 699 scored, 1
F2-budget skip, **zero unexplained rows**; every scored pair passed all
four gates (Prop 3.1 runtime law, conjugacy partition, metamorphic
endpoints with >= 500 sampled lassos, choice laws with 20 seeded
subsets, endpoint cross-oracles with det-HOA witness replays).

### `|F|` — the freedom in bits (report F3)

min 0 / median 20 / p95 124 / max 458 over 699 scored pairs;
`bits = 0` share 1/699 (the point-interval case
`1state1ap0acc_0 x 1state1ap0acc_3`, where K settles phi outright).

### Endpoint kill rates (report F4)

| population | scored | settles | refutes |
|---|--:|--:|--:|
| fwd | 300 | 21 (7.0%) | 17 (5.7%) |
| rev | 299 | 21 (7.0%) | 12 (4.0%) |
| comp | 100 | **100 (100%)** | 0 |

`settles` is symmetric in the pair (emptiness of an intersection) — fwd
and rev agree at 21, the built-in cross-check. `refutes` is directional
(an inclusion), and differs: 17 vs 12. The complement stratum settles
always, as predicted (`p_min = empty` by construction), and its
`k_settles_phi` agreed with `intersecting_word` finding nothing on all
100 pairs.

### Cost

Total 252.7 s over 699 scored pairs; max scored case 12.5 s. The one
F2 skip (`3state1ap0acc_029734_c x 3state1ap0acc_007436`, reversed
direction only; its forward twin scored at 11.9 s with product n = 492,
linked = 6895, bits = 121) blows the 15 s cap inside the *gate's*
per-class `saturate` re-check (`O(|linked| * n^2)` per class), not in
`given_that` itself — the construction had already produced its
interval on the forward run.
