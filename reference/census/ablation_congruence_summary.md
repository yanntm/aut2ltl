# Congruence column — P9 / P10 / dual symmetry

source: `tests/sosl/logs/ablate_full.csv`  (6222 ablation rows)

| verdict | fixpoint_congruent | rows |
|---|---|---|
| ACCEPTOR_ONLY | false | 3137 |
| BUDGET | false | 12 |
| BUDGET | n/a | 719 |
| BUDGET | true | 5 |
| OVERSIZE | n/a | 13 |
| SOUND | true | 2336 |

dual pairs: 3111 — of which 378 have a side that never decided (BUDGET/OVERSIZE `n/a`) and are not comparable; 2733 compared

- **P9 (build-stopping)**: clean
- **P10 (theory finding)**: clean
- **dual symmetry**: clean
