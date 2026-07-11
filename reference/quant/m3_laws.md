# M3 — distance, shadow, essential: the laws

- date: 2026-07-11
- git: 423cc5ecc
- corpus: /home/ythierry/git/BuchiToLTL/genaut/corpus/flat_canon (6222 .sos files)
- seeds: pair/triple sample seeds on the driver command line; case mode is deterministic (uniform + the M2 skewed p)
- regeneration (from `sosl/`): cases `python3 -m tests.quant.m3_gate --list | while read f; do timeout 15 python3 -m tests.quant.m3_gate "$f" >/dev/null; done`; pairs `python3 -m tests.quant.m3_gate --pairs 1000 1 | tee tests/quant/logs/m3_pair_sample.txt | while read a b; do timeout 15 python3 -m tests.quant.m3_gate $a $b >/dev/null; done`; triples `python3 -m tests.quant.m3_gate --triples 500 1 | tee tests/quant/logs/m3_triple_sample.txt | while read a b c; do timeout 15 python3 -m tests.quant.m3_gate $a $b $c >/dev/null; done`; then `python3 -m tests.quant.m3_gate --aggregate`

| law | sample | green | red | budget-blown |
|---|---|---|---|---|
| case laws: d(L,sh)=d(L,es)=0, idempotence, sh⟹es consistency, Prop 4.5 p-freeness, apr⟹ltl (3738 aperiodic, 5660 ltl-up-to-null) | 6222 | 6222 | 0 | 0 |
| pair laws: symmetry both p's, sh⟹es across the pair (154 with equal shadows; 313 null-disagreement) | 1000 | 993 | 0 | 7 |
| triangle inequality | 500 | 497 | 0 | 3 |

A budget-blown row (15s per-case `timeout`, big aligned products or large essential quotients) is a recorded datum, not a law violation — no row means the kill. `pfree` red would convict paper Prop 4.5 (stop-the-line); none is expected.
