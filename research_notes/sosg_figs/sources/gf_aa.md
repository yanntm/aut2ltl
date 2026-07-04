# SOSG algebra summary — GF(aa)

Canonical syntactic ω-semigroup `S(L)₊` read off each input automaton. `TM` = transition monoid; a group in `TM` may be a presentation artifact, a group in `S(L)₊` is intrinsic (⇔ not LTL-definable).

## Fingerprints

| input | \|Q\| | \|EM¹\| | \|S(L)₊¹\| | grp TM | grp S(L)₊ | LTL? | evidence |
|---|---|---|---|---|---|---|---|
| GF(aa) | 2 | 7 | 6 | no | no | yes | LTL — DG DAG 19 nodes / flat tree 1,991,717 (0.001s) |

## GF(aa)

*Input:* `G F (a & X a)`

### Deterministic form `D`

```hoa
HOA: v1
States: 2
Start: 0
AP: 1 "a"
acc-name: Buchi
Acceptance: 1 Inf(0)
properties: trans-labels explicit-labels trans-acc complete
properties: deterministic
--BODY--
State: 0
[0] 0 {0}
[!0] 1
State: 1
[0] 0
[!0] 1
--END--
```

### Enriched monoid `EM(D)` → `S(L)₊`

`|EM¹| = 7` elements folding onto `|S(L)₊¹| = 6` classes. `rmul` is right-multiplication by each letter (`!a`, `a`), as `EM` element ids.

| id | word | st | mk | rmul | → class |
|---|---|---|---|---|---|
| 0 | `eps` | [0 1] | [{} {}] | 1 2 | 0 `eps` |
| 1 | `!a` | [1 1] | [{} {}] | 1 3 | 1 `!a` |
| 2 | `a` | [0 0] | [{0} {}] | 4 5 | 2 `a` |
| 3 | `!a;a` | [0 0] | [{} {}] | 1 5 | 3 `!a;a` |
| 4 | `a;!a` | [1 1] | [{0} {}] | 4 2 | 4 `a;!a` |
| 5 | `a;a` | [0 0] | [{0} {0}] | 6 5 | 5 `a;a` |
| 6 | `a;a;!a` | [1 1] | [{0} {0}] | 6 5 | 5 `a;a` |

### Canonical algebra `S(L)₊¹`

| class | key (shortlex-least word) | idem |
|---|---|---|
| 0 | `eps` | ✓ |
| 1 | `!a` | ✓ |
| 2 | `a` |  |
| 3 | `!a;a` | ✓ |
| 4 | `a;!a` | ✓ |
| 5 | `a;a` | ✓ |

*Letter map:* `!a` → 1, `a` → 2.

*Multiplication* (row `i` · col `j`):

```
·  0  1  2  3  4  5
0  0  1  2  3  4  5
1  1  1  3  3  1  5
2  2  4  5  2  5  5
3  3  1  5  3  5  5
4  4  4  2  2  4  5
5  5  5  5  5  5  5
```

*Accepting linked pairs* (1 of 16): `([a;a],[a;a])`.

### Invariant `𝓘(L)` — `.sosg` serialization

```
SOSG v1
ap: a
classes: 6
0  eps
1  !a
2  a
3  !a;a
4  a;!a
5  a;a
letters: !a->1  a->2
mult:
     0 1 2 3 4 5
  0  0 1 2 3 4 5
  1  1 1 3 3 1 5
  2  2 4 5 2 5 5
  3  3 1 5 3 5 5
  4  4 4 2 2 4 5
  5  5 5 5 5 5 5
accept:
  5 5
residuals: 1
0  eps
res-mult:
     !a a
  0  0 0
```

