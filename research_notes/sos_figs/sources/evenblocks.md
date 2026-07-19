# SoS algebra summary — EvenBlocks

Canonical syntactic ω-semigroup `S(L)₊` read off each input automaton. `TM` = transition monoid; a group in `TM` may be a presentation artifact (the LTL-definability verdict, which turns on a group in `S(L)₊` itself, belongs to the definability engine, not this algebra summary).

## Fingerprints

| input | \|Q\| | \|EM¹\| | \|S(L)₊¹\| | grp TM |
|---|---|---|---|---|
| EvenBlocks | 2 | 16 | 8 | yes |

## EvenBlocks

*Input:* `../research_notes/sos_figs/sources/evenblocks.hoa`

### Deterministic form `D`

```hoa
HOA: v1
States: 2
Start: 0
AP: 1 "a"
acc-name: Rabin 1
Acceptance: 2 Fin(0) & Inf(1)
properties: trans-labels explicit-labels trans-acc complete
properties: deterministic
--BODY--
State: 0
[!0] 0 {1}
[0] 1
State: 1
[!0] 0 {0}
[0] 0
--END--
```

### Enriched monoid `EM(D)` → `S(L)₊`

`|EM¹| = 16` elements folding onto `|S(L)₊¹| = 8` classes. `rmul` is right-multiplication by each letter (`!a`, `a`), as `EM` element ids. The identity element hosts two classes (`[eps]` and any neutral non-empty class).

| id | word | st | mk | rmul | → class |
|---|---|---|---|---|---|
| 0 | `eps` | [0 1] | [{} {}] | 1 2 | 0 `eps` / 5 `a;a` |
| 1 | `!a` | [0 0] | [{1} {0}] | 3 4 | 1 `!a` |
| 2 | `a` | [1 0] | [{} {}] | 5 0 | 2 `a` |
| 3 | `!a;!a` | [0 0] | [{1} {0,1}] | 3 6 | 1 `!a` |
| 4 | `!a;a` | [1 1] | [{1} {0}] | 7 1 | 3 `!a;a` |
| 5 | `a;!a` | [0 0] | [{0} {1}] | 8 9 | 4 `a;!a` |
| 6 | `!a;!a;a` | [1 1] | [{1} {0,1}] | 10 3 | 3 `!a;a` |
| 7 | `!a;a;!a` | [0 0] | [{0,1} {0}] | 10 11 | 6 `!a;a;!a` |
| 8 | `a;!a;!a` | [0 0] | [{0,1} {1}] | 8 12 | 4 `a;!a` |
| 9 | `a;!a;a` | [1 1] | [{0} {1}] | 13 5 | 7 `a;!a;a` |
| 10 | `!a;!a;a;!a` | [0 0] | [{0,1} {0,1}] | 10 14 | 6 `!a;a;!a` |
| 11 | `!a;a;!a;a` | [1 1] | [{0,1} {0}] | 7 7 | 6 `!a;a;!a` |
| 12 | `a;!a;!a;a` | [1 1] | [{0,1} {1}] | 10 8 | 7 `a;!a;a` |
| 13 | `a;!a;a;!a` | [0 0] | [{0} {0,1}] | 10 15 | 6 `!a;a;!a` |
| 14 | `!a;!a;a;!a;a` | [1 1] | [{0,1} {0,1}] | 10 10 | 6 `!a;a;!a` |
| 15 | `a;!a;a;!a;a` | [1 1] | [{0} {0,1}] | 13 13 | 6 `!a;a;!a` |

### Canonical algebra `S(L)₊¹`

| class | key (shortlex-least word) | idem |
|---|---|---|
| 0 | `eps` | ✓ |
| 1 | `!a` | ✓ |
| 2 | `a` |  |
| 3 | `!a;a` |  |
| 4 | `a;!a` |  |
| 5 | `a;a` | ✓ |
| 6 | `!a;a;!a` | ✓ |
| 7 | `a;!a;a` | ✓ |

*Letter map:* `!a` → 1, `a` → 2.

*Multiplication* (row `i` · col `j`):

```
·  0  1  2  3  4  5  6  7
0  0  1  2  3  4  5  6  7
1  1  1  3  3  6  1  6  6
2  2  4  5  7  1  2  6  3
3  3  6  1  6  1  3  6  3
4  4  4  7  7  6  4  6  6
5  5  1  2  3  4  5  6  7
6  6  6  6  6  6  6  6  6
7  7  6  4  6  4  7  6  7
```

*Accepting linked pairs* (6 of 14): `([!a],[!a])`, `([!a;a],[a;!a;a])`, `([a;!a],[!a])`, `([!a;a;!a],[!a])`, `([!a;a;!a],[a;!a;a])`, `([a;!a;a],[a;!a;a])`.

### Invariant `𝓘(L)` — `.sos` serialization

```
SOS v1
ap: a
classes: 8
0 eps
1 !a
2 a
3 !a;a
4 a;!a
5 a;a
6 !a;a;!a
7 a;!a;a
letters: !a->1 a->2
mult:
0: 0 1 2 3 4 5 6 7
1: 1 1 3 3 6 1 6 6
2: 2 4 5 7 1 2 6 3
3: 3 6 1 6 1 3 6 3
4: 4 4 7 7 6 4 6 6
5: 5 1 2 3 4 5 6 7
6: 6 6 6 6 6 6 6 6
7: 7 6 4 6 4 7 6 7
accept:
1 1
3 7
4 1
6 1
6 7
7 7
residuals: 1
0 eps
res-step:
0: 0 0
```

