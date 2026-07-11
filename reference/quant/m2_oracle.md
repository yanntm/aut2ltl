# M2 — law L1: measure vs the Route A oracle

- date: 2026-07-11
- git: 0001e9526
- corpus: /home/ythierry/git/BuchiToLTL/genaut/corpus/flat_canon (4248 .sos files, det/ mates by basename)
- regeneration (from `sosl/`): `python3 -m tests.quant.oracle_gate --list | while read f; do timeout 15 python3 -m tests.quant.oracle_gate "$f" >/dev/null; done; python3 -m tests.quant.oracle_gate --aggregate`

**Law.** `measure(I(X)).value == route_a(det/X.hoa).value` exactly, under uniform p and the skewed `p(a) = (1+a)/sum(1+m)`; the oracle is the classical BSCC analysis on the paired deterministic complete EL automaton, Spot for parsing only, `Fraction` throughout.

| cases | green | red | skip | missing | median ms | max ms |
|---|---|---|---|---|---|---|
| 4248 | 4248 | 0 | 0 | 0 | 2 | 195 |
