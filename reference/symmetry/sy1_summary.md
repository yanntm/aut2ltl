# date: 2026-07-11
# git-rev: c8f4d3004
# seed: 20260711
# corpus: genaut/corpus/flat_canon/sos

# SY1 census summary

- cases: **6222** (by AP count: {'0': 2, '1': 4006, '2': 1438, '3': 776})
- status: {'ok': 6222}
- corpus `.cat` tags: LTL {'no': 2484, 'yes': 3738}, stutter {'invariant': 896, 'sensitive': 5326}
- candidate checks with kernel+obstruction law asserted: **69742** — zero violations (a violation aborts the run)
- wall per case ms: median 5.8, p95 142.9, max 4277.1

## F3 — inert APs

- nonempty `inert_aps`: **0** / 6222 (0%)

## F4 — generator hits

- cases with ≥1 symmetric generator: **206** (3.3108%); per generator: {'f0': 36, 'f1': 10, 't01': 82, 't02': 86, 't12': 4}
- cases with ≥1 anti generator: **8** (0.1286%); per generator: {'f0': 8, 'f1': 2}
- `anti_possible` true: **164** (2.6358%) — the pair-count fast path closes the anti question on the other 6058 cases (97.3642%)

## Stratified by AP count

| n | cases | ≥1 sym generator | ≥1 anti generator | anti_possible | nontrivial group (full sweep) | group-order distribution |
|---|---|---|---|---|---|---|
| 0 | 2 | 0 (0.00%) | 0 | 0 | 0 (0.00%) | {'1': 2} |
| 1 | 4006 | 32 (0.80%) | 6 | 132 | 32 (0.80%) | {'1': 3974, '2': 32} |
| 2 | 1438 | 38 (2.64%) | 2 | 26 | 202 (14.05%) | {'1': 1236, '2': 182, '4': 18, '8': 2} |
| 3 | 776 | 136 (17.53%) | 0 | 6 | 388 (50.00%) | {'1': 388, '2': 284, '4': 34, '6': 58, '12': 8, '24': 4} |

## Full B_n sweep (n ≤ 3 rows)

- rows swept: 6222
- symmetric-element count distribution (identity included): {'1': 5600, '2': 498, '4': 52, '6': 58, '8': 2, '12': 8, '24': 4}
