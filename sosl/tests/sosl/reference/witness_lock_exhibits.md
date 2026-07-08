# Witness lock — prefix-independent permanent stalls

The refutation of the prefix-dependence necessity conjecture: prefix-independent languages whose right-congruence fixpoint is a **certified permanent stall**, recovered only by the saturation sweep's ω-power (rotation) columns.

### 2state1ap2acc_parity_0088836118

Coarse fixpoint (no-sat+exact, certified): **8 classes**. Canonical (saturation on): **10 classes**. The gap is reached with 1 counterexample(s) and 5 saturation escalation(s).

Coarse `.sos` (the non-canonical fixpoint the exact oracle certifies):
```
SOS v1
ap: a
classes: 8
0 eps
1 !a
2 a
3 !a;!a
4 !a;a
5 a;!a
6 a;a
7 !a;!a;a
letters: !a->1 a->2
mult:
0: 0 1 2 3 4 5 6 7
1: 1 3 4 3 7 1 6 7
2: 2 5 6 1 2 6 6 4
3: 3 3 7 3 7 3 6 7
4: 4 1 6 3 4 6 6 7
5: 5 1 2 3 4 5 6 7
6: 6 6 6 6 6 6 6 6
7: 7 3 6 3 7 6 6 7
accept:
3 3
6 3
6 7
7 7
```

Canonical `.sos`:
```
SOS v1
ap: a
classes: 10
0 eps
1 !a
2 a
3 !a;!a
4 !a;a
5 a;!a
6 a;a
7 !a;!a;a
8 a;!a;!a
9 a;!a;!a;a
letters: !a->1 a->2
mult:
0: 0 1 2 3 4 5 6 7 8 9
1: 1 3 4 3 7 1 6 7 3 7
2: 2 5 6 8 2 6 6 9 6 6
3: 3 3 7 3 7 3 6 7 3 7
4: 4 1 6 3 4 6 6 7 6 6
5: 5 8 2 8 9 5 6 9 8 9
6: 6 6 6 6 6 6 6 6 6 6
7: 7 3 6 3 7 6 6 7 6 6
8: 8 8 9 8 9 8 6 9 8 9
9: 9 8 6 8 9 6 6 9 6 6
accept:
3 3
3 8
6 3
6 7
6 8
7 7
8 3
8 8
9 7
```

Separating left context — the saturation escalation(s) that recover the merged class(es):

| chain | split | minted column |
|---|---|---|
| branch1 | a -> a, !a;a | !a·([]·!a)^ω |
| frozen | a -> a, a;a | !a·([]·!a;!a)^ω |
| branch1 | !a -> !a, !a;!a;a ; !a;a -> !a;a, a;!a | a;!a;!a·([]·a;!a;!a)^ω |
| frozen | !a -> !a, a;!a;!a | a·([]·!a;a)^ω |
| frozen | !a;a -> !a;a, a;!a;!a;a | a·([]·!a;!a;a)^ω |

### 2state1ap2acc_parity_1178851077

Coarse fixpoint (no-sat+exact, certified): **14 classes**. Canonical (saturation on): **16 classes**. The gap is reached with 2 counterexample(s) and 10 saturation escalation(s).

Coarse `.sos` (the non-canonical fixpoint the exact oracle certifies):
```
SOS v1
ap: a
classes: 14
0 eps
1 !a
2 a
3 !a;!a
4 !a;a
5 a;!a
6 a;a
7 !a;!a;!a
8 !a;!a;a
9 !a;a;!a
10 a;!a;!a
11 !a;!a;!a;a
12 !a;!a;a;!a
13 !a;a;!a;!a
letters: !a->1 a->2
mult:
0: 0 1 2 3 4 5 6 7 8 9 10 11 12 13
1: 1 3 4 7 8 9 6 7 11 12 13 11 7 3
2: 2 5 6 10 2 6 6 12 2 5 6 8 5 10
3: 3 7 8 7 11 12 6 7 11 7 3 11 7 7
4: 4 9 6 13 4 6 6 7 4 9 6 11 9 13
5: 5 10 2 12 2 5 6 3 8 5 10 8 12 10
6: 6 6 6 6 6 6 6 6 6 6 6 6 6 6
7: 7 7 11 7 11 7 6 7 11 7 7 11 7 7
8: 8 12 6 3 8 6 6 7 8 12 6 11 12 3
9: 9 13 4 7 4 9 6 7 11 9 13 11 7 13
10: 10 12 2 3 8 5 6 7 8 12 10 11 12 3
11: 11 7 6 7 11 6 6 7 11 7 6 11 7 7
12: 12 3 8 7 8 12 6 7 11 12 3 11 7 3
13: 13 7 4 7 11 9 6 7 11 7 13 11 7 7
accept:
6 7
6 11
7 7
11 11
```

Canonical `.sos`:
```
SOS v1
ap: a
classes: 16
0 eps
1 !a
2 a
3 !a;!a
4 !a;a
5 a;!a
6 a;a
7 !a;!a;!a
8 !a;!a;a
9 !a;a;!a
10 a;!a;!a
11 !a;!a;!a;a
12 !a;!a;a;!a
13 !a;a;!a;!a
14 a;!a;!a;!a
15 a;!a;!a;!a;a
letters: !a->1 a->2
mult:
0: 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
1: 1 3 4 7 8 9 6 7 11 12 13 11 7 3 7 11
2: 2 5 6 10 2 6 6 14 2 5 6 15 5 10 6 6
3: 3 7 8 7 11 12 6 7 11 7 3 11 7 7 7 11
4: 4 9 6 13 4 6 6 7 4 9 6 11 9 13 6 6
5: 5 10 2 14 2 5 6 14 15 5 10 15 14 10 14 15
6: 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6 6
7: 7 7 11 7 11 7 6 7 11 7 7 11 7 7 7 11
8: 8 12 6 3 8 6 6 7 8 12 6 11 12 3 6 6
9: 9 13 4 7 4 9 6 7 11 9 13 11 7 13 7 11
10: 10 14 2 14 15 5 6 14 15 14 10 15 14 14 14 15
11: 11 7 6 7 11 6 6 7 11 7 6 11 7 7 6 6
12: 12 3 8 7 8 12 6 7 11 12 3 11 7 3 7 11
13: 13 7 4 7 11 9 6 7 11 7 13 11 7 7 7 11
14: 14 14 15 14 15 14 6 14 15 14 14 15 14 14 14 15
15: 15 14 6 14 15 6 6 14 15 14 6 15 14 14 6 6
accept:
6 7
6 11
6 14
7 7
7 14
11 11
14 7
14 14
15 11
```

Separating left context — the saturation escalation(s) that recover the merged class(es):

| chain | split | minted column |
|---|---|---|
| branch1 | a -> a, !a;a | !a;!a·([]·!a;!a)^ω |
| frozen | a -> a, a;a | !a;!a·([]·!a;!a;!a)^ω |
| frozen | !a;a -> !a;a, !a;!a;a | eps·([]·!a)^ω |
| branch1 | !a;a -> !a;a, a;!a | a;!a;!a·([]·!a;a;!a;!a)^ω |
| branch1 | !a;!a;a -> !a;!a;a, !a;a;!a | a;!a·([]·!a;a;!a)^ω |
| frozen | !a;!a -> !a;!a, !a;!a;!a;a | !a;!a·([]·a;!a;!a)^ω |
| branch1 | !a;!a;a -> !a;!a;a, a;!a;!a | !a;!a;!a·([]·a;!a;!a;!a)^ω |
| frozen | !a -> !a, !a;!a;a;!a ; !a;!a -> !a;!a, !a;a;!a;!a | eps·([]·a;!a)^ω |
| frozen | !a;!a;a;!a -> !a;!a;a;!a, a;!a;!a;!a | a·([]·!a;!a;a)^ω |
| frozen | !a;!a;a -> !a;!a;a, a;!a;!a;!a;a | a·([]·!a;!a;!a;a)^ω |
