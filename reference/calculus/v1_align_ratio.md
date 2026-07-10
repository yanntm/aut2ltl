# V1a — alignment-ratio distribution

- date: 2026-07-10
- git: e92495732
- seed: 20260709 (uniform), 20260710 (large), 20260711 (related)
- corpus: /home/ythierry/git/BuchiToLTL/genaut/corpus/flat_canon

Ratio = `|nodes| / (n_A * n_B)`; time is COLD `align` BFS wall (§8.1: alignment is reported cold). Pairs are sampled within alphabet strata.

| pop | pairs | min | p25 | median | p75 | p95 | max | med ms |
|---|---|---|---|---|---|---|---|---|
| uniform | 5000 | 0.0145 | 0.1329 | 0.1736 | 0.2292 | 0.3556 | 0.5925 | 0.1 |
| large | 200 | 0.0145 | 0.0867 | 0.1186 | 0.1438 | 0.2441 | 0.4027 | 0.4 |
| related | 1000 | 0.0083 | 0.0333 | 0.0625 | 0.1111 | 0.2500 | 0.3333 | 0.0 |

| pop | ratio<0.25 | ratio<0.5 | ratio<0.9 | ratio≈1.0 | F2 |
|---|---|---|---|---|---|
| uniform | 0.8084 | 0.9856 | 1.0000 | 0.0000 | 0 |
| large | 0.9500 | 1.0000 | 1.0000 | 0.0000 | 0 |
| related | 0.8580 | 1.0000 | 1.0000 | 0.0000 | 0 |

The `related` median ratio (0.0625) sits below the `uniform` median (0.1736): complement partners share the algebra, so the generated product collapses toward the diagonal, confirming §3.3's related-operands prediction.
