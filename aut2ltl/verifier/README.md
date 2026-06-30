# aut2ltl/verifier — the non-LTL witness checker

A `NOT_LTL` verdict from `aut2ltl` can carry a **witness**: a counting family
`(u, v, x, p)` claiming that membership of `u . v^n . x` in the language toggles with
`n mod p`. This package **replays** that family against the input automaton and reports
whether the claim holds — a standalone, acceptance-agnostic check that depends on
nothing but the `Witness` value type and Spot.

It is the independent verifier the witness docs name as a separate concern
(`bls/definability/witness/algorithm.md`): the engine *produces* the witness; this
package *checks* it.

## Two ways to use it

**API.** For any caller that wants to re-check or iterate witnesses:

```python
from aut2ltl.verifier import verify          # verify(aut, Witness) -> (ok, pattern)
ok, pattern = verify(spot.automaton("x.hoa"), witness)
```

**CLI.** Replay a serialized witness line (what the front end prints on stdout for a
NOT_LTL input):

```console
$ python3 -m aut2ltl.verifier samples/validation/hoa/mod3_a.hoa \
      "NOT_LTL p=3 u=[] v=[a; a] x=[cycle{!a}]"
VERIFY: ok pattern=1001001
```

stdout is one parseable marker; the exit code is the verdict: `0` ok (toggles with
period p), `1` fail (constant / wrong period — a bad certificate), `2` no-witness (the
family is incomplete, nothing to replay).

## What it checks — and the caveat

See [`algorithm.md`](algorithm.md). In short: it samples membership of `u . v^n . x`
for `n = 0..2p` via Spot (correct for any acceptance type), and accepts iff the pattern
is non-constant and repeats with period exactly `p`. This is the **suggestive tier**:
finitely many samples witness phase *distinguishability*, not *periodicity*, so `ok`
corroborates a witness without proving it — but `fail` is a genuine red flag that the
printed certificate does not check out.

## Modules

| module | concern |
|---|---|
| `check.py` | `member` (lasso membership), the sampler, `verify_suggestive`, `verify(aut, Witness)` |
| `__main__.py` | the CLI: detect HOA/LTL input, parse the witness line, replay, print the marker |
