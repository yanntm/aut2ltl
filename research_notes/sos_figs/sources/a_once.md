# SoS algebra summary — a_once

Canonical syntactic ω-semigroup `S(L)₊` read off each input automaton. `TM` = transition monoid; a group in `TM` may be a presentation artifact, a group in `S(L)₊` is intrinsic (⇔ not LTL-definable).

## Fingerprints

| input | \|Q\| | \|EM¹\| | \|S(L)₊¹\| | grp TM | grp S(L)₊ | LTL? | evidence |
|---|---|---|---|---|---|---|---|
| a_once | 3 | 4 | 4 | no | no | yes | LTL — DG DAG 14 nodes / flat tree 93,674 (0.001s) |

## a_once

*Input:* `research_notes/sos_figs/sources/a_once.hoa`

### Deterministic form `D`

```hoa
HOA: v1
States: 3
Start: 0
AP: 1 "a"
acc-name: Buchi
Acceptance: 1 Inf(0)
properties: trans-labels explicit-labels trans-acc complete
properties: deterministic very-weak
--BODY--
State: 0
[0] 1 {0}
[!0] 2 {0}
State: 1
[!0] 1 {0}
[0] 2 {0}
State: 2
[t] 2
--END--
```

### Enriched monoid `EM(D)` → `S(L)₊`

`|EM¹| = 4` elements folding onto `|S(L)₊¹| = 4` classes. `rmul` is right-multiplication by each letter (`!a`, `a`), as `EM` element ids. The identity element hosts two classes (`[eps]` and any neutral non-empty class).

| id | word | st | mk | rmul | → class |
|---|---|---|---|---|---|
| 0 | `eps` | [0 1 2] | [{} {} {}] | 1 2 | 0 `eps` |
| 1 | `!a` | [2 1 2] | [{0} {0} {}] | 1 3 | 1 `!a` |
| 2 | `a` | [1 2 2] | [{0} {0} {}] | 2 3 | 2 `a` |
| 3 | `!a;a` | [2 2 2] | [{0} {0} {}] | 3 3 | 3 `!a;a` |

### Canonical algebra `S(L)₊¹`

| class | key (shortlex-least word) | idem |
|---|---|---|
| 0 | `eps` | ✓ |
| 1 | `!a` | ✓ |
| 2 | `a` |  |
| 3 | `!a;a` | ✓ |

*Letter map:* `!a` → 1, `a` → 2.

*Multiplication* (row `i` · col `j`):

```
·  0  1  2  3
0  0  1  2  3
1  1  1  3  3
2  2  2  3  3
3  3  3  3  3
```

*Accepting linked pairs* (1 of 8): `([a],[!a])`.

### Invariant `𝓘(L)` — `.sos` serialization

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
residuals: 3
0 eps
1 !a
2 a
res-step:
0: 1 2
1: 1 1
2: 2 1
```

