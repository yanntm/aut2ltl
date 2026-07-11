# M1 — theta-profile + exact measure: the flip gate

- date: 2026-07-11
- git: b5cc0062e
- corpus: /home/ythierry/git/BuchiToLTL/genaut/corpus/flat_canon (4248 .sos files)
- regeneration (from `sosl/`): `python3 -m tests.quant.flip_gate --list | while read f; do timeout 15 python3 -m tests.quant.flip_gate "$f" >/dev/null; done; python3 -m tests.quant.flip_gate --aggregate`

**Law.** `mu(L) + mu(~L) == 1` exactly (uniform p) and pointwise-negated theta-profiles, complement by the calculus flip, no reduce, all numbers `Fraction`.

| cases | green | red | missing |
|---|---|---|---|
| 4248 | 4248 | 0 | 0 |

| mu = 0 | 0 < mu < 1 | mu = 1 | median n | max n | median bottom SCCs | max |
|---|---|---|---|---|---|---|
| 1737 | 774 | 1737 | 15 | 121 | 1 | 7 |
