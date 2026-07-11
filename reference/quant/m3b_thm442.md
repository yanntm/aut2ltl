# M3b — Thm 4.4(2) as a biconditional: essentials ⟺ null xor-profile

- date: 2026-07-11
- git: 86217ce85
- corpus: /home/ythierry/git/BuchiToLTL/genaut/corpus/flat_canon (M3's 1000-pair sample, seed 1)
- regeneration (from `sosl/`): `python3 -m tests.quant.m3_gate --pairs 1000 1 | tee tests/quant/logs/m3_pair_sample.txt | while read a b; do timeout 15 python3 -m tests.quant.m3b_gate $a $b >/dev/null; done; python3 -m tests.quant.m3b_gate --aggregate`

| law | sample | green | red | budget-blown |
|---|---|---|---|---|
| byte-equal reduced essentials ⟺ all-zero aligned xor-profile (316 null-disagreement, 316 essential-equal) | 1000 | 999 | 0 | 1 |

Both directions asserted per pair; a red row in either direction convicts paper Thm 4.4(2) (stop-the-line). A budget-blown pair (15s `timeout`) is a recorded datum — no row means the kill.
