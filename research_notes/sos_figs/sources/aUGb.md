# SoS algebra summary — aUGb

Canonical syntactic ω-semigroup `S(L)₊` read off each input automaton. `TM` = transition monoid; a group in `TM` may be a presentation artifact (the LTL-definability verdict, which turns on a group in `S(L)₊` itself, belongs to the definability engine, not this algebra summary).

## Fingerprints

| input | \|Q\| | \|EM¹\| | \|S(L)₊¹\| | grp TM |
|---|---|---|---|---|
| aUGb | 3 | 10 | 5 | no |

## aUGb

*Input:* `../research_notes/sos_figs/sources/aUGb.hoa`

### Deterministic form `D`

```hoa
HOA: v1
States: 3
Start: 1
AP: 1 "a"
acc-name: Buchi
Acceptance: 1 Inf(0)
properties: trans-labels explicit-labels trans-acc complete
properties: deterministic stutter-invariant very-weak
--BODY--
State: 0
[!0] 0 {0}
[0] 2
State: 1
[!0] 0
[0] 1
State: 2
[t] 2
--END--
```

### Enriched monoid `EM(D)` → `S(L)₊`

`|EM¹| = 10` elements folding onto `|S(L)₊¹| = 5` classes. `rmul` is right-multiplication by each letter (`!a`, `a`), as `EM` element ids. The identity element hosts two classes (`[eps]` and any neutral non-empty class).

| id | word | st | mk | rmul | → class |
|---|---|---|---|---|---|
| 0 | `eps` | [0 1 2] | [{} {} {}] | 1 2 | 0 `eps` |
| 1 | `!a` | [0 0 2] | [{0} {} {}] | 3 4 | 1 `!a` |
| 2 | `a` | [2 1 2] | [{} {} {}] | 5 2 | 2 `a` |
| 3 | `!a;!a` | [0 0 2] | [{0} {0} {}] | 3 6 | 1 `!a` |
| 4 | `!a;a` | [2 2 2] | [{0} {} {}] | 4 4 | 3 `!a;a` |
| 5 | `a;!a` | [2 0 2] | [{} {} {}] | 7 8 | 4 `a;!a` |
| 6 | `!a;!a;a` | [2 2 2] | [{0} {0} {}] | 6 6 | 3 `!a;a` |
| 7 | `a;!a;!a` | [2 0 2] | [{} {0} {}] | 7 9 | 4 `a;!a` |
| 8 | `a;!a;a` | [2 2 2] | [{} {} {}] | 8 8 | 3 `!a;a` |
| 9 | `a;!a;!a;a` | [2 2 2] | [{} {0} {}] | 9 9 | 3 `!a;a` |

### Canonical algebra `S(L)₊¹`

| class | key (shortlex-least word) | idem |
|---|---|---|
| 0 | `eps` | ✓ |
| 1 | `!a` | ✓ |
| 2 | `a` | ✓ |
| 3 | `!a;a` | ✓ |
| 4 | `a;!a` |  |

*Letter map:* `!a` → 1, `a` → 2.

*Multiplication* (row `i` · col `j`):

```
·  0  1  2  3  4
0  0  1  2  3  4
1  1  1  3  3  3
2  2  4  2  3  4
3  3  3  3  3  3
4  4  4  3  3  3
```

*Accepting linked pairs* (2 of 6): `([!a],[!a])`, `([a;!a],[!a])`.

### Invariant `𝓘(L)` — `.sos` serialization

```
SOS v1
ap: a
classes: 5
0 eps
1 !a
2 a
3 !a;a
4 a;!a
letters: !a->1 a->2
mult:
0: 0 1 2 3 4
1: 1 1 3 3 3
2: 2 4 2 3 4
3: 3 3 3 3 3
4: 4 4 3 3 3
accept:
1 1
4 1
residuals: 3
0 eps
1 !a
2 !a;a
res-step:
0: 1 0
1: 1 2
2: 2 2
```

