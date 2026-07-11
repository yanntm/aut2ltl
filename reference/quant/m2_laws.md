# M2 — laws L2-L5: modularity, monotonicity, trichotomy, obligation

- date: 2026-07-11
- git: ca829e5a8
- corpus: /home/ythierry/git/BuchiToLTL/genaut/corpus/flat_canon (6220 .sos files)
- seeds: pair sample seed on the driver command line; per-file p seed `20260711:<name>`
- regeneration (from `sosl/`): pairs `python3 -m tests.quant.law_gate --pairs 1000 1 | while read a b; do timeout 15 python3 -m tests.quant.law_gate "$a" "$b" >/dev/null; done`; cases `python3 -m tests.quant.law_gate --list | while read f; do timeout 15 python3 -m tests.quant.law_gate "$f" >/dev/null; done`; then `python3 -m tests.quant.law_gate --aggregate`

| law | sample | green | red | budget-blown |
|---|---|---|---|---|
| L2 modularity + L3 monotonicity (pairs; 130 with an inclusion) | 1000 | 994 | 0 | 6 |
| L4 trichotomy + L5 obligation (cases; 3182 in the obligation band) | 6220 | 6220 | 0 | — |

missing single-case rows: 0. A budget-blown pair (15s per-case cap, big aligned products) is a recorded datum, not a law violation — no row means the 15s `timeout` killed it.
