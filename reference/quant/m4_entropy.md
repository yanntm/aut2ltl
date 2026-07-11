# M4 — entropy: certified enclosures and the laws

- date: 2026-07-11
- git: 86217ce85
- corpus: /home/ythierry/git/BuchiToLTL/genaut/corpus/flat_canon (6222 .sos files)
- seeds: pair sample seed on the driver command line; case mode is deterministic
- regeneration (from `sosl/`): cases `python3 -m tests.quant.m4_gate --list | while read f; do timeout 15 python3 -m tests.quant.m4_gate "$f" >/dev/null; done`; pairs `python3 -m tests.quant.m4_gate --pairs 1000 1 | tee tests/quant/logs/m4_pair_sample.txt | while read a b; do timeout 15 python3 -m tests.quant.m4_gate $a $b >/dev/null; done`; then `python3 -m tests.quant.m4_gate --aggregate`

| law | sample | green | red | budget-blown |
|---|---|---|---|---|
| case laws: emptiness, 1 <= rho_lo, rho_hi <= |Sigma|, structural h(cl(L)) = h(L) (0 non-converged brackets, data) | 6222 | 6222 | 0 | 0 |
| monotonicity under inclusion (110 pairs with an inclusion) | 1000 | 1000 | 0 | 0 |

A budget-blown row (15s per-case `timeout`) and a non-converged bracket (still a valid enclosure by Collatz-Wielandt) are recorded data, not law violations. `h` is reported as the ulp-widened float bracket; every law above is decided on the exact rational side.
