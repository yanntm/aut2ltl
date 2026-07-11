### gf_aa_parity / default — split ledger
final classes: 6 (initial stabilized: 3)

| # | trigger | chain | n | split | column |
|--:|---|---|---|---|---|
| 1 | cex (eps, !a;a;a) | loop | 3->4 | !a -> !a, !a;a | !a·([]·a)^ω |
| 2 | saturation | frozen | 4->5 | !a;a -> !a;a, a;!a | !a·([]·!a;a)^ω |
| 3 | saturation | branch1 | 5->6 | a -> a, a;a | !a·([]·!a)^ω |

| phase | fill | harvest | saturation | P-cache | total |
|---|--:|--:|--:|--:|--:|
| member | 51 | 4 | 9 | 10 | 74 |

equiv 2 · sat escalations 2 · columns lin/om 0/4

### gf_aa_parity / default — signature matrix

| key | c0 | c1 | c2 | c3 |
|---|---|---|---|---|
| `eps` | 0 | 1 | 0 | 0 |
| `!a` | 0 | 0 | 0 | 0 |
| `a` | 1 | 1 | 1 | 0 |
| `!a;a` | 0 | 1 | 0 | 0 |
| `a;!a` | 0 | 1 | 1 | 0 |
| `a;a` | 1 | 1 | 1 | 1 |

Columns (context each drops `[]` into):
- `c0` = eps·([]·eps)^ω
- `c1` = !a·([]·a)^ω
- `c2` = !a·([]·!a;a)^ω
- `c3` = !a·([]·!a)^ω

### gf_aa_reset / default — split ledger
final classes: 6 (initial stabilized: 3)

| # | trigger | chain | n | split | column |
|--:|---|---|---|---|---|
| 1 | cex (eps, !a;a;a) | loop | 3->4 | !a -> !a, !a;a | !a·([]·a)^ω |
| 2 | saturation | frozen | 4->5 | !a;a -> !a;a, a;!a | !a·([]·!a;a)^ω |
| 3 | saturation | branch1 | 5->6 | a -> a, a;a | !a·([]·!a)^ω |

| phase | fill | harvest | saturation | P-cache | total |
|---|--:|--:|--:|--:|--:|
| member | 51 | 4 | 9 | 10 | 74 |

equiv 2 · sat escalations 2 · columns lin/om 0/4

### gf_aa_reset / default — signature matrix

| key | c0 | c1 | c2 | c3 |
|---|---|---|---|---|
| `eps` | 0 | 1 | 0 | 0 |
| `!a` | 0 | 0 | 0 | 0 |
| `a` | 1 | 1 | 1 | 0 |
| `!a;a` | 0 | 1 | 0 | 0 |
| `a;!a` | 0 | 1 | 1 | 0 |
| `a;a` | 1 | 1 | 1 | 1 |

Columns (context each drops `[]` into):
- `c0` = eps·([]·eps)^ω
- `c1` = !a·([]·a)^ω
- `c2` = !a·([]·!a;a)^ω
- `c3` = !a·([]·!a)^ω

### even / default — split ledger
final classes: 5 (initial stabilized: 3)

| # | trigger | chain | n | split | column |
|--:|---|---|---|---|---|
| 1 | cex (eps, a;a;!a) | stem | 3->4 | a -> a, a;a | eps·[]·!a , (a;a;!a)^ω |
| 2 | saturation | frozen | 4->5 | a -> a, a;!a | eps·[]·a;!a , (a;a;!a)^ω |

| phase | fill | harvest | saturation | P-cache | total |
|---|--:|--:|--:|--:|--:|
| member | 32 | 4 | 7 | 8 | 51 |

equiv 2 · sat escalations 1 · columns lin/om 2/1

### even / default — signature matrix

| key | c0 | c1 | c2 |
|---|---|---|---|
| `eps` | 0 | 1 | 0 |
| `!a` | 1 | 1 | 1 |
| `a` | 0 | 0 | 1 |
| `a;!a` | 0 | 0 | 0 |
| `a;a` | 0 | 1 | 0 |

Columns (context each drops `[]` into):
- `c0` = eps·([]·eps)^ω
- `c1` = eps·[]·!a , (a;a;!a)^ω
- `c2` = eps·[]·a;!a , (a;a;!a)^ω

### evenblocks / default — split ledger
final classes: 8 (initial stabilized: 3)

| # | trigger | chain | n | split | column |
|--:|---|---|---|---|---|
| 1 | cex (eps, !a;a;a) | loop | 3->4 | a -> a, !a;a | a·([]·a)^ω |
| 2 | saturation | frozen | 4->6 | a -> a, a;a ; !a;a -> !a;a, a;!a | a·([]·!a;a)^ω |
| 3 | saturation | frozen | 6->8 | !a -> !a, a;!a;a ; a;a -> a;a, !a;a;!a | eps·([]·!a)^ω |

| phase | fill | harvest | saturation | P-cache | total |
|---|--:|--:|--:|--:|--:|
| member | 67 | 4 | 14 | 14 | 99 |

equiv 2 · sat escalations 2 · columns lin/om 0/4

### evenblocks / default — signature matrix

| key | c0 | c1 | c2 | c3 |
|---|---|---|---|---|
| `eps` | 0 | 0 | 0 | 1 |
| `!a` | 1 | 0 | 0 | 1 |
| `a` | 0 | 0 | 1 | 0 |
| `!a;a` | 0 | 1 | 0 | 0 |
| `a;!a` | 0 | 1 | 1 | 0 |
| `a;a` | 0 | 0 | 0 | 1 |
| `!a;a;!a` | 0 | 0 | 0 | 0 |
| `a;!a;a` | 1 | 0 | 0 | 0 |

Columns (context each drops `[]` into):
- `c0` = eps·([]·eps)^ω
- `c1` = a·([]·a)^ω
- `c2` = a·([]·!a;a)^ω
- `c3` = eps·([]·!a)^ω

### a_implies_xa / default — split ledger
final classes: 5 (initial stabilized: 4)

| # | trigger | chain | n | split | column |
|--:|---|---|---|---|---|
| 1 | saturation | branch1 | 4->5 | !a -> !a, a;a | a·([]·a)^ω |

| phase | fill | harvest | saturation | P-cache | total |
|---|--:|--:|--:|--:|--:|
| member | 32 | 0 | 2 | 9 | 43 |

equiv 1 · sat escalations 1 · columns lin/om 0/3

### a_implies_xa / default — signature matrix

| key | c0 | c1 | c2 |
|---|---|---|---|
| `eps` | 0 | 1 | 1 |
| `!a` | 1 | 1 | 0 |
| `a` | 1 | 0 | 1 |
| `a;!a` | 0 | 0 | 1 |
| `a;a` | 1 | 1 | 1 |

Columns (context each drops `[]` into):
- `c0` = eps·([]·eps)^ω
- `c1` = eps·([]·!a)^ω
- `c2` = a·([]·a)^ω

### a_once / default — split ledger
final classes: 4 (initial stabilized: 2)

| # | trigger | chain | n | split | column |
|--:|---|---|---|---|---|
| 1 | cex (a, !a) | stem | 2->3 | !a -> !a, a | eps·[]·!a , (!a)^ω |
| 2 | saturation | branch1 | 3->4 | !a -> !a, !a;a | a·[]·!a , (!a)^ω |

| phase | fill | harvest | saturation | P-cache | total |
|---|--:|--:|--:|--:|--:|
| member | 26 | 3 | 2 | 4 | 35 |

equiv 2 · sat escalations 1 · columns lin/om 2/1

### a_once / default — signature matrix

| key | c0 | c1 | c2 |
|---|---|---|---|
| `eps` | 0 | 0 | 1 |
| `!a` | 0 | 0 | 1 |
| `a` | 0 | 1 | 0 |
| `!a;a` | 0 | 0 | 0 |

Columns (context each drops `[]` into):
- `c0` = eps·([]·eps)^ω
- `c1` = eps·[]·!a , (!a)^ω
- `c2` = a·[]·!a , (!a)^ω
