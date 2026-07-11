# K-series — extended-corpus measurement drop (K-E1 / K-E3 / K-E7)

- date: 2026-07-11
- git: cd8d90bb0 (probes: `tests/cascade/`, committed through a724906cb)
- corpus: `genaut/corpus/flat_canon` — **6 222** `.sos` (3 738 LTL / 2 484
  non-LTL; the extended catalogue: campaign +1000 primals to Wagner ω³/ω⁴,
  plus the late pair `3state1ap2acc_parity_0009241386589983080592`(+`_c`))
- census records: `python3 -m tests.sos2ltl.census_build
  genaut/corpus/flat_canon/sos --out tests/cascade/logs/census_flat_canon.jsonl`
  (6 222 records; **8 786** layer readings `UNDECIDED` over **2 114**
  languages — the K-E1 stratum)
- timeout convention: 60 s per command on the cluster; `TIMEOUT` is data
  (EXP/PSPACE-hard problems), it delimits the heavy stratum.

## K-E1 pass 1 — (C)-coverage (cluster run `20260711-190325-k_e1`)

`cluster/oarrun.sh --name k_e1 --split 500 --timeout 60 --walltime 0:15:00
tests/cascade/logs/cmds_k_e1.txt` — 2 114 per-language commands
(`tests/cascade/k_e1_one.py`), all accounted in 10 reap rounds (~17 min):
**1 642 ok, 472 timeout, 0 fail**. Data: `k_e1_cluster.csv` (6 610 layer
rows).

| result | layers |
|---|--:|
| (C) decides at k=0 | 6 105 |
| (C) decides at k=1 | 346 |
| (C) decides at k=2 | 159 |
| **decided** | **6 610 / 8 786** |
| missing (their language hit the 60 s cap) | 2 176 |

Every decided layer decides at **k ≤ 2**. No `CONFLICT` row can appear in
pass 1: `sweep_layer` reports one only after four full-width decides, which
never fits the 60 s cap — conflicts sit in the 472-language timeout stratum
by construction. Mechanism sums over decided rows (K-E7 piggyback):
absorption 14 050 pairs, group 7 387, non-splitting `other` 3 076,
**verdict-splitting `other` = 0** (no third mechanism in the decided mass).

## K-E1 pass 2 — conflict hunt on the timeout stratum (SUBMITTED, id lost)

`tests/cascade/k_e1_verify.py <id> <layer> 0` (early-exit `find_c_conflict`
+ inline ALG-7: member toggle + non-conjugacy) over the 2 176 missing
`(id, layer)` pairs — `tests/cascade/logs/cmds_k_e1_verify.txt`, regen:
join `census_flat_canon.jsonl`'s UNDECIDED readings against
`k_e1_cluster.csv`. The submission client was killed at its 5-min cap
**after an unknown number of `oarsub` calls**; the run id
(`20260711-HHMMSS-k_e1v`, submitted ≈ 19:50–19:55) was never printed.
Recovery, either: (a) list `$REMOTE_RUNS` for `*k_e1v*` (one ssh, needs
user's ok) and `cluster/reap_until.sh` it; or (b) resubmit fresh under a
new name (`--name k_e1v2`) — safe, a fresh id writes its own run dir, the
only cost is duplicated cluster time.

## K-F12 specimen (ALG-7 verified, `kf12_specimen_alg7.txt`)

`2state2ap1acc_parity_3772037665` — 13 classes, aperiodic, Wagner (ω³, σ),
frozen singleton layer {5}: `find_c_conflict` at k=0 in 27 states; loops
(idem 12, rejects) vs (idem 5, accepts) share the recurring edge set
(|F|=3); `inv.member` toggles; pairs non-conjugate ⟹ **GENUINE** — the
first in-frame floor inhabitant (ledger K-F12). Regen:
`python3 -m tests.cascade.k_e1_verify 2state2ap1acc_parity_3772037665 5 0`.

## K-E3 — one-sidedness + Cor C.9 stratum (local rerun, patched decider)

`python3 -m tests.cascade.k_e3_sweep tests/cascade/logs/census_flat_canon.jsonl
genaut/corpus/flat_canon/sos --out …` → `k_e3.csv` (5 050 languages with a
(C)-decided final layer at k ≤ 3).

| family side (≥2-class collected F) | layers |
|---|--:|
| upward | 16 |
| downward | 16 |
| both | 28 |
| neither | 14 |
| **total** | **74** |

The up/down tie is structural: the catalogue is complement-closed and
complement swaps the closure direction. Cor C.9 gating stratum
(prefix-independent ∧ terminal non-frozen anchored ∧ upward): **0**.

## K-E3 pfxind — prefix-independence forces a frozen final layer

`python3 -m tests.cascade.k_e3_pfxind …` → `k_e3_pfxind.txt`: of 6 220
scanned languages (late pair scanned separately: not prefix-independent),
**1 104 prefix-independent, 0 with a non-frozen final layer** — the
implication holds frame-wide (was 132/132 on the old cut).
