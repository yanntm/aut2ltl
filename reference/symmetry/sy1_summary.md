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

## Full B_n sweep (n ≤ 3 rows)

- rows swept: 6222
- symmetric-element count distribution (identity included): {'1': 5600, '2': 498, '4': 52, '6': 58, '8': 2, '12': 8, '24': 4}
