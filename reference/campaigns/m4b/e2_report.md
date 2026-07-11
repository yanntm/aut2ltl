# E2 — Saturation ablation

Ablation leg: `--no-saturation --eq-mode exact` (with exact equivalence every surviving stall is provably permanent). Canonical leg: `default` (saturation on).

| case | prefix-indep | ref | no-sat learned | stall class | expected | cross-check |
|---|:--:|--:|--:|---|---|:--:|
| a_implies_xa | no | 5 | 4 | permanent | permanent | ✓ |
| a_once | no | 4 | 3 | permanent | permanent | ✓ |
| even | no | 5 | 5 | transient | transient | ✓ |
| evenblocks | yes | 8 | 8 | transient | transient | ✓ |
| gf_aa_parity | no | 6 | 6 | transient | transient | ✓ |
| gf_aa_reset | no | 6 | 6 | transient | transient | ✓ |

**Stall-class frequency (ablation leg).** permanent: 2 · transient: 4.

## Permanent specimens (first-class exhibits)

### a_implies_xa

Coarse fixpoint (no-sat+exact, certified): **4 classes**. Canonical (saturation on): **5 classes**. The gap is reached with 0 counterexample(s) and 1 saturation escalation(s).

Coarse `.sos` (the non-canonical fixpoint the exact oracle certifies):
```
SOS v1
ap: a
classes: 4
0 eps
1 !a
2 a
3 a;!a
letters: !a->1 a->2
mult:
0: 0 1 2 3
1: 1 1 1 1
2: 2 3 1 1
3: 3 3 3 3
accept:
1 1
1 3
```

Canonical `.sos`:
```
SOS v1
ap: a
classes: 5
0 eps
1 !a
2 a
3 a;!a
4 a;a
letters: !a->1 a->2
mult:
0: 0 1 2 3 4
1: 1 1 1 1 1
2: 2 3 4 4 4
3: 3 3 3 3 3
4: 4 4 4 4 4
accept:
1 1
1 3
1 4
4 1
4 3
4 4
```

Separating left context — the saturation escalation(s) that recover the merged class(es):

| chain | split | minted column |
|---|---|---|
| branch1 | !a -> !a, a;a | a·([]·a)^ω |

### a_once

Coarse fixpoint (no-sat+exact, certified): **3 classes**. Canonical (saturation on): **4 classes**. The gap is reached with 1 counterexample(s) and 1 saturation escalation(s).

Coarse `.sos` (the non-canonical fixpoint the exact oracle certifies):
```
SOS v1
ap: a
classes: 3
0 eps
1 !a
2 a
letters: !a->1 a->2
mult:
0: 0 1 2
1: 1 1 1
2: 2 2 1
accept:
2 1
```

Canonical `.sos`:
```
SOS v1
ap: a
classes: 4
0 eps
1 !a
2 a
3 !a;a
letters: !a->1 a->2
mult:
0: 0 1 2 3
1: 1 1 3 3
2: 2 2 3 3
3: 3 3 3 3
accept:
2 1
```

Separating left context — the saturation escalation(s) that recover the merged class(es):

| chain | split | minted column |
|---|---|---|
| branch1 | !a -> !a, !a;a | a·[]·!a , (!a)^ω |
