# SoS algebra summary — a_implies_xa

Canonical syntactic ω-semigroup `S(L)₊` read off each input automaton. `TM` = transition monoid; a group in `TM` may be a presentation artifact, a group in `S(L)₊` is intrinsic (⇔ not LTL-definable).

## Fingerprints

| input | \|Q\| | \|EM¹\| | \|S(L)₊¹\| | grp TM | grp S(L)₊ | LTL? | evidence |
|---|---|---|---|---|---|---|---|
| a_implies_xa | 4 | 5 | 5 | no | no | yes | LTL — DG DAG 16 nodes / flat tree 63,026 (0.001s) |

## a_implies_xa

*Input:* `research_notes/sos_figs/sources/a_implies_xa.hoa`

### Deterministic form `D`

```hoa
HOA: v1
States: 4
Start: 2
AP: 1 "a"
acc-name: Buchi
Acceptance: 1 Inf(0)
properties: trans-labels explicit-labels trans-acc complete
properties: deterministic very-weak
--BODY--
State: 0
[0] 1 {0}
[!0] 3 {0}
State: 1
[t] 1 {0}
State: 2
[0] 0 {0}
[!0] 1 {0}
State: 3
[t] 3
--END--
```

### Enriched monoid `EM(D)` → `S(L)₊`

`|EM¹| = 5` elements folding onto `|S(L)₊¹| = 5` classes. `rmul` is right-multiplication by each letter (`!a`, `a`), as `EM` element ids. The identity element hosts two classes (`[eps]` and any neutral non-empty class).

| id | word | st | mk | rmul | → class |
|---|---|---|---|---|---|
| 0 | `eps` | [0 1 2 3] | [{} {} {} {}] | 1 2 | 0 `eps` |
| 1 | `!a` | [3 1 1 3] | [{0} {0} {0} {}] | 1 1 | 1 `!a` |
| 2 | `a` | [1 1 0 3] | [{0} {0} {0} {}] | 3 4 | 2 `a` |
| 3 | `a;!a` | [1 1 3 3] | [{0} {0} {0} {}] | 3 3 | 3 `a;!a` |
| 4 | `a;a` | [1 1 1 3] | [{0} {0} {0} {}] | 4 4 | 4 `a;a` |

### Canonical algebra `S(L)₊¹`

| class | key (shortlex-least word) | idem |
|---|---|---|
| 0 | `eps` | ✓ |
| 1 | `!a` | ✓ |
| 2 | `a` |  |
| 3 | `a;!a` | ✓ |
| 4 | `a;a` | ✓ |

*Letter map:* `!a` → 1, `a` → 2.

*Multiplication* (row `i` · col `j`):

```
·  0  1  2  3  4
0  0  1  2  3  4
1  1  1  1  1  1
2  2  3  4  4  4
3  3  3  3  3  3
4  4  4  4  4  4
```

*Accepting linked pairs* (6 of 14): `([!a],[!a])`, `([!a],[a;!a])`, `([!a],[a;a])`, `([a;a],[!a])`, `([a;a],[a;!a])`, `([a;a],[a;a])`.

### Invariant `𝓘(L)` — `.sos` serialization

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
residuals: 4
0 eps
1 !a
2 a
3 a;!a
res-step:
0: 1 2
1: 1 1
2: 3 1
3: 3 3
```

